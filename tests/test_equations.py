"""Tests for the equation count, which has to agree with MathJax's own numbering."""

import unittest
from pathlib import Path

import build

# Display equations and the numbers MathJax 3.2.2 gives them under ``tags: "all"``:
# "#" stands for the next number in the count, anything else for a manual ``\tag``.
NUMBERED_FORMS = [
    (r"x", ["#"]),
    (r"x \notag", []),
    (r"x \nonumber", []),
    (r"x \tag{A}", ["A"]),
    (r"x \tag*{A}", ["A"]),
    (r"x \tag{$a_{1}$}", ["$a_{1}$"]),
    (r"a \\ b", ["#"]),
    ("x % \\notag\n", ["#"]),
    (r"x = 5\% \notag", []),
    (r"\begin{equation} x \end{equation}", ["#"]),
    (r"\begin{equation} x \notag \end{equation}", []),
    (r"\begin{equation} a \\ b \end{equation}", ["#"]),
    (r"\begin{equation} x \end{equation} \notag", ["#"]),
    (r"\notag \begin{equation} x \end{equation}", ["#"]),
    (r"\begin{equation*} x \end{equation*}", []),
    (r"\begin{equation*} x \tag{A} \end{equation*}", ["A"]),
    (r"\begin{multline} a \\ b \end{multline}", ["#"]),
    (r"\begin{multline} a \notag \\ b \end{multline}", []),
    (r"\begin{multline*} a \\ b \end{multline*}", []),
    (r"\begin{align} a \\ b \end{align}", ["#", "#"]),
    (r"\begin{align} a \notag \\ b \end{align}", ["#"]),
    (r"\begin{align} a \notag \\ b \notag \end{align}", []),
    (r"\begin{align} a \tag{A} \\ b \end{align}", ["A", "#"]),
    (r"\begin{align} a \\ \\ b \end{align}", ["#", "#", "#"]),
    (r"\begin{align} a \\[2pt] b \\* c \end{align}", ["#", "#", "#"]),
    (r"\begin{align} a \cr b \newline c \end{align}", ["#", "#", "#"]),
    ("\\begin{align} a \\\\ b \\\\\n\\end{align}", ["#", "#"]),
    ("\\begin{align} a \\\\[2pt]\n\\end{align}", ["#"]),
    ("\\begin{align} a \\\\*\n\\end{align}", ["#"]),
    ("\\begin{align} a \\\\ % note\n\\end{align}", ["#"]),
    ("\\begin{align} a \\\\% note\n b \\end{align}", ["#", "#"]),
    ("\\begin{align} a % \\\\ b\n\\end{align}", ["#"]),
    ("\\begin{align} a \\\\ \\notag\n\\end{align}", ["#"]),
    ("\\begin{align} a \\\\ \\label{x}\n\\end{align}", ["#"]),
    ("\\begin{align} a \\\\ \\tag{A}\n\\end{align}", ["#"]),
    (r"\begin{align} a \end{align} \notag", ["#"]),
    (r"\begin{align} \sum_{\substack{a \\ b}} \\ c \end{align}", ["#", "#"]),
    (r"\begin{align} {a \\ b} \\ c \end{align}", ["#", "#"]),
    (r"\begin{align} \{ a \\ b \} \end{align}", ["#", "#"]),
    (r"\begin{align} a = \begin{cases} 1 \\ 2 \end{cases} \\ b \end{align}", ["#", "#"]),
    (r"\begin{align} a = \begin{cases} 1 \notag \\ 2 \end{cases} \\ b \end{align}", ["#"]),
    (r"\begin{align} \begin{aligned} a \\ b \end{aligned} \\ c \end{align}", ["#", "#"]),
    (r"\begin{align} \begin{aligned} a \notag \end{aligned} \\ c \end{align}", ["#", "#"]),
    (r"\begin{align} \begin{array}{c} a \\ b \end{array} \\ c \end{align}", ["#", "#"]),
    (r"\begin {align} a \\ b \end {align}", ["#", "#"]),
    (r"y = \begin{align} a \\ b \end{align}", ["#", "#"]),
    (r"\begin{align*} a \\ b \end{align*}", []),
    (r"\begin{align*} a \tag{A} \\ b \tag{B} \end{align*}", ["A", "B"]),
    (r"\begin{gather} a \\ b \end{gather}", ["#", "#"]),
    (r"\begin{gather*} a \\ b \end{gather*}", []),
    (r"\begin{alignat}{2} a &= b \\ c &= d \end{alignat}", ["#", "#"]),
    (r"\begin{alignat*}{2} a &= b \\ c &= d \end{alignat*}", []),
    (r"\begin{eqnarray} a \\ b \end{eqnarray}", ["#", "#"]),
    (r"\begin{eqnarray*} a \\ b \end{eqnarray*}", []),
    (r"\begin{flalign} a \\ b \end{flalign}", ["#", "#"]),
    (r"\begin{flalign*} a \\ b \end{flalign*}", ["#"]),
    (r"\begin{flalign*} a \notag \\ b \end{flalign*}", ["#"]),
    (r"\begin{xalignat}{1} a & b \\ c & d \end{xalignat}", ["#", "#"]),
    (r"\begin{xalignat*}{1} a & b \\ c & d \end{xalignat*}", ["#"]),
    (r"\begin{xxalignat}{1} a & b \\ c & d \end{xxalignat}", ["#"]),
    (r"\begin{equation}\begin{split} a \\ b \end{split}\end{equation}", ["#"]),
    (r"\begin{split} a \\ b \end{split}", ["#"]),
    (r"\begin{aligned} a \\ b \end{aligned}", ["#"]),
    (r"\begin{aligned} a \notag \\ b \end{aligned}", ["#"]),
    (r"\begin{aligned} a \\ b \end{aligned} \notag", []),
    (r"\notag \begin{aligned} a \\ b \end{aligned}", []),
    (r"\begin{gathered} a \\ b \end{gathered}", ["#"]),
    (r"\begin{alignedat}{1} a \\ b \end{alignedat}", ["#"]),
    (r"\begin{cases} a \\ b \end{cases}", ["#"]),
    (r"\begin{cases} a \\ b \end{cases} \nonumber", []),
    (r"\begin{array}{c} a \\ b \end{array}", ["#"]),
    (r"\begin{pmatrix} a \\ b \end{pmatrix}", ["#"]),
]

# Where a ``\label`` takes effect, as (equation, labels that get a number).
LABEL_FORMS = [
    (r"x \label{a}", ["a"]),
    (r"x \label {a}", ["a"]),
    (r"x \notag \label{a}", []),
    (r"x \tag{A} \label{a}", ["a"]),
    (r"\begin{align} a \label{a} \\ b \label{b} \end{align}", ["a", "b"]),
    (r"\begin{align} a \label{a} \notag \\ b \label{b} \end{align}", ["b"]),
    (r"\label{a} \begin{align} a \\ b \end{align}", []),
    (r"\label{a} \begin{equation} x \end{equation}", []),
    (r"\begin{equation}\begin{split} a \label{a} \\ b \end{split}\end{equation}", []),
    (r"\begin{equation}\begin{split} a \\ b \end{split}\label{a}\end{equation}", ["a"]),
    (r"\begin{aligned} a \label{a} \\ b \end{aligned}", []),
    (r"\begin{aligned} a \\ b \end{aligned} \label{a}", ["a"]),
    (r"\label{a} \begin{aligned} a \\ b \end{aligned}", ["a"]),
    (r"\begin{cases} a \label{a} \\ b \end{cases}", ["a"]),
    (r"\begin{align} \begin{aligned} a \label{a} \end{aligned} \\ c \end{align}", []),
    (r"\begin{align} \begin{aligned} a \end{aligned} \label{a} \\ c \end{align}", ["a"]),
    (r"\begin{align} \begin{cases} a \label{a} \\ b \end{cases} \\ c \end{align}", ["a"]),
    (r"\begin{align*} a \label{a} \\ b \tag{B} \end{align*}", []),
    (r"\begin{align*} a \tag{A} \label{a} \\ b \tag{B} \label{b} \end{align*}", ["a", "b"]),
    (r"\begin{equation*} x \tag{A} \label{a} \end{equation*}", ["a"]),
]


def display(tex: str) -> str:
    """Wrap TeX as the Markdown step emits a display equation."""
    return f'<div class="arithmatex">\\[{tex}\\]</div>\n'


def inline(tex: str) -> str:
    """Wrap TeX as the Markdown step emits inline math."""
    return f'<span class="arithmatex">\\({tex}\\)</span>'


def make_page(name: str, body_html: str, **fields) -> build.Page:
    fields.setdefault("kind", "chapter")
    fields.setdefault("number", "1")
    return build.Page(
        source=Path(f"{name}.md"), url=f"{name}/", meta={}, body_md="", body_html=body_html, **fields
    )


def make_section(chapter: build.Page, name: str, body_html: str, number: str) -> build.Page:
    return make_page(
        name, body_html, kind="section", number=number, chapter=chapter, counters=chapter.counters
    )


class EquationRowsTest(unittest.TestCase):
    def test_numbers_follow_mathjax(self):
        for tex, expected in NUMBERED_FORMS:
            with self.subTest(tex=tex):
                rows = build.equation_rows(tex)
                numbers = ["#" if row.counted else row.tag for row in rows]
                self.assertEqual([number for number in numbers if number], expected)

    def test_labels_follow_mathjax(self):
        for tex, expected in LABEL_FORMS:
            with self.subTest(tex=tex):
                rows = build.equation_rows(tex)
                labels = [row.label for row in rows if row.label and (row.counted or row.tag)]
                self.assertEqual(labels, expected)


class NumberEquationsTest(unittest.TestCase):
    def test_count_runs_through_section_pages(self):
        chapter = make_page("opener", display(r"x \label{a}"), number="2")
        rows = display(r"\begin{align} a \\ b \label{b} \end{align}")
        first = make_section(chapter, "first", rows, "2.1")
        second = make_section(chapter, "second", display(r"x \notag") + display(r"y \label{c}"), "2.2")
        labels = {}
        for page in (chapter, first, second):
            build.number_equations(page, labels)
        self.assertEqual([p.equation_offset for p in (chapter, first, second)], [0, 1, 3])
        self.assertEqual(labels, {"a": (chapter, "2.1"), "b": (first, "2.3"), "c": (second, "2.4")})

    def test_each_chapter_counts_from_one(self):
        one = make_page("one", display("x"))
        two = make_page("two", display(r"y \label{a}"), number="2")
        labels = {}
        build.number_equations(one, labels)
        build.number_equations(two, labels)
        self.assertEqual(two.equation_offset, 0)
        self.assertEqual(labels["a"], (two, "2.1"))

    def test_page_outside_a_chapter_has_no_prefix(self):
        page = make_page("home", display(r"x \label{a}"), kind="home", number="")
        labels = {}
        build.number_equations(page, labels)
        self.assertEqual(labels["a"], (page, "1"))

    def test_manual_tag_keeps_its_text_and_skips_the_count(self):
        page = make_page("page", display(r"x \tag{A} \label{a}") + display(r"y \label{b}"))
        labels = {}
        build.number_equations(page, labels)
        self.assertEqual(labels, {"a": (page, "A"), "b": (page, "1.1")})

    def test_escaped_tex_is_read_as_written(self):
        page = make_page("page", display(r"\begin{align} a &amp;&lt; b \\ c &amp;= d \end{align}"))
        build.number_equations(page, {})
        self.assertEqual(page.counters["equation"], 2)

    def test_repeated_label_fails(self):
        labels = {}
        build.number_equations(make_page("one", display(r"x \label{a}")), labels)
        with self.assertRaisesRegex(build.BuildError, r"two\.md: equation label a .* one\.md"):
            build.number_equations(make_page("two", display(r"y \label{a}")), labels)


class ResolveEquationRefsTest(unittest.TestCase):
    def setUp(self):
        self.chapter = make_page("book/chapter", display(r"x \label{eq:a}"))
        self.other = make_page("book/other", "", number="2")
        self.labels = {"eq:a": (self.chapter, "1.1"), "eq b": (self.other, "2.3")}

    def resolved(self, page: build.Page) -> str:
        build.resolve_equation_refs(page, self.labels)
        return page.body_html

    def test_reference_on_the_same_page_stays_with_mathjax(self):
        body = self.chapter.body_html + inline(r"\eqref{eq:a}")
        self.chapter.body_html = body
        self.assertEqual(self.resolved(self.chapter), body)

    def test_reference_to_another_page_becomes_a_link(self):
        self.other.body_html = inline(r"\eqref{eq:a}")
        self.assertEqual(
            self.resolved(self.other),
            inline(r"\href{../../book/chapter/#mjx-eqn:eq:a}{\text{(1.1)}}"),
        )

    def test_plain_ref_prints_no_parentheses(self):
        self.other.body_html = inline(r"\ref{eq:a}")
        self.assertIn(r"{\text{1.1}}", self.resolved(self.other))

    def test_reference_inside_a_display_equation(self):
        self.other.body_html = display(r"x = \eqref{eq:a}")
        self.assertIn(r"\href{../../book/chapter/#mjx-eqn:eq:a}", self.resolved(self.other))

    def test_spaces_in_a_label_become_underscores_in_the_anchor(self):
        self.chapter.body_html = inline(r"\eqref{eq b}")
        self.assertIn("#mjx-eqn:eq_b}", self.resolved(self.chapter))

    def test_code_is_left_alone(self):
        body = r"<p><code>\eqref{eq:missing}</code></p>"
        self.chapter.body_html = body
        self.assertEqual(self.resolved(self.chapter), body)

    def test_unknown_label_fails(self):
        self.chapter.body_html = inline(r"\eqref{eq:missing}")
        with self.assertRaisesRegex(build.BuildError, r"\\eqref\{eq:missing\} matches no"):
            self.resolved(self.chapter)


if __name__ == "__main__":
    unittest.main()
