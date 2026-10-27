# Python for Data Analysts - Slides (course site)

The lectures of the course "Python for Data Analysts": 16 sessions of 4 academic
hours, for analysts who move from SQL and SAS to Python, pandas and NumPy.

Live site: https://ivapopova-courses.github.io/Python-Data-Analysts-UniCredit-Slides/

The site is built with [VitePress](https://vitepress.dev/) and
[course-kit](https://github.com/SciScend/course-kit): every lecture is one Markdown
page, with a sidebar, search, dark mode, and Python examples you can run and edit
on the page (Python runs in the browser with [Pyodide](https://pyodide.org/)).

The course has four repositories, cloned side by side in one course folder:

| Folder | Repository | What it is |
|---|---|---|
| `Slides/` | https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Slides | this repo - the lectures |
| `Homework/` | https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework | practice tasks and homework |
| `Labs/` | https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Labs | code written in class |
| `trainer/` | private | trainer notes and solutions |

## Run it

```bash
npm install          # once
npm run dev          # live preview at http://localhost:5173, reloads on save
npm run build        # static site in site/.vitepress/dist (for GitHub Pages)
```

## In class

- **Present** (button in the top bar, or key `P`): bigger text, no side panels -
  for the projector.
- **Notes** (button, key `T`, or `?trainer` in the URL): shows the yellow
  "Trainer notes" boxes, if a page has any. Only with `npm run dev:trainer`, which
  reads the notes from `../trainer` (`trainerDir` in `.vitepress/config.mjs`). The
  public build has none.
- **Run / Edit / Reset** under the examples: the code runs in the browser. The
  first Run of a page loads Pyodide from the CDN (needs internet).

## Layout

```text
site/                          the course site (VitePress)
    index.md                   home page: the 16 sessions
    agenda.md                  course agenda
    how-to.md, sample-data.md, project.md
    lectures/NN-topic.md       one page per lecture
    under-the-hood.md          the list of the animations
    public/animations/         step-by-step animations (anim.js + anim.css + one page each;
                               bg/*.html only redirect to ?lang=bg)
    public/diagrams/           SVG diagrams, English and bg/ - made by tools/make-diagrams.py
    .vitepress/config.mjs      sidebar, nav
    .vitepress/pythonRun.mjs   the "python run" code blocks (markdown)
    .vitepress/theme/          PyRunCode.vue + pyRunner.js (Run / Edit / Reset with Pyodide),
                               DataFile.vue + dataPreview.js (the preview of a data file),
                               LangSwitch.vue (the EN / BG button), codeFold, scrollHash
    bg/                        GENERATED Bulgarian pages (git-ignored, see i18n/)
i18n/                          translations: bg/*.po, the generator, translator guide, glossary
data/*.csv                     MADE-UP sample data (same files as in Homework/data/)
tools/make-diagrams.py         writes site/public/diagrams/ (both languages) - run it after a change
```

Practice files are in the Homework repository; students run
`python 01-intro-syntax-types/practice/task1-first-values.py` from its root.

## Runnable Python

Write ` ```python run ` instead of ` ```python ` (line highlighting works too:
` ```python{2,3} run `). On the page:

- every block runs in a fresh namespace - variables do not carry over between
  blocks;
- the files of `data/` are in the folder `data/` (`pd.read_csv("data/loans.csv")`);
- the value of the last line is printed if it is an expression (like Jupyter);
- imported packages (pandas, numpy, matplotlib, ...) are loaded automatically;
  matplotlib figures are shown as images;
- `input()` does not work.

The Pyodide version is set in `site/.vitepress/theme/pyRunner.js`
(`PYODIDE_VERSION`). Pyodide runs a newer Python (3.14) than the students'
3.12 / 3.13 - avoid features newer than 3.12 in the examples.

## Two languages

Every page is also in Bulgarian, under `/bg/`; the **EN / BG** button next to the
theme switch changes the language. English is the source. The translations are
gettext `.po` files in `i18n/bg/` (one per page), filled in by a translator; the
Bulgarian pages are generated from them on every `npm run dev` / `npm run build`.

```bash
npm run i18n:update     # after changing English pages: refresh the .po files
npm run i18n:status     # what is left to translate (and how many words)
npm run i18n:pack       # zip for the translator
npm run i18n:import -- <folder or files>   # the translator's files back
npm run i18n:check      # broken code, links or markup in translations
```

Workflow and details: [`i18n/README.md`](i18n/README.md).

## Writing a lecture

- **Callouts:** `::: tip`, `::: warning`, `::: danger`, `::: info`, and
  `::: details Answer` for answers to check-yourself questions.
- **Data files:** `<DataFile file="loans.csv" />` shows `data/loans.csv` as a button
  that opens a preview of the file: a table with a filter (CSV, the sheets of an
  `.xlsx`, the tables of an SQLite `.db`), the file as text, and Download. The file
  is read in the browser, without Python (`theme/dataPreview.js`). Used on
  `sample-data.md`; works in a table cell and in lectures too.
- **Diagrams:** `![Alt text](/diagrams/name.svg){.diagram}`; add the drawing and its
  English and Bulgarian texts to `tools/make-diagrams.py` and run it. In dark mode the
  site inverts them (`theme/diagram.css`).
- **Animations:** a page in `site/public/animations/` that uses `anim.js` (see
  `namesAndObjects.html`); every text is a pair `[English, Bulgarian]`. Add a
  `bg/<page>.html` redirect (copy one) so that the Bulgarian pages link to it, and list
  it in `under-the-hood.md`. Link a scenario as
  `[1. Title](../animations/page.html#1){target="_blank"}`.
- **New lecture:** add the page to `lectures` in `.vitepress/config.mjs`, link it from
  `index.md` and `agenda.md`, and put its practice files in `NN-topic/` of the
  Homework repository. This can be done long before the session: the public site
  shows it only once it is released (next section).
- **Before class:** run every practice file and solution with `python`, run the
  examples (`node trainer/tools/run-examples.mjs NN`), and click through the page
  in `npm run dev`.
- **Translation:** after the English page is done, `npm run i18n:update`, then send
  the new `.po` file to the translator (`npm run i18n:pack`).

## Releasing a lecture

All lectures can be written in advance. The public site (`npm run build`, run by
GitHub Actions) shows only the lectures up to the number in
`site/.vitepress/released.mjs`. A lecture with a higher number has no page in
either language and is not in the search; every link to it (sidebar, agenda,
index, "see lecture N" in other lectures) is shown as plain text. `npm run dev`
and `TRAINER=1` builds show all lectures.

On the session day (or just before it):

1. Raise `releasedUpTo` in `site/.vitepress/released.mjs` to the session's number.
2. `npm run build` - check that the new page is in `site/.vitepress/dist/lectures/`.
3. Commit and push; GitHub Pages deploys.

The source of unreleased lectures is still in the repository (and readable on
GitHub); only the site hides it.

## Licence

CC BY-NC-SA 4.0 - see `LICENSE`. Copyright SciScend.

---

Built with Claude Opus 5.5 via Claude Code. Published by [SciScend](https://sciscend.com/).
