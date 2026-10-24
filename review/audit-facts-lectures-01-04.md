# Facts audit: lectures 1 - 4, how-to, sample data

Date of the audit: 2026-10-24. Report only - no page was changed.

Pages: `site/lectures/01-intro-syntax-types.md`, `02-conditions-and-loops.md`,
`03-lists-tuples-sets.md`, `04-functions.md`, `site/how-to.md`, `site/sample-data.md`.

## Summary

| | |
|---|---|
| Runnable blocks (` ```python run `) | **270**: lecture 1: 72, lecture 2: 66, lecture 3: 57, lecture 4: 70, how-to: 2, sample data: 3 |
| Failing in A (3.12 / pandas 2.2) | 31 - all on purpose (the text or a comment announces the error) |
| Failing in B (3.14 / pandas 3.0) | 31 - the same blocks, the same exception types |
| Failing in only one environment | **0** |
| Output different between A and B | 11 - 4 caused by the Python version, 7 not deterministic (ids, addresses, timings, set order) |
| Warnings (any environment) | 0 |
| External links checked | 107 unique URLs: 57 OK, 22 redirected (all still work), 28 could not be checked automatically or failed - see "Links" |
| Findings | **wrong: 4**, **portability: 4**, **outdated: 3**, **minor: 9** |

Clean pages: **`sample-data.md`** has no findings. Lecture 2 and lecture 4 have one
finding each (a wrong sentence, no code problem). No example uses a feature newer than
Python 3.12, and no example depends on a pandas 2 / 3 difference.

The most important points:

1. **The students will not get pandas 2.2.** `pandas>=2.2` in `requirements.txt`
   (shown in lecture 1, section 4) resolves today to **pandas 3.1.0** and numpy 2.5.4
   on Python 3.12. The assumption "students run pandas 2.2" holds only if the
   Homework requirements pin `pandas<3`. (portability, lecture 1)
2. **Python 3.15 is out** (2026-10-09) and python.org now offers 3.15.1 and the
   *Python install manager* first; the setup advice still assumes the classic
   installer and links to the page that gives 3.15. (outdated / portability, how-to
   and lecture 1)
3. Three wrong sentences that a careful student will notice: "dictionaries are
   unordered" (lecture 3), "all three [extensions] are from Microsoft" with two listed
   (lecture 1), "the usual LGD as defaults" with no LGD in the code (lecture 4).

## 1. How the examples were run

Script: a scratch folder outside the repository. It extracts every ` ```python run `
and ` ```python{...} run ` block (also indented ones inside containers) and runs each
one in its own process, like the `DRIVER` of `site/.vitepress/theme/pyRunner.js`: a
fresh namespace with `__name__ == "__main__"`, file name `<example>`, the current folder
is the repository root, the last statement printed with `repr()` if it is an
expression (not after a trailing `;`), tracebacks cut to the lines of the example,
`MPLBACKEND=Agg`, `COLUMNS=200`, the "non-interactive" matplotlib warning ignored.

| Env | Python | pandas | numpy | matplotlib |
|---|---|---|---|---|
| A | 3.12.3 | 2.2.3 | 2.5.4 | 3.11.2 |
| B | 3.14.6 | 3.0.6 | 2.5.4 | 3.11.2 |
| C (extra) | 3.13 | 2.2.3 | 2.5.4 | 3.11.2 |
| The site: Pyodide 314.0.7 (from `pyodide-lock.json`) | 3.14.2 | 3.0.2 | 2.4.6 | 3.10.8 |

All environments were built with `uv`. C was added to separate Python 3.13 from
3.14 effects: C gives the same output as A in every block except the ones that are
not deterministic.

### Blocks that fail (on purpose) - 31, identical in A and B except two messages

| Page | Blocks (number on the page) | Error |
|---|---|---|
| Lecture 1 | 8, 20, 25, 29, 30, 33, 41, 42, 50, 51, 72 | IndentationError, SyntaxError, NameError, TypeError, ValueError - each announced by the text or a comment |
| Lecture 2 | 6, 33 | TypeError, SyntaxError - announced |
| Lecture 3 | 5, 23, 28, 31, 33, 46, 50, 54 | IndexError, TypeError, ValueError, KeyError - announced |
| Lecture 4 | 6, 9, 12, 15, 21, 27, 34, 38, 43, 48 | NameError, TypeError, SyntaxError, UnboundLocalError - announced |

Every error comment that quotes a message (`TypeError: 'int' object is not callable`,
`SyntaxError: name capture 'RETAIL' makes remaining patterns unreachable`,
`IndentationError: unexpected indent`, ...) was compared with the real message in A, B
and C; all match, except lecture 3, block 46 (see the findings).

### Blocks with different output in A and B - 11

| Page, block | Section | A (3.12) | B (3.14) | Cause / action |
|---|---|---|---|---|
| L1 #4 | Machine code, compilers and interpreters | `dis` shows offsets, `LOAD_CONST 0 (100)`, `RETURN_CONST` | no offsets, `LOAD_SMALL_INT 100`, `LOAD_CONST` + `RETURN_VALUE` | Python version; the text already says the instructions differ. None |
| L1 #26 | Names, not boxes | `11759912 11759912` ... | `23008552 23008552` ... | `id()` values are addresses; differ on every machine. None |
| L3 #33 | Unpacking | `ValueError: too many values to unpack (expected 2)` | `... (expected 2, got 3)` | Python 3.14 message; the text does not quote it. None |
| L3 #39 | 9. Lists or tuples? | `88 bytes for the list` / `64 bytes for the tuple` | `88` / `72` | Python 3.14 tuples are 8 bytes larger; see finding L3-M1 |
| L3 #46 | Create a set | `TypeError: unhashable type: 'list'` | `TypeError: cannot use 'list' as a set element (unhashable type: 'list')` | Python 3.14 message; see finding L3-P1 |
| L3 #45, #48, #54 | Create a set; SELECT DISTINCT; The four operations | e.g. `{1, 2, 3, 'b', 'a'}` | e.g. `{1, 2, 3, 'a', 'b'}` | String hashes are randomised per run (three runs of A gave two different orders). The warning box "The order of a set is not kept" already explains it. None |
| L3 #51 | Sets are fast for `in` | `0.015190 s` / `0.000003 s` | `0.009656 s` / `0.000002 s` | Timing. None |
| L4 #5 | 3. Calling a function | `<function greet at 0x7f4a...>` | `<function greet at 0x7f7a...>` | Address. None |
| L4 #68 | Arguments and the return value | `took 0.0003 s` | `took 0.0005 s` | Timing. None |

pandas: only 5 blocks use pandas or matplotlib (lecture 1 #1 and #5, how-to #2,
sample data #1 and #2). Their output is the same in A and B: no dtype is printed, so
the `object` / `str` difference of pandas 3 does not show; no copy-on-write case; the
chart (lecture 1 #5) draws one figure in both.

Windows: every `open()` in the examples passes `encoding="utf-8"`, so the examples do
not depend on the Windows default encoding (cp1252 / cp1251 on Python 3.12 / 3.13;
UTF-8 mode is the default only from 3.15). Good.

## 2. Findings by page

Severity: **wrong** - the text or code is incorrect; **portability** - works on the
site but not on the students' 3.12 / pandas 2.2 setup (or the reverse); **outdated**;
**minor**.

### Lecture 1 - `01-intro-syntax-types.md`

| # | Severity | Section | Block / quote | Problem | Evidence | Suggested fix |
|---|---|---|---|---|---|---|
| L1-W1 | wrong | 5. VS Code > Extensions and themes | "Install these ... all three are from Microsoft:" | Only two extensions follow (Python, Jupyter). Also incomplete: the Python extension now installs **three** others - Pylance, Python Debugger and Python Environments. | VS Code Marketplace API, `ms-python.python` 2026.11: `ExtensionPack = ms-python.vscode-pylance, ms-python.debugpy, ms-python.vscode-python-envs` | "both are from Microsoft"; "Python - running and debugging Python; it installs Pylance (completion, errors while you type), Python Debugger and Python Environments too" |
| L1-P1 | portability | 4. Installing Python and packages > `requirements.txt` | `pandas>=2.2`, `numpy>=2.0` | With no upper bound, `pip install -r requirements.txt` installs **pandas 3.1.0** and numpy 2.5.4 today, also on Python 3.12 (pandas 3 needs Python 3.11+). So the students run pandas 3, not 2.2 - the opposite of what the course assumes; later sessions (14 - 16) will meet the pandas 3 behaviour (`str` dtype, copy-on-write). | `uv pip install --dry-run "pandas>=2.2" "numpy>=2.0" "matplotlib>=3.9"` on Python 3.12: `+ pandas==3.1.0`, `+ numpy==2.5.4`. [pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html) | Decide which pandas the course targets. Either pin `pandas>=2.2,<3` in the Homework `requirements.txt` and in this listing, or accept pandas 3 (it matches the site) and update the course assumption. The listing on this page must match the Homework file. |
| L1-O1 | outdated | 2. Python next to SQL and SAS > A short history | "(3.12 in 2023, 3.13 in 2024, 3.14 in 2025)" | Python 3.15 came out on 2026-10-09. 3.12 and 3.13 are both in the security-only phase: python.org has no new Windows installers for them (the last are 3.12.10 and 3.13.17). | [devguide.python.org/versions](https://devguide.python.org/versions/): 3.15 bugfix, first release 2026-10-09; 3.13 and 3.12 "security". [python.org/downloads/windows](https://www.python.org/downloads/windows/): last 3.12 installer 3.12.10 (2025-04-08), 3.13.17 (2026-10-21) | Add "3.15 in 2026". Optional: "3.12 and 3.13 now get only security fixes - fine for this course". |
| L1-O2 | outdated | 4. > Several Python versions | "Since Python 3.14, python.org also offers the *Python install manager* for Windows" | The install manager is now the **first** entry of python.org's Windows page ("Latest Python install manager - Python install manager 26.4"), above "Latest Python 3 Release - Python 3.15.1". The classic installer (with "Add python.exe to PATH") is still offered per version, but a student who takes the first download gets the install manager, where `py install 3.13` / `py list` are the commands. | [python.org/downloads/windows](https://www.python.org/downloads/windows/) (2026-10-24); [Using Python on Windows](https://docs.python.org/3/using/windows.html) | One sentence: "python.org now offers the Python install manager first: with it, `py install 3.13` installs a version and `py list` shows them." See also how-to finding H-P1. |
| L1-O3 | outdated | 3. > "Advanced: faster Python" | "Python 3.13 added two experiments: a JIT compiler ... and a free-threaded build ... Both are off by default." | True for 3.13, but the site runs 3.14: there the free-threaded build is **officially supported** (no longer experimental), and the official Windows and macOS binaries include the (still experimental) JIT, off by default. | [What's New in Python 3.14](https://docs.python.org/3.14/whatsnew/3.14.html): "PEP 779: Free-threaded Python is officially supported"; "Binary releases for the experimental just-in-time compiler" | Add: "In 3.14 the free-threaded build is officially supported, and the Windows and macOS installers include the JIT (still off by default)." |
| L1-M1 | minor | 11. Numbers and operators > Comparison operators | SAS column: `` `<`, `LE` `` and `` `>`, `GE` `` | Each row covers two Python operators (`<`, `<=`), but the SAS cell mixes the symbol of one with the mnemonic of the other. Lecture 2 has the right mapping. | SAS: `<` = `LT`, `<=` = `LE`, `>` = `GT`, `>=` = `GE` | `` `<`, `<=` (`LT`, `LE`) `` and `` `>`, `>=` (`GT`, `GE`) `` |
| L1-M2 | minor | 14. > `round()` rounds half to even | "SAS `ROUND` and SQL `ROUND` round a 5 away from zero" | True for SAS and for `DECIMAL` / `NUMERIC` values in SQL; but e.g. PostgreSQL rounds `double precision` values half to even. | [PostgreSQL math functions](https://www.postgresql.org/docs/current/functions-math.html): "For numeric, ties are broken by rounding away from zero. For double precision, the tie-breaking behavior is platform dependent, but 'round to nearest even' is the most common rule." | "SQL `ROUND` on `DECIMAL` / `NUMERIC` values" |
| L1-M3 | minor | Read more | "NumPy for beginners (SciPy 2019)" | The video is the SciPy **2018** tutorial. | YouTube oEmbed for `V0D2mhVt7NE`: "Intro to Numerical Computing with NumPy (Beginner) \| SciPy 2018 Tutorial" | "(SciPy 2018)" |
| L1-M4 | minor | Read more | "pandas from the ground up (PyCon 2015)" | Could not confirm the video: YouTube oEmbed answers `401 Unauthorized` for `5JnMutdy6Fw` (embedding disabled, or private); the page itself was rate-limited (429). The other 6 YouTube links answer normally. | `https://www.youtube.com/oembed?url=...5JnMutdy6Fw` -> 401 | Open it in a browser; if it is gone, replace it or drop it. |
| L1-M5 | minor | Read more | "JupyterLab (video)" | The video is "JupyterLab: The Next-Generation Jupyter Frontend" (O'Reilly) - an early presentation from before JupyterLab 1.0; the interface of JupyterLab 4 (in `requirements.txt`: `jupyterlab>=4.2`) looks different. | YouTube oEmbed for `w7jq4XgwLJQ` | Replace with the [JupyterLab "Get Started" docs](https://jupyterlab.readthedocs.io/en/stable/getting_started/overview.html) or a recent video. |

Checked and correct in lecture 1 (no action): Zen of Python has 19 aphorisms; Python
1.0 1994 / 2.0 2000 / 3.0 2008 / end of Python 2 in 2020; 5 years of support per
version; the 3.13 REPL (colours, multi-line editing, `exit` without brackets);
`SyntaxWarning` for `"\d"` since 3.12 (A and B both warn); the Anaconda licence
threshold of 200 employees; `py --list` / `py -0`; `uv python install 3.12`; f-strings
since 3.6 (2016); `Decimal` default precision 28; `int("1_000")`; the precedence
table; the store aliases path; JupyterLab `Ctrl+Shift+C`; every value printed in a
comment (`# 2.68`, `# 512`, `# -4`, `# 1100.0`, ...) matches the run.

### Lecture 2 - `02-conditions-and-loops.md`

| # | Severity | Section | Block / quote | Problem | Evidence | Suggested fix |
|---|---|---|---|---|---|---|
| L2-W1 | wrong | 14. `continue` | "`continue` skips the records you do not want - like a `WHERE`, or a `DELETE` / `RETURN` in a DATA step" | `RETURN` does not skip a record: at the end of the step it causes an **implicit OUTPUT**, so the row is written. Only `DELETE` (or a subsetting `IF`) drops it. | SAS documentation, RETURN statement (summary): when `RETURN` sends control back to the beginning of the DATA step, an implicit `OUTPUT` writes the observation (unless the step has an explicit `OUTPUT`) | "like a `WHERE`, a subsetting `IF` or `DELETE` in a DATA step" |

Checked and correct (no action): `match` since 3.10; the `SyntaxError: name capture
'RETAIL' makes remaining patterns unreachable` message (identical in 3.12, 3.13 and
3.14); SQL `NULL AND TRUE` is `NULL`; SAS `ifc()` / `coalesce()`; "after 22 tries"
and the `-0.00` of the schedule match the runs; the IFRS 9 stage rule matches the
sample data. The SAS `do until` / `while True` mapping is right.

### Lecture 3 - `03-lists-tuples-sets.md`

| # | Severity | Section | Block / quote | Problem | Evidence | Suggested fix |
|---|---|---|---|---|---|---|
| L3-W1 | wrong | 11. Sets > Sets and dictionaries | "Both are **unordered** collections" | Dictionaries keep the insertion order, guaranteed since Python 3.7. The same page relies on it a few lines above: "To remove duplicates **and** keep the first order: `list(dict.fromkeys(items))`". | [Mapping types - dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict): "Changed in version 3.7: Dictionary order is guaranteed to be insertion order." | "Both are **mutable** and use **curly brackets**. A set has no order; a dictionary keeps the order in which the keys were added (session 6)." |
| L3-P1 | portability | 11. > Create a set | block 46: `# TypeError: unhashable type: 'list'` | The comment quotes the 3.12 / 3.13 message. On the site (3.14) the student sees `TypeError: cannot use 'list' as a set element (unhashable type: 'list')`. | Run: A and C `TypeError: unhashable type: 'list'`; B `TypeError: cannot use 'list' as a set element (unhashable type: 'list')` | `# TypeError: a list is unhashable` (true for both), or quote both messages. |
| L3-M1 | minor | 9. Lists or tuples? | block 39, `sys.getsizeof` | The tuple is 64 bytes in 3.12 / 3.13 but 72 bytes in 3.14 (the site); the list is 88 in both. The point (a tuple is smaller) holds, the numbers do not. Not quoted in the text, so no error - only a student comparing the site with VS Code will wonder. | Run: A `88` / `64`, B `88` / `72` | Optional: "(the exact numbers depend on the Python version)". |
| L3-M2 | minor | 12. > The four operations | table: "`EXCEPT` (Oracle: `MINUS`)" | Oracle supports `EXCEPT` since 21c; `MINUS` is the old name. | [Oracle 21c SQL reference, The Set Operators](https://docs.oracle.com/en/database/oracle/oracle-database/21/sqlrf/The-UNION-ALL-INTERSECT-MINUS-Operators.html): "The EXCEPT operator is a synonym for MINUS" | "`EXCEPT` (older Oracle: `MINUS`)" |

Checked and correct (no action): the slice comments (`[2, 3, 4]`, `[9, 8, 7]`, ...);
`range` is 48 bytes for any length in A and B; `sorted()` / `list.sort()`; set
operations; the `frozenset` example; the "order of a set" warning (confirmed: the
order changes from run to run).

### Lecture 4 - `04-functions.md`

| # | Severity | Section | Block / quote | Problem | Evidence | Suggested fix |
|---|---|---|---|---|---|---|
| L4-W1 | wrong | 4. > Default values | "On the portfolio - the most common term and the usual LGD as defaults:" | The example below (`annuity_payment(amount, yearly_rate, years=5)`) has only the term as a default; there is no LGD. | Block 11 of the page | "On the portfolio - the most common term as a default:" (or add an `expected_loss(..., lgd=0.45)` example) |

Checked and correct (no action): `str | None` since 3.10; the `type` statement since
3.12; lazy annotations in 3.14 (PEP 649 / 749) with the note that it is not needed for
3.12 / 3.13; every type hint of section 8 works in 3.12; `sorted()` has keyword-only
`key` / `reverse`; `help(len)` shows `len(obj, /)`; the `UnboundLocalError` message;
PEP 8 on named lambdas; PEP 257; the fixed BGN / EUR rate 1.95583.

### How-to - `how-to.md`

| # | Severity | Section | Block / quote | Problem | Evidence | Suggested fix |
|---|---|---|---|---|---|---|
| H-P1 | portability | Set up Python on your computer | "[Python](https://www.python.org/downloads/) 3.12 or 3.13, 64-bit"; "tick **Add python.exe to PATH** on the first screen of the Python installer" | The link leads to the page whose big button is now **Python 3.15.1** (not the course's 3.12 / 3.13, not the site's 3.14), and on Windows the first download is the **Python install manager**, which has no "Add python.exe to PATH" screen. A student who follows the link literally ends up with 3.15 or with a different installer than described. | [python.org/downloads/windows](https://www.python.org/downloads/windows/) on 2026-10-24: "Latest Python install manager - Python install manager 26.4", "Latest Python 3 Release - Python 3.15.1", then "Python 3.13.17 - Oct. 21, 2026 ... Download Windows installer (64-bit)" | Link to `https://www.python.org/downloads/windows/` and say: "under Stable Releases, the newest **Python 3.13.x** - **Download Windows installer (64-bit)**"; or describe the install manager path (`py install 3.13`). |
| H-P2 | portability | Practice and homework > 8. Create the virtual environment | `.venv\Scripts\activate` | The default terminal of VS Code on Windows is PowerShell, where this runs `Activate.ps1` and can fail with "running scripts is disabled on this system". The fix is only in lecture 1 (section 4, the warning box); the first-time setup page does not mention it. | Lecture 1, "PowerShell: running scripts is disabled on this system" | Add one line: "PowerShell says *running scripts is disabled*? See [lecture 1](/lectures/01-intro-syntax-types#virtual-environments)" (or copy the `Set-ExecutionPolicy ... -Scope Process` line). |

Checked and correct (no action): the two runnable blocks; `py -m venv .venv`;
`python -m pip install --upgrade pip`; the Git steps.

### Sample data - `sample-data.md`

**Clean.** The row counts (150 / 400 / 10), every example value in the column tables
(`C0002 sme Ruse M 5 2014-06-08`, `L000001 ... 1156900.00 1044231.30 8.83`,
`4 BBB 0.0025 0.006 moderate risk`) match `data/*.csv`; the stage rule ("stage 3 means
more than 90 days past due or rating 10", with stage 2 as in lecture 2) holds for all
400 loans (0 mismatches); retail clients have an empty `industry` (91 of 91). The three
blocks give the same output in A and B.

## 3. Links

107 unique external URLs in the six pages, each requested (with redirects followed):

| Result | Count | Notes |
|---|---|---|
| 200, no redirect | 57 | |
| 200 after a redirect | 22 | see below - all still work, anchors exist on the target pages |
| Real Python (9), Rosetta Code (2) | 11 | 403 "Just a moment..." (Cloudflare bot check), also from a headless browser - **not checked**; check by hand |
| YouTube | 7 | 429 from the page; checked through the oEmbed API instead: 6 OK, 1 unclear (L1-M4) |
| GitHub | 9 | the proxy blocks plain requests; in a headless browser: `github.com`, `microsoft/vscode`, `pyenv/pyenv` OK, `/signup` 403 (bot check), `your-user/...` is a placeholder (fine) |
| The course's own Homework and Labs repositories (4 URLs) and the course site URL (1) | 5 | 404 for an anonymous visitor (private repositories; the site URL answers "Site not found - GitHub Pages"). Fine if the students are added as collaborators and the site is meant to be private; if the site should be public, check the Pages settings. |

Redirects (minor, optional to update):

- `docs.python.org/3/library/functions.html` (5 links: page, `#enumerate`, `#input`,
  `#ord`, `#print`) -> `docs.python.org/3/builtins/functions.html`, and
  `docs.python.org/3/library/stdtypes.html` (8 links) ->
  `docs.python.org/3/builtins/stdtypes.html`. `docs.python.org/3/` is now the **3.15**
  documentation; all anchors exist there. Consider linking to `/3.13/` (the students'
  version), where the old paths still work.
- VS Code docs (6 links): `docs/editor/tasks` -> `docs/debugtest/tasks`,
  `docs/editor/workspaces` -> `docs/editing/workspaces/workspaces`,
  `docs/getstarted/themes` -> `docs/configure/themes`,
  `docs/getstarted/tips-and-tricks` (2) -> `docs/editing/getting-started/tips-and-tricks`,
  `docs/getstarted/userinterface` -> `docs/editing/getting-started/userinterface`.
- `docs.conda.io/` -> `/en/latest/`, `pipenv.pypa.io/` -> `/en/latest/`,
  `pyodide.org/` -> `/en/stable/`, `git-scm.com/downloads` -> `/downloads/` (harmless).

## 4. All findings by severity

| Severity | Count | Findings |
|---|---|---|
| wrong | 4 | L1-W1, L2-W1, L3-W1, L4-W1 |
| portability | 4 | L1-P1 (pandas 3 through `requirements.txt`), L3-P1, H-P1, H-P2 |
| outdated | 3 | L1-O1, L1-O2, L1-O3 |
| minor | 9 | L1-M1, L1-M2, L1-M3, L1-M4, L1-M5, L3-M1, L3-M2, the docs.python.org redirects, the VS Code docs redirects (section 3) |
