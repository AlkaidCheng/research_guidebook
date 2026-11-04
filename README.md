# Research Guidebook

A textbook-style reference to the methods, tools and conventions behind my
research projects, organised by field and topic and revised as the projects
move on.

**Read it at <https://alkaidcheng.github.io/research_guidebook/>.**

## Contents

- **Part I: High Energy Physics**: event generation, detector simulation and
  statistical inference.

## Building locally

The site is generated from Markdown by `build.py`, which needs Python 3.10 or
later and the packages in `requirements.txt`.

```bash
pip install -r requirements.txt
python3 build.py
python3 -m http.server --directory site 8000
```

Then open <http://127.0.0.1:8000/>. The build fails on a broken internal link,
a missing figure, a citation without a reference entry, a reference that is
never cited, an `\eqref` to a label no numbered equation carries, or an
equation label used twice.

## Writing a chapter

1. Write the chapter as Markdown in its part's directory under `book/`, with a
   YAML front matter block giving its `title`, a one-sentence `summary`, an
   optional `status` (for example `in-preparation`) and a `references` map of
   citation keys to formatted entries.
2. Add the file name to the part's `chapters` list in `book.yaml`. Chapters
   are numbered in that order, continuously through the book.
3. Use `##` for sections and `###` for subsections; the build numbers them.
   Display equations in `$$ … $$` are numbered within the chapter and can
   carry `\label{}`, which `\eqref{}` reaches from any page. An image becomes
   a numbered figure with its alt text as caption; a table followed by a
   paragraph starting with `Table:` becomes a numbered table.
4. Cite with `[@key]`; the reference list is generated at the end of the
   chapter in order of first citation.
5. Set material apart with `!!! definition`, `!!! example`, `!!! remark`,
   `!!! recipe`, `!!! warning` or `!!! summary` blocks. The first four are
   numbered within the chapter.

Every section, subsection, figure, table and numbered box has a permalink:
the `§` mark that appears beside it copies a URL that opens the book at that
place. Section anchors are derived from the heading text, so renaming a
heading changes its link. Figures and tables open enlarged when clicked.

A chapter can also span several pages. Make it a directory in the part, with
an `index.md` opener and one Markdown file per section, and list them in
`book.yaml`:

```yaml
chapters:
  - dir: statistical-inference
    sections:
      - likelihoods.md
      - hypothesis-tests.md
```

Each section page is numbered within the chapter (3.1, 3.2), its `##` headings
become subsections (3.1.1), and figures, tables, numbered boxes and equations
keep one running count through the chapter, so splitting a chapter changes none
of those numbers. An `\eqref` to an equation on another page prints its number
and links to it. Each page has its own `references` map and reference list.

A new part is a new directory with an `index.md` opener and an entry in
`book.yaml`.

Every pull request is built by CI, and each push to `main` is deployed to
GitHub Pages.

## License

[MIT](LICENSE)
