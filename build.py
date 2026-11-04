#!/usr/bin/env python3
"""Build the guidebook: Markdown chapters in ``book/`` become a static site in ``site/``.

The book is described by ``book.yaml`` (parts and the chapters they contain). A
chapter is a Markdown file with a YAML front matter block, or a directory holding an
opener and one such file per section. The build numbers parts, chapters, sections,
figures, tables and boxed environments, counts equations so that MathJax can carry
their numbers from page to page, resolves citations against each page's reference
list, rewrites ``.md`` links into site URLs, emits a search index, and fails on any
broken internal link, unknown citation or equation reference with no equation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent
BOOK_DIR = ROOT / "book"
THEME_DIR = ROOT / "theme"
SITE_DIR = ROOT / "site"
CONFIG = ROOT / "book.yaml"

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

# Boxed environments that receive a running number within the chapter.
NUMBERED_BOXES = {
    "definition": "Definition",
    "example": "Example",
    "remark": "Remark",
    "recipe": "Recipe",
}

# Boxed environments that carry a kind label but no running number.
LABELLED_BOXES = {"warning": "Warning", "caution": "Caution", "note": "Note", "tip": "Tip"}

# How MathJax numbers a display equation under ``tags: "all"``. These environments own
# the display's numbers: the first set has one per row, the second one in all, and a
# starred name means none unless a row carries ``\tag``. The third set takes no number
# of its own and discards any ``\label``, ``\tag`` or ``\notag`` written inside it. Any
# other display takes one number. These follow the MathJax version loaded in base.html,
# so an upgrade must recheck them.
# https://github.com/mathjax/MathJax-src/blob/3.2.2/ts/input/tex/ams/AmsMappings.ts#L102
# https://github.com/mathjax/MathJax-src/blob/3.2.2/ts/input/tex/base/BaseMappings.ts#L703
# https://github.com/mathjax/MathJax-src/blob/3.2.2/ts/input/tex/base/BaseItems.ts#L1105
# https://github.com/mathjax/MathJax-src/blob/3.2.2/ts/input/tex/Tags.ts#L572
ROW_ENVIRONMENTS = {
    "align",
    "align*",
    "alignat",
    "alignat*",
    "eqnarray",
    "eqnarray*",
    "flalign",
    "gather",
    "gather*",
    "xalignat",
}
ONE_ROW_ENVIRONMENTS = {"equation", "equation*", "multline", "multline*"}
INNER_ENVIRONMENTS = {
    "aligned",
    "alignedat",
    "flalign*",
    "gathered",
    "split",
    "xalignat*",
    "xxalignat",
}

MARKDOWN_EXTENSIONS = [
    "abbr",
    "admonition",
    "attr_list",
    "def_list",
    "footnotes",
    "md_in_html",
    "smarty",
    "tables",
    "toc",
    "pymdownx.arithmatex",
    "pymdownx.betterem",
    "pymdownx.details",
    "pymdownx.highlight",
    "pymdownx.inlinehilite",
    "pymdownx.keys",
    "pymdownx.superfences",
]
MARKDOWN_EXTENSION_CONFIGS = {
    "toc": {"toc_depth": "2-3", "permalink": False},
    "footnotes": {"PLACE_MARKER": "<!-- footnotes -->", "BACKLINK_TITLE": "Back to text"},
    "pymdownx.arithmatex": {"generic": True},
    "pymdownx.highlight": {"css_class": "highlight", "guess_lang": False},
    "smarty": {"smart_angled_quotes": False},
}

PYGMENTS_LIGHT = "friendly"
PYGMENTS_DARK = "github-dark"


class BuildError(Exception):
    """A problem that must stop the build."""


# --------------------------------------------------------------------------- model


@dataclass
class Page:
    """One output page: the home page, a part opener, a chapter or a chapter's section."""

    kind: str  # "home" | "part" | "chapter" | "section"
    source: Path  # Markdown source, relative to BOOK_DIR
    url: str  # site-relative URL ending in "/" ("" for the home page)
    meta: dict
    body_md: str
    title: str = ""
    number: str = ""  # "1" for a chapter, "I" for a part, "1.3" for a section page
    part: Page | None = None
    chapter: Page | None = None  # the chapter a section page belongs to
    chapters: list[Page] = field(default_factory=list)
    section_pages: list[Page] = field(default_factory=list)
    sections: list[dict] = field(default_factory=list)  # headings within this page
    counters: dict[str, int] = field(default_factory=dict)  # shared across a chapter's pages
    equation_offset: int = 0  # equations numbered on the chapter's earlier pages
    body_html: str = ""
    prev: Page | None = None
    next: Page | None = None

    @property
    def status(self) -> str:
        return str(self.meta.get("status", "")).strip()

    @property
    def summary(self) -> str:
        return str(self.meta.get("summary", "")).strip()

    @property
    def chapter_number(self) -> str:
        """The number of the chapter this page is in, empty outside chapters."""
        if self.kind == "section":
            return self.chapter.number
        return self.number if self.kind == "chapter" else ""

    @property
    def has_numbered_headings(self) -> bool:
        """Whether H2/H3 are numbered; an opener with section pages leaves them plain."""
        return self.kind == "section" or (self.kind == "chapter" and not self.section_pages)

    @property
    def output_path(self) -> Path:
        return SITE_DIR / self.url / "index.html"

    @property
    def depth(self) -> int:
        return self.url.count("/")

    @property
    def root(self) -> str:
        return "../" * self.depth if self.depth else "./"

    def href(self, target: Page) -> str:
        return self.root + target.url


@dataclass
class EquationRow:
    """One row of a display equation that MathJax may number."""

    label: str = ""
    tag: str = ""  # the text of a manual ``\tag``
    counted: bool = True  # takes the next number in the running count


# --------------------------------------------------------------------- front matter

FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def split_front_matter(text: str, source: Path) -> tuple[dict, str]:
    match = FRONT_MATTER.match(text)
    if not match:
        raise BuildError(f"{source}: missing YAML front matter")
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as error:
        raise BuildError(f"{source}: invalid front matter: {error}") from None
    if not isinstance(meta, dict):
        raise BuildError(f"{source}: front matter must be a mapping")
    return meta, text[match.end():]


def read_page(kind: str, rel: Path, url: str) -> Page:
    path = BOOK_DIR / rel
    if not path.is_file():
        raise BuildError(f"book.yaml refers to a missing file: {rel}")
    meta, body = split_front_matter(path.read_text(encoding="utf-8"), rel)
    title = str(meta.get("title", "")).strip()
    if not title:
        raise BuildError(f"{rel}: front matter needs a title")
    return Page(kind=kind, source=rel, url=url, meta=meta, body_md=body, title=title)


def load_book() -> tuple[dict, list[Page]]:
    """Read ``book.yaml`` and return the config plus every page in reading order."""
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    pages: list[Page] = [read_page("home", Path("index.md"), "")]
    chapter_no = 0
    for index, part_cfg in enumerate(config.get("parts", [])):
        directory = part_cfg["dir"].strip("/")
        part = read_page("part", Path(directory) / "index.md", f"{directory}/")
        part.number = ROMAN[index]
        pages.append(part)
        for entry in part_cfg.get("chapters", []):
            chapter_no += 1
            if isinstance(entry, str):
                chapter_dir = PurePosixPath(entry).stem
                source, section_names = Path(directory) / entry, []
            else:
                chapter_dir = entry["dir"].strip("/")
                source = Path(directory) / chapter_dir / "index.md"
                section_names = entry.get("sections", [])
            chapter = read_page("chapter", source, f"{directory}/{chapter_dir}/")
            chapter.number = str(chapter_no)
            chapter.part = part
            part.chapters.append(chapter)
            pages.append(chapter)
            for section_no, name in enumerate(section_names, start=1):
                stem = PurePosixPath(name).stem
                section = read_page(
                    "section", Path(directory) / chapter_dir / name, f"{directory}/{chapter_dir}/{stem}/"
                )
                section.number = f"{chapter.number}.{section_no}"
                section.part = part
                section.chapter = chapter
                section.counters = chapter.counters
                chapter.section_pages.append(section)
                pages.append(section)
    for before, after in zip(pages, pages[1:]):
        before.next = after
        after.prev = before
    return config, pages


# ------------------------------------------------------------------- HTML passes

CODE_SEGMENT = re.compile(r"(<pre.*?</pre>|<code.*?</code>)", re.S)


def outside_code(text: str, transform) -> str:
    """Apply ``transform`` to the parts of ``text`` that are not code."""
    parts = CODE_SEGMENT.split(text)
    return "".join(part if i % 2 else transform(part) for i, part in enumerate(parts))


HEADING = re.compile(r'<h([23]) id="([^"]+)">(.*?)</h\1>', re.S)


def anchor_link(anchor: str) -> str:
    """A permalink that copies the shareable URL of the element when clicked."""
    return (
        f' <a class="anchor" href="#{anchor}" title="Copy link to this place"'
        f' aria-label="Copy link to this place">§</a>'
    )


def number_headings(page: Page) -> None:
    """Prefix H2/H3 with section numbers and collect the chapter's section list."""
    counters = [0, 0]
    sections: list[dict] = []

    def replace(match: re.Match) -> str:
        level, anchor, text = int(match.group(1)), match.group(2), match.group(3)
        plain = re.sub(r"<[^>]+>", "", text).strip()
        unnumbered = "unnumbered" in text or plain.strip().lower() in {"references", "further reading"}
        if level == 2:
            counters[1] = 0
            if not unnumbered:
                counters[0] += 1
        elif not unnumbered:
            counters[1] += 1
        if unnumbered or not page.has_numbered_headings:
            label = ""
        elif level == 2:
            label = f"{page.number}.{counters[0]}"
        else:
            label = f"{page.number}.{counters[0]}.{counters[1]}"
        sections.append({"level": level, "id": anchor, "title": plain, "number": label})
        prefix = f'<span class="secnum">{label}</span> ' if label else ""
        return f'<h{level} id="{anchor}">{prefix}{text}{anchor_link(anchor)}</h{level}>'

    page.body_html = HEADING.sub(replace, page.body_html)
    page.sections = sections


FIGURE = re.compile(r"<p>(<img [^>]*>)</p>")
TABLE_CAPTION = re.compile(r"(<table>.*?</table>)\s*(?:<p>Table:\s*(.*?)</p>)?", re.S)
IMG_ALT = re.compile(r'alt="([^"]*)"')


IMG_SRC = re.compile(r'src="([^"]+)"')
XML_DECLARATION = re.compile(r"<\?xml[^>]*\?>\s*")


def inline_svg(page: Page, img: str, caption: str) -> str | None:
    """Embed a local SVG figure so it can use the page's colour tokens."""
    src = IMG_SRC.search(img)
    if not src or not src.group(1).endswith(".svg") or "://" in src.group(1):
        return None
    path = BOOK_DIR / page.source.parent / src.group(1)
    if not path.is_file():
        raise BuildError(f"{page.source}: missing figure: {src.group(1)}")
    svg = XML_DECLARATION.sub("", path.read_text(encoding="utf-8")).strip()
    title = html.escape(caption, quote=True)
    return svg.replace("<svg", f'<svg class="inline-svg" role="img" aria-label="{title}"', 1)


def number_figures_and_tables(page: Page) -> None:
    label = f"{page.chapter_number}." if page.chapter_number else ""
    counters = page.counters

    def figure(match: re.Match) -> str:
        fig = counters["figure"] = counters.get("figure", 0) + 1
        img = match.group(1)
        alt = IMG_ALT.search(img)
        caption = alt.group(1) if alt else ""
        body = inline_svg(page, img, caption) or img
        return (
            f'<figure id="fig-{fig}">{body}<figcaption>'
            f'<span class="caplabel">Figure {label}{fig}</span> {caption}'
            f'{anchor_link(f"fig-{fig}")}</figcaption></figure>'
        )

    def table(match: re.Match) -> str:
        body, caption = match.group(1), match.group(2)
        if not caption:
            # Only captioned tables are numbered, so the numbers run without gaps.
            return f'<figure class="table"><div class="table-wrap">{body}</div></figure>'
        tab = counters["table"] = counters.get("table", 0) + 1
        cap = (
            f'<figcaption><span class="caplabel">Table {label}{tab}</span> {caption}'
            f'{anchor_link(f"tab-{tab}")}</figcaption>'
        )
        return f'<figure class="table" id="tab-{tab}">{cap}<div class="table-wrap">{body}</div></figure>'

    page.body_html = FIGURE.sub(figure, page.body_html)
    page.body_html = TABLE_CAPTION.sub(table, page.body_html)


BOX = re.compile(
    r'<div class="admonition ([\w-]+)( [\w -]+)?">\s*<p class="admonition-title">(.*?)</p>', re.S
)


def number_boxes(page: Page) -> None:
    counters = page.counters
    label = f"{page.chapter_number}." if page.chapter_number else ""

    def replace(match: re.Match) -> str:
        kind, extra, title = match.group(1), match.group(2) or "", match.group(3)
        name = NUMBERED_BOXES.get(kind)
        if name is None:
            plain = LABELLED_BOXES.get(kind)
            if plain is None:
                return match.group(0)
            head = f'<span class="boxlabel">{plain}</span>'
            if title and title.lower() != plain.lower():
                head += f' <span class="boxtitle">{title}</span>'
            return f'<div class="admonition {kind}{extra}">\n<p class="admonition-title">{head}</p>'
        counters[kind] = counters.get(kind, 0) + 1
        box_id = f"{kind}-{label}{counters[kind]}".replace(".", "-")
        head = f'<span class="boxlabel">{name} {label}{counters[kind]}</span>'
        if title and title != kind.capitalize():
            head += f' <span class="boxtitle">{title}</span>'
        head += anchor_link(box_id)
        return (
            f'<div class="admonition {kind}{extra}" id="{box_id}">\n'
            f'<p class="admonition-title">{head}</p>'
        )

    page.body_html = BOX.sub(replace, page.body_html)


DISPLAY_MATH = re.compile(r'<div class="arithmatex">\\\[(.*?)\\\]</div>', re.S)
TEX_COMMENT = re.compile(r"((?<!\\)(?:\\\\)*)%.*")
TEX_TOKEN = re.compile(
    r"""
    \\begin\s*\{(?P<begin>[^}]*)\}
    | \\end\s*\{(?P<end>[^}]*)\}
    | \\label\s*\{(?P<label>[^}]*)\}
    | \\tag\*?\s*\{(?P<tag>(?:[^{}]|\{[^{}]*\})*)\}
    | (?P<notag>\\(?:notag|nonumber)\b)
    | (?P<row_end>\\\\\*?(?:\[[^\]]*\])?|\\(?:cr|newline)\b)
    | (?P<open>\{)
    | (?P<close>\})
    | \\.
    """,
    re.X | re.S,
)
ROW_MARKS = {"label", "tag", "notag"}


def is_empty_row(tex: str) -> bool:
    """Whether a row holds nothing but marks; MathJax drops such a row at a table's end."""
    return not TEX_TOKEN.sub(lambda t: "" if t.lastgroup in ROW_MARKS else t.group(), tex).strip()


def equation_rows(tex: str) -> list[EquationRow]:
    """Split a display equation into the rows MathJax can number, in page order."""
    tex = TEX_COMMENT.sub(r"\1", tex)
    rows: list[EquationRow] = []
    row = EquationRow()
    environments: list[str] = []
    braces = 0
    outer = ""  # the environment that owns the display's numbers
    row_start = 0

    for token in TEX_TOKEN.finditer(tex):
        kind = token.lastgroup
        in_outer = bool(outer) and len(environments) == 1 and not braces
        if kind == "begin":
            name = token["begin"]
            if not environments and name in ROW_ENVIRONMENTS | ONE_ROW_ENVIRONMENTS:
                outer = name
                row = EquationRow(counted=not name.endswith("*"))
                row_start = token.end()
            environments.append(name)
        elif kind == "end":
            if in_outer:
                if not is_empty_row(tex[row_start:token.start()]):
                    rows.append(row)
                row = EquationRow()
            del environments[-1:]
        elif kind == "row_end" and in_outer and outer in ROW_ENVIRONMENTS:
            rows.append(row)
            row = EquationRow(counted=not outer.endswith("*"))
            row_start = token.end()
        elif kind == "open":
            braces += 1
        elif kind == "close":
            braces -= 1
        elif kind in ROW_MARKS and INNER_ENVIRONMENTS.isdisjoint(environments):
            if kind == "label":
                row.label = token["label"]
            elif kind == "tag":
                row.tag = token["tag"]
                row.counted = False
            else:
                row.counted = False
    return rows if outer else [row]


def number_equations(page: Page, equation_labels: dict[str, tuple[Page, str]]) -> None:
    """Carry the chapter's equation count through this page and record its labels."""
    counters = page.counters
    prefix = f"{page.chapter_number}." if page.chapter_number else ""
    page.equation_offset = counters.get("equation", 0)
    for tex in DISPLAY_MATH.findall(page.body_html):
        for row in equation_rows(html.unescape(tex)):
            number = row.tag
            if row.counted:
                counters["equation"] = counters.get("equation", 0) + 1
                number = f"{prefix}{counters['equation']}"
            if not row.label or not number:
                continue
            if row.label in equation_labels:
                other = equation_labels[row.label][0].source
                raise BuildError(f"{page.source}: equation label {row.label} is also used in {other}")
            equation_labels[row.label] = (page, number)


MATH = re.compile(r'<(div|span) class="arithmatex">.*?</\1>', re.S)
EQUATION_REF = re.compile(r"\\(eqref|ref)\s*\{([^}]*)\}")


def resolve_equation_refs(page: Page, equation_labels: dict[str, tuple[Page, str]]) -> None:
    """Check every equation reference and turn those that leave the page into links."""

    def replace(match: re.Match) -> str:
        command, label = match.group(1), match.group(2)
        if label not in equation_labels:
            raise BuildError(f"{page.source}: \\{command}{{{label}}} matches no numbered equation")
        target, number = equation_labels[label]
        if target is page:
            return match.group(0)  # MathJax resolves references within a page
        text = f"({number})" if command == "eqref" else number
        anchor = "mjx-eqn:" + re.sub(r"\s", "_", label)
        return rf"\href{{{page.href(target)}#{anchor}}}{{\text{{{text}}}}}"

    page.body_html = MATH.sub(lambda m: EQUATION_REF.sub(replace, m.group(0)), page.body_html)


CITE = re.compile(r"\[@([^\]]+)\]")


def resolve_citations(page: Page, md: markdown.Markdown) -> list[str]:
    """Turn ``[@key]`` into numbered citations and append the reference list."""
    references = page.meta.get("references") or {}
    if not isinstance(references, dict):
        raise BuildError(f"{page.source}: 'references' must be a mapping of key to text")
    order: list[str] = []
    warnings: list[str] = []

    def number(key: str) -> int:
        if key not in references:
            raise BuildError(f"{page.source}: citation [@{key}] has no entry in 'references'")
        if key not in order:
            order.append(key)
        return order.index(key) + 1

    def replace(match: re.Match) -> str:
        keys = [k.strip().lstrip("@") for k in match.group(1).split(";") if k.strip()]
        links = [f'<a class="cite" href="#ref-{k}">{number(k)}</a>' for k in keys]
        return f'<span class="cites">[{", ".join(links)}]</span>'

    page.body_html = outside_code(page.body_html, lambda s: CITE.sub(replace, s))
    unused = [k for k in references if k not in order]
    if unused:
        warnings.append(f"{page.source}: references never cited: {', '.join(unused)}")
    if order:
        items = []
        for key in order:
            text = md.convert(str(references[key]))
            md.reset()
            text = re.sub(r"^<p>|</p>$", "", text.strip())
            items.append(f'<li id="ref-{key}">{text}</li>')
        page.body_html += (
            '\n<section class="references"><h2 id="references" class="unnumbered">References</h2>'
            f'<ol class="references">{"".join(items)}</ol></section>'
        )
    return warnings


LINK = re.compile(r'(href|src)="([^"#]*?\.(?:md|svg|png|jpe?g|gif|pdf|webp))(#[^"]*)?"')


def rewrite_links(page: Page, pages_by_source: dict[Path, Page], assets: set[Path]) -> None:
    """Rewrite ``.md`` links into site URLs and check that every target exists."""
    source_dir = page.source.parent

    def replace(match: re.Match) -> str:
        attr, target, fragment = match.group(1), match.group(2), match.group(3) or ""
        if "://" in target or target.startswith("/"):
            return match.group(0)
        resolved = Path(PurePosixPath(source_dir.as_posix()) / target)
        resolved = Path(*[p for p in PurePosixPath(resolved.as_posix()).parts])
        normalised = Path(PurePosixPath("/" + resolved.as_posix()).as_posix().lstrip("/"))
        # collapse ".." components
        parts: list[str] = []
        for part in normalised.parts:
            if part == "..":
                if not parts:
                    raise BuildError(f"{page.source}: link escapes the book: {target}")
                parts.pop()
            elif part != ".":
                parts.append(part)
        normalised = Path(*parts) if parts else Path()
        if target.endswith(".md"):
            dest = pages_by_source.get(normalised)
            if dest is None:
                raise BuildError(f"{page.source}: link to a page that is not in book.yaml: {target}")
            return f'{attr}="{page.href(dest)}{fragment}"'
        if not (BOOK_DIR / normalised).is_file():
            raise BuildError(f"{page.source}: missing asset: {target}")
        assets.add(normalised)
        return f'{attr}="{page.root}{normalised.as_posix()}{fragment}"'

    page.body_html = LINK.sub(replace, page.body_html)


def mark_external_links(page: Page) -> None:
    page.body_html = re.sub(
        r'<a href="(https?://[^"]+)"',
        r'<a href="\1" class="external" rel="noopener"',
        page.body_html,
    )


# ------------------------------------------------------------------------- search

TAG = re.compile(r"<[^>]+>")


def search_entries(page: Page) -> list[dict]:
    """One entry per H2 section, with plain text for the client-side index."""
    chunks = re.split(r'(?=<h2 id=")', page.body_html)
    entries = []
    for chunk in chunks:
        heading = re.match(r'<h2 id="([^"]+)">(.*?)</h2>', chunk, re.S)
        text = html.unescape(TAG.sub(" ", chunk)).replace("§", "")
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        if heading:
            section = html.unescape(TAG.sub("", heading.group(2))).replace("§", "").strip()
            anchor = "#" + heading.group(1)
            text = text[len(section):].strip() if text.startswith(section) else text
        else:
            section, anchor = "", ""
        prefix = {"chapter": f"{page.number}. ", "section": f"{page.number} "}.get(page.kind, "")
        entries.append(
            {
                "url": page.url + anchor,
                "page": prefix + page.title,
                "section": section,
                "text": text[:1200],
            }
        )
    return entries


# -------------------------------------------------------------------------- build


def make_markdown() -> markdown.Markdown:
    return markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS, extension_configs=MARKDOWN_EXTENSION_CONFIGS
    )


def pygments_css() -> str:
    light = HtmlFormatter(style=PYGMENTS_LIGHT).get_style_defs(".highlight")
    dark = HtmlFormatter(style=PYGMENTS_DARK)
    dark_css = dark.get_style_defs('[data-theme="dark"] .highlight')
    return f"{light}\n{dark_css}\n"


def render_pages(config: dict, pages: list[Page]) -> list[dict]:
    md = make_markdown()
    pages_by_source = {p.source: p for p in pages}
    assets: set[Path] = set()
    equation_labels: dict[str, tuple[Page, str]] = {}
    index: list[dict] = []
    warnings: list[str] = []

    env = Environment(
        loader=FileSystemLoader(THEME_DIR / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    build_date = dt.date.today()
    env.globals.update(book=config, build_date=build_date.strftime("%B %Y"), pages=pages)

    for page in pages:
        page.body_html = md.convert(page.body_md)
        md.reset()
        number_headings(page)
        number_figures_and_tables(page)
        number_boxes(page)
        number_equations(page, equation_labels)
        warnings += resolve_citations(page, md)
        rewrite_links(page, pages_by_source, assets)
        mark_external_links(page)
        index += search_entries(page)

    # A reference can point forward, so this waits until every page is numbered.
    for page in pages:
        resolve_equation_refs(page, equation_labels)

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    parts = [p for p in pages if p.kind == "part"]
    for page in pages:
        template = env.get_template(f"{page.kind}.html")
        page.output_path.parent.mkdir(parents=True, exist_ok=True)
        page.output_path.write_text(template.render(page=page, parts=parts), encoding="utf-8")

    for rel in sorted(assets):
        dest = SITE_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BOOK_DIR / rel, dest)

    static_out = SITE_DIR / "static"
    shutil.copytree(THEME_DIR / "static", static_out)
    (static_out / "pygments.css").write_text(pygments_css(), encoding="utf-8")
    (SITE_DIR / "search.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")
    return warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--allow-warnings",
        action="store_true",
        help="do not fail the build on warnings (uncited references)",
    )
    args = parser.parse_args(argv)
    try:
        config, pages = load_book()
        warnings = render_pages(config, pages)
    except BuildError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    chapters = sum(1 for p in pages if p.kind == "chapter")
    print(f"built {len(pages)} pages ({chapters} chapters) into {SITE_DIR.relative_to(ROOT)}/")
    if warnings and not args.allow_warnings:
        print("error: warnings are fatal (pass --allow-warnings to override)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
