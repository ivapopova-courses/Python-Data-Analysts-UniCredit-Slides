# Slides - the course site of "Python for Data Analysts"

The lectures of a 16-session course for data analysts who move from SQL and SAS to
Python and pandas. A VitePress site built on course-kit, with an English source and
a generated Bulgarian version. How it works: `README.md` (layout, `python run`
blocks, releasing) and `i18n/README.md` (translations).

The course has other repositories (Homework, Labs, and a private trainer repo with
notes, outlines and solutions). They are **not** in this checkout: do not create
files that stand in for them, and do not change the site to depend on them.

## Commands

```bash
npm install             # once
npm run build           # must pass before every commit
npm run i18n:status     # what is left to translate
npm run i18n:check      # must find no problems after a change to i18n/
npm run i18n:update     # only after a change to an English page
```

Never run `npm run dev:trainer` / `build:trainer` (they read `../trainer`, which is
not here) and never deploy a build by hand: GitHub Actions deploys `main`.

## Rules

- **ASCII punctuation only** in everything you write: English pages, Bulgarian
  translations, commit messages, PR texts. Straight quotes `"..."`, a dash is
  ` - `, three dots `...`. Cyrillic letters in Bulgarian text are of course fine.
- **Privacy.** All data in the course is made up (`data/*.csv`: ids like `C0001`,
  `L000001`). The course is for an in-house group of a client company: do not name
  the client (or any real company, bank or person) in the site text, the
  translations, READMEs or commit messages. The repository name is the only place
  where it appears; do not copy it into text. Do not add anything about the
  group or its members.
- **Generated files - never edit them by hand:** `site/bg/` (git-ignored, made
  from `i18n/bg/*.po` on every build), `site/public/diagrams/` (made by
  `tools/make-diagrams.py`).
- **Translations:** edit only the `msgstr` lines of `i18n/bg/**/*.po`; never change
  a `msgid`, the `#.` / `#:` comments or the `X-Source-File` header. Follow
  `i18n/TRANSLATOR.md` and `i18n/glossary.md`. A machine translation sets the
  header `Last-Translator: Claude <model> (machine translation - to review)`.
- **Do not change** unless the task asks for it: `site/.vitepress/released.mjs`
  (`releasedUpTo` is raised by the author on the session day), the deploy
  workflow, the course-kit version, the content of the English lectures.
- **Python in the examples:** the students run Python 3.12 / 3.13 with pandas
  2.2+; the site runs Pyodide (Python 3.14, pandas 3.0). Examples must work on
  both; a feature newer than 3.12 or a pandas 2 / 3 difference is pointed out in
  the text.
- New lectures are written from outlines the author approves outside this repo.
  Do not write a new lecture or restructure an existing one on your own.

## Git

- Work on a branch and open a pull request to `main`; never push to `main`.
- Commit messages in English. Every commit ends with a trailer naming the model,
  from your exact model ID, in its own final paragraph after a blank line:
  `Assisted-by: claude-opus-5-5` (for example). No `Co-Authored-By: Claude` or
  "Generated with Claude Code" lines.
