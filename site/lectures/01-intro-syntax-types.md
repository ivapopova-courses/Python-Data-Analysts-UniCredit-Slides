---
title: 1. Introduction, syntax, data types and variables
---

# 1. Introduction, syntax, data types and variables

<div class="lecture-meta">
  <span>Session 1</span><span>practice: <code>01-intro-syntax-types/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- find your way in the course: the goal, the sessions, the materials;
- say what Python is good for, next to SQL and SAS, and how it runs your code;
- set up a project: Python, a virtual environment, `pip` and `requirements.txt`;
- run Python code in VS Code, in the terminal and in a Jupyter notebook;
- read the structure of a program: lines, indentation, comments, `print()`;
- work with the basic types: `int`, `float`, `str`, `bool`, `None`;
- use variables, and understand what a name in Python really is;
- calculate with the operators and the `math` module;
- convert values between types and build text with f-strings;
- calculate money values exactly with `Decimal`, and round them the way SAS and SQL do.

From SQL to Python - the same question, two ways:

```sql
SELECT SUM(outstanding) FROM loans WHERE stage = 3;
```

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(loans.loc[loans["stage"] == 3, "outstanding"].sum())
```

By session 16 you will write code like this every day. Today we start from the
pieces it is made of: values, types, variables and operators.

## 1. About the course

### The goal

**A smooth move to Python as the main tool for the same daily work** that you now
do in SQL and SAS: reporting, modelling and ad-hoc analysis. You already know how
to work with data - joins, groups, filters, formats. In this course you learn the
same things in a new language, and what Python adds on top: automation of files and
reports, a huge choice of free libraries, and notebooks that mix code, tables,
charts and text.

### The sessions

16 sessions of 4 academic hours. The full plan is on the [Agenda](/agenda) page:

| Sessions | Topic |
|---|---|
| 1 - 2 | The language: types, variables, operators, conditions and loops |
| 3 - 6 | Collections: lists, tuples, sets, dictionaries; functions |
| 7 - 9 | Text, regular expressions, errors and files |
| 10 - 12 | Modules, Git, classes and objects |
| 13 | Databases: SQL from Python |
| 14 - 16 | NumPy and pandas: the Python version of your SQL and SAS work; the final project |

### How we work

- **Theory with many examples.** Every lecture page has runnable examples: press
  **Run** under an example, change it with **Edit**, run it again (see
  [How to use these pages](/how-to)).
- **Practice in VS Code.** Each session has practice tasks that check themselves and
  print `OK` or `FAIL`, and a homework. We review the homework at the start of the
  next session.
- **From what you know.** Every topic starts from its SQL or SAS version: `CASE
  WHEN`, `GROUP BY`, `JOIN`, the DATA step, `PROC SORT`, `PROC MEANS`, formats,
  macros.
- **Made-up data.** All examples use a small loan portfolio that looks like real
  data but is invented: [the sample data](/sample-data).
- **Questions at any time.** Do not wait for the end of the session - ask whenever
  something is not clear. Feedback is welcome at any time too: what helps, what
  does not, what is hard.

### The materials

| What | Where |
|---|---|
| The lectures (this site) | https://ivapopova-courses.github.io/Python-Data-Analysts-UniCredit-Slides/ |
| Practice tasks and homework | https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework |
| The code written in class | https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Labs |
| Step-by-step animations | [Animations](/under-the-hood) |
| The final project | [Final project](/project) |

## 2. Python next to SQL and SAS

### What Python is

Python is a **general-purpose programming language**: free, open source, and one of
the most used languages in the world. It is used for:

- data analysis, statistics, machine learning and AI;
- automation: files, Excel reports, emails, scheduled jobs;
- web applications and web services;
- system administration and the cloud;
- science, education, and small devices (Raspberry Pi).

For an analyst, the main reason is the **libraries**: pandas and NumPy for tables
and numbers, matplotlib for charts, statsmodels and scikit-learn for models,
openpyxl for Excel, SQLAlchemy for databases. They are all free.

### SQL, SAS and Python - what each is for

| | SQL | SAS | Python |
|---|---|---|---|
| What it is | a query language of the database | a commercial system for data and statistics | a general-purpose language with libraries for data |
| Where the data is | in the database | SAS data sets (`.sas7bdat`), libraries | in memory: lists, dictionaries, pandas DataFrames; files and databases |
| Typical work | select, join, group, filter | DATA step, PROCs, formats, macros | everything above, plus automation, charts, models |
| Price | part of the database | licence | free |

You will **not** stop using SQL. The best place to filter and join big tables is
still the database; Python sends the SQL query and works with the result (session
13). Python replaces mostly the SAS part of the work - and adds what neither SQL nor
SAS does well.

How SAS ideas map to Python (most of them come in the later sessions):

| SAS | Python |
|---|---|
| DATA step | a loop over rows (sessions 2 - 6), or pandas (sessions 14 - 16) |
| `PROC SORT` | `sorted()`, `DataFrame.sort_values()` |
| `PROC MEANS`, `PROC SUMMARY` | `sum()`, `statistics`, `DataFrame.groupby().agg()` |
| `PROC FREQ` | `collections.Counter`, `value_counts()`, `pd.crosstab()` |
| `PROC TRANSPOSE` | `DataFrame.pivot()`, `melt()` |
| formats (`COMMA12.2`, `PERCENT8.2`) | f-strings: `f"{x:,.2f}"`, `f"{x:.2%}"` - section 13 |
| macros, `%LET` | functions (session 4), variables |
| `LIBNAME` | file paths, database connections |
| the SAS log | the output in the terminal; error messages (*tracebacks*) |
| an Enterprise Guide project | a Jupyter notebook - section 7 |

### "Batteries included"

Python comes with a large **standard library**: modules for files, CSV, JSON, dates,
exact decimal numbers, regular expressions, SQLite databases, statistics, and much
more. You only `import` them. Everything else is on **PyPI**, the Python Package
Index (https://pypi.org): hundreds of thousands of free packages, installed with
`pip` (section 4).

```python run
import statistics

rates = [8.83, 5.44, 4.79, 8.35]
print(statistics.mean(rates))
print(statistics.median(rates))
```

### The Zen of Python

The design rules of the language, written by Tim Peters. Run `import this` to see
all 19:

```python run
import this
```

The ones you will feel most in this course:

- *Readability counts.* Code is read much more often than it is written.
- *Explicit is better than implicit.* Python does not convert `"5"` to `5` for you
  (SAS does, with a note in the log) - you say what you want (section 12).
- *Errors should never pass silently.* A problem stops the program with a clear
  message, instead of a wrong number in the report.
- *There should be one - and preferably only one - obvious way to do it.*

### A short history

- **1991:** the first version, by **Guido van Rossum** in the Netherlands. The name
  comes from the comedy show *Monty Python's Flying Circus*, not from the snake.
- **1994:** Python 1.0. **2000:** Python 2.0.
- **2008:** Python 3.0 - not compatible with Python 2. Python 2 ended in **2020**:
  if you find Python 2 code (`print "hello"` without brackets), it is old.
- Since 2019 a new version comes out **every October** (3.12 in 2023, 3.13 in 2024,
  3.14 in 2025, 3.15 in 2026), and each version gets security fixes for 5 years. In
  this course you use **3.12 or 3.13**: they now get only security fixes, which is fine
  for the course.

### Implementations

Python is a language; a program that runs Python code is an *implementation*:

| Implementation | What it is |
|---|---|
| [CPython](https://www.python.org/) | the standard one, written in C - the Python you install from python.org. When people say "Python", they mean CPython |
| [PyPy](https://pypy.org/) | a faster implementation with a JIT compiler, for long-running pure-Python code |
| [Pyodide](https://pyodide.org/) | CPython compiled for the browser (WebAssembly) - it runs the examples on this site |
| [MicroPython](https://micropython.org/) | a small Python for microcontrollers |
| [Cython](https://cython.org/) | not an implementation, but a compiler: Python-like code to C, for fast extensions. Parts of pandas are written in it |

Older names you may still meet: Jython (Python on Java) and IronPython (Python on
.NET) are rarely used today.

## 3. How Python runs your code

### Machine code, compilers and interpreters

The processor understands only **machine code**: very simple instructions in binary.
A program in a "human" language must be translated first. There are two classic
ways:

- A **compiler** translates the **whole** program first, into a file that runs
  (an `.exe`). Like a translator who translates the whole book, and then you read it.
  Languages: C, C++, Rust; Java and C# compile to *bytecode* for a virtual machine.
- An **interpreter** reads the program and runs it **straight away**, statement by
  statement, without an `.exe`. Like an interpreter at a meeting, sentence by
  sentence. Languages: Python, JavaScript, PHP, Ruby. SAS works in a similar way:
  it compiles and runs one DATA step or PROC at a time.

Python is an **interpreted** language, with a small compiler inside:

1. it reads your file and checks the syntax - a `SyntaxError` stops everything here,
   before the first line runs;
2. it translates the code into **bytecode**, simple instructions for the Python
   virtual machine (imported modules keep their bytecode in `__pycache__` folders
   with `.pyc` files - you will see one in the Homework repository);
3. the **Python virtual machine** runs the bytecode, one instruction at a time;
4. the results go to the screen, to files, to a database.

![From your code to the result: a script, the REPL or a notebook cell go to the Python interpreter, which compiles them to bytecode and runs it](/diagrams/run-python.svg){.diagram}

You can see the bytecode with the `dis` module (the instructions differ a little
between Python versions):

```python run
import dis

dis.dis("interest = outstanding * rate / 100")
```

::: info Advanced: faster Python
Python 3.13 added two experiments: a **JIT compiler** (it turns hot bytecode into
machine code) and a **free-threaded** build without the GIL (Python code can run
on several processor cores at once). Both are off by default. In 3.14 the
free-threaded build is officially supported, and the Windows and macOS installers
include the JIT (still off by default). For data work, speed
comes from the libraries: pandas and NumPy do the heavy work in C.
:::

A short video about compilers and interpreters:
[How do computers read code?](https://www.youtube.com/watch?v=QXjU9qTsYCc)
(Frame of Essence). Hello World in hundreds of languages:
[rosettacode.org](https://rosettacode.org/wiki/Hello_world/Text).

## 4. Installing Python and packages

You installed the tools before the course - see
[Set up Python on your computer](/how-to#setup). This section explains what each
step does, so you can do it again for a new project.

### Python

- **Windows:** the installer from
  [python.org/downloads](https://www.python.org/downloads/windows/). On the first
  screen tick **Add python.exe to PATH**. Python goes to
  `C:\Users\<you>\AppData\Local\Programs\Python\Python3xx\`.
- **macOS:** the installer from python.org, or Homebrew
  ([Using Python on macOS](https://docs.python.org/3/using/mac.html)).
- **Linux:** usually installed; otherwise the package manager of the system
  ([Using Python on Unix](https://docs.python.org/3/using/unix.html)).

Check it in a terminal:

::: code-group
```powershell [Windows]
py --version          # the Python launcher
python --version      # if Python is in PATH
```
```bash [Linux / macOS]
python3 --version
```
:::

::: warning "python" opens the Microsoft Store?
On Windows, `python` can start the Microsoft Store instead of your Python. Use
`py`, or switch off the store aliases: **Settings > Apps > Advanced app settings >
App execution aliases**, turn off `python.exe` and `python3.exe`. If the command is
not found at all, Python is not in `PATH`:
[How to add Python to PATH](https://realpython.com/add-python-to-path/).
:::

### Several Python versions

You can have several versions side by side. On Windows the **Python launcher**
`py` chooses one:

```powershell
py --list            # the installed versions (also: py -0)
py -3.12 --version   # run a given version
py -3.12 -m venv .venv   # a virtual environment with Python 3.12
```

On macOS and Linux, the tools for this are [pyenv](https://github.com/pyenv/pyenv) and
[uv](https://docs.astral.sh/uv/) (`uv python install 3.12`). On Windows, python.org
now offers the *Python install manager* first: with it, `py install 3.13` installs a
version and `py list` shows the installed ones. The classic installer of each
version (with **Add python.exe to PATH**) is still on the
[Windows downloads page](https://www.python.org/downloads/windows/).

### Packages and pip

A **package** (or *library*) is code someone wrote for others to use: pandas,
NumPy, matplotlib. **pip** installs packages from PyPI:

| Command | What it does |
|---|---|
| `pip install pandas` | installs the latest version that works with your Python |
| `pip install "pandas>=2.2"` | a version 2.2 or newer |
| `pip install --upgrade pandas` | installs a newer version |
| `pip uninstall pandas` | removes it |
| `pip list` | the installed packages |
| `pip show pandas` | the version, where it is, what it needs |
| `pip freeze` | the installed packages with their exact versions |
| `pip install -r requirements.txt` | everything listed in the file |
| `pip help` | all commands ([pip documentation](https://pip.pypa.io/en/stable/cli/)) |

::: tip `python -m pip`
`python -m pip install ...` is the same as `pip install ...`, but it is sure to use
the `pip` of **this** `python`. Use it when you are not sure which Python is active.
:::

### Virtual environments

**Why.** Each project needs its own packages, often in a given version: last year's
report needs pandas 2.2, a new model needs pandas 3. If all projects install into
the one Python of the computer, a new install can break an old project (this is
called *dependency hell*).

**What.** A **virtual environment** (venv) is a folder in the project - usually
`.venv` - with its own copy of `python` and its own packages. Packages installed while
it is active go there, and only there.

![The system Python and two projects, each with its own .venv folder and its own versions of the packages](/diagrams/venv.svg){.diagram}

The `venv` module comes with Python. Once per project, in the project folder:

::: code-group
```powershell [Windows]
py -m venv .venv
```
```bash [Linux / macOS]
python3 -m venv .venv
```
:::

Every time you work on the project, **activate** it:

::: code-group
```powershell [Windows]
.venv\Scripts\activate            # PowerShell and cmd
source .venv/Scripts/activate     # only in Git Bash
```
```bash [Linux / macOS]
source .venv/bin/activate
```
:::

The prompt starts with `(.venv)`. Now `python` and `pip` are the ones in `.venv`:

::: code-group
```powershell [Windows]
where.exe python   # the first line must end with .venv\Scripts\python.exe
deactivate         # leave the virtual environment
```
```bash [Linux / macOS]
which python       # must end with .venv/bin/python
deactivate         # leave the virtual environment
```
:::

::: warning PowerShell: "running scripts is disabled on this system"
PowerShell may refuse to run `Activate.ps1`. Allow it for the current terminal only,
then activate again:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.venv\Scripts\activate
```

Or use the **Command Prompt** (cmd): in VS Code, the **v** next to the **+** of the
terminal panel opens a new terminal of another type.
:::

### `requirements.txt`: the list of packages

A project lists its packages in `requirements.txt`, so anyone can rebuild the same
environment. The Homework repository has one:

```text
jupyterlab>=4.2
ipykernel>=6.29
numpy>=2.0
pandas>=2.2
openpyxl>=3.1
sqlalchemy>=2.0
matplotlib>=3.9
```

```bash
pip install -r requirements.txt     # install all of them
pip freeze > requirements.txt       # or: write down the exact versions you have now
```

`pip freeze` gives exact versions (`pandas==3.1.0`): use it when a report must
give the same result next year, on another computer. This is called *freezing the
dependencies* - it avoids "but it works on my machine".

::: info pandas 2 or pandas 3?
`>=` means "this version or newer", so `pandas>=2.2` installs the newest pandas -
**pandas 3** today (3.1 in October 2026). The site runs pandas 3 too, so this course
uses pandas 3; where pandas 2.2 behaves differently (the type of text columns,
copies of a DataFrame), sessions 14 - 16 say so. Check yours with `pip show pandas`.
:::

What the packages of this course are for:

| Package | What for | Sessions |
|---|---|---|
| `numpy` | fast arrays and calculations with numbers | 14 - 16 |
| `pandas` | tables (DataFrame): read, filter, group, join, write | 14 - 16 (a preview today) |
| `matplotlib` | charts | 16 (a preview in section 7) |
| `jupyterlab`, `ipykernel` | Jupyter notebooks, in the browser and in VS Code | all |
| `openpyxl` | read and write Excel files | 9, 14 - 16 |
| `sqlalchemy` | connect pandas to a database | 13, 16 |

[seaborn](https://seaborn.pydata.org/) (nicer statistical charts, built on matplotlib)
is not in the list - install it with `pip` if you want to try it.

### Without a virtual environment: an example

A script that needs a package which is not installed stops at the `import`:

```text
> python simple_plot.py
Traceback (most recent call last):
  File "C:\course\simple_plot.py", line 1, in <module>
    import matplotlib.pyplot as plt
ModuleNotFoundError: No module named 'matplotlib'
```

The fix is not `pip install` into the system Python, but: activate the project's
venv (or create it), `pip install matplotlib` there, and run the script again.

### Other tools

| Tool | What it is |
|---|---|
| [uv](https://docs.astral.sh/uv/) | a new, very fast tool: Python versions, virtual environments and packages in one (`uv venv`, `uv pip install`) |
| [Poetry](https://python-poetry.org/), [pipenv](https://pipenv.pypa.io/) | manage a project's packages and venv together, with a lock file of exact versions |
| [conda](https://docs.conda.io/) | packages and environments, also for non-Python software; comes with Anaconda and Miniconda |

::: warning Anaconda in a company
The Anaconda Distribution and its default package channel need a **paid licence**
in organisations with more than 200 employees. This course uses the standard
python.org Python with `venv` and `pip`, which is free for everyone.
:::

## 5. VS Code

### Editors and IDEs

- [Visual Studio Code](https://code.visualstudio.com/) - free, open source
  ([on GitHub](https://github.com/microsoft/vscode)), by Microsoft, for every
  language; extensions add what you need. We use it in the course. It also runs in
  the browser: [vscode.dev](https://vscode.dev/).
- [PyCharm](https://www.jetbrains.com/pycharm/) - a Python IDE by JetBrains (a free
  version and a paid one).
- [Sublime Text](https://www.sublimetext.com/) - a fast, light editor.
- JupyterLab - notebooks in the browser (section 7).

### The parts of the window

| Part | Where | What for |
|---|---|---|
| Activity Bar | far left | Explorer, Search, Source Control (Git), Extensions |
| Side Bar | left | the files of the folder (Explorer) |
| Editor | middle | your files, in tabs |
| Panel | bottom | the Terminal, Problems, Output |
| Status Bar | very bottom | the active Python (for example `3.12.7 ('.venv')`) - click it to change it |

Read more: [User interface](https://code.visualstudio.com/docs/editing/getting-started/userinterface).

### Extensions and themes

Install these from the **Extensions** view (`Ctrl+Shift+X`); both are from
Microsoft:

- **Python** - running and debugging Python; it installs three more extensions
  too: **Pylance** (completion, errors while you type), **Python Debugger** and
  **Python Environments**;
- **Jupyter** - notebooks inside VS Code.

Later lectures work with data files. These extensions help you look at them
without leaving VS Code:

- **Data Wrangler** (Microsoft) - a DataFrame or a CSV file as a table you can
  sort and filter, with statistics per column; it writes the pandas code for the
  cleaning steps you click (lectures 14 - 16);
- **Rainbow CSV** (mechatroner) - each column of a CSV file in its own colour, and
  SQL-like queries on the file;
- **SQLite Viewer** (Florian Klampfer) - the tables of a SQLite database
  (lecture 13);
- **Spreadsheet Viewer** (MESCIUS) - `.xlsx` files inside VS Code.

You do not have to search for them one by one: the Homework folder lists them all
in `.vscode/extensions.json`, and VS Code offers to install them when you open the
folder. How, and how to use the same list in your own projects:
[VS Code extensions](/how-to#vscode-extensions).

A colour theme: `Ctrl+K Ctrl+T`
([Themes](https://code.visualstudio.com/docs/configure/themes)).

### A folder is a workspace

Always open the **folder** of a project, not single files: **File > Open Folder**,
or right-click the folder in Windows Explorer > **Open with Code**. The folder is
your **workspace**: VS Code remembers the open files, and you can keep settings for
this folder only in `.vscode/settings.json` (`Ctrl+Shift+P` >
**Preferences: Open Workspace Settings**). Read more:
[What is a VS Code workspace?](https://code.visualstudio.com/docs/editing/workspaces/workspaces)

For this course, the folders are:

```text
course/
    Python-Data-Analysts-UniCredit-Homework/   your work: tasks and homework
    Python-Data-Analysts-UniCredit-Labs/       the code from the lessons (only git pull)
```

### Choose the Python of the project

`Ctrl+Shift+P` > **Python: Select Interpreter** > the one in `.venv`. VS Code then
runs your files with it, and new terminals activate the venv by themselves.

### Create and run a Python file

1. In the Explorer, right-click the folder > **New File**, name it `hello.py`.
2. Write:

   ```python
   my_name = "Iva"
   print("Hello, " + my_name)
   ```

3. Run it, in one of these ways:
   - the **Run Python File** button (the triangle, top right);
   - right-click in the editor > **Run Python > Run Python File in Terminal**;
   - in the terminal: `python hello.py`;
   - `Ctrl+Enter` - only in the Labs folder, which has this shortcut in
     `.vscode/keybindings.json`.

The output appears in the **Terminal** panel.

::: tip Old way: a build task
Older courses used a *task* in `.vscode/tasks.json` and `Ctrl+Shift+B` to run the
file ([Tasks](https://code.visualstudio.com/docs/debugtest/tasks)). It still works, but
the Run button does the same without setup.
:::

### Shortcuts worth learning first

| Keys | Action |
|---|---|
| `Ctrl+Shift+P` | the Command Palette: every command, by name |
| `Ctrl+P` | open a file by name |
| `Ctrl+S` | save |
| `Ctrl+Z` / `Ctrl+Y` | undo / redo |
| `` Ctrl+` `` | show / hide the terminal |
| `Ctrl+B` | show / hide the Side Bar |
| `Ctrl+J` | show / hide the Panel |
| `Ctrl+/` | comment / uncomment the selected lines |
| `Ctrl+D` | select the next match of the selection (edit several places at once) |
| `Alt+Up` / `Alt+Down` | move the line up / down |
| `Shift+Enter` | run the selected lines in a Python terminal |
| `F5` | run with the debugger |

In the terminal, `cls` (cmd) or `clear` clears the screen. All shortcuts:
[keyboard reference sheets](https://code.visualstudio.com/docs/editing/getting-started/tips-and-tricks#_keyboard-reference-sheets).

### Git in VS Code

The **Source Control** view (`Ctrl+Shift+G`) shows the changed files; type a message,
**Commit**, then **Sync** (push). The commands for the Homework repository are in
[How to use these pages](/how-to#practice-and-homework); Git itself is the topic of
session 10.

## 6. The terminal and the REPL

### Run a script

A **script** is a `.py` file. Run it from a terminal, in the folder of the project:

```bash
python hello.py                                    # a file in this folder
python 01-intro-syntax-types/practice/task1-first-values.py
python -c "print(2 ** 10)"                         # one line of code
python -m pip --version                            # run a module
```

### The REPL

`python` (or `py`) **without a file** starts the interactive Python - the **REPL**
(read, evaluate, print, loop). Type a line, press `Enter`, see the result. The prompt
is `>>>`; `...` means "continue the statement":

```text
>>> 1044231.30 * 8.83 / 100
92205.62379000001
>>> rate = 8.83
>>> rate * 2
17.66
>>> exit()
```

You leave with `exit()`, or `Ctrl+Z` then `Enter` (Windows), `Ctrl+D` (macOS, Linux).
Since Python 3.13 the REPL has colours, editing of whole blocks, and `exit`
works without the brackets.

The REPL is good for a quick try. For anything you want to keep, write a file or a
notebook.

## 7. Jupyter notebooks

A **notebook** (`.ipynb` file) is a document of **cells**. A code cell runs, and its
result - a number, a table, a chart - appears right under it. Text cells explain the
work. It is the closest thing in Python to an Enterprise Guide project or a SQL
worksheet: ideal for exploring data and showing results.

![A notebook in JupyterLab: a Markdown cell with a heading, a code cell with a table as its output, and a code cell with a bar chart](/images/jupyterlab-notebook.png){.screenshot}

In the picture (JupyterLab in the browser):

- **left** - the file browser: the notebook is a normal file, next to the `data` folder;
- **"Portfolio check"** - a Markdown cell: a heading and a line of text;
- **`[1]`** - a code cell and its output, a table; the blue bar marks the selected cell;
- **`[2]`** - a code cell whose output is a chart;
- **top right** - the kernel, `Python 3 (ipykernel)`, the Python that runs the code;
  `Idle` in the status bar means that it waits for work.

### What is Jupyter?

[Project Jupyter](https://jupyter.org/) is the free, open-source project behind
notebooks. The name comes from three languages: **Ju**lia, **Pyt**hon and **R** -
a notebook can run other languages too, but we use only Python.

The notebook is the **file**; several programs can open the same `.ipynb`:

| Program | Where it runs |
|---|---|
| [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) | in the browser, started from your computer (`jupyter lab`) |
| [VS Code](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) | inside the editor - what we use in this course |
| cloud data platforms (for example Google Colab, Databricks) | on a server, opened in the browser |

An `.ipynb` file is text (JSON) that holds the code, the text **and the last
outputs**. So a notebook keeps its tables and charts when you close it, and GitHub
shows it as a page, with the results, without running it.

### What notebooks are used for

- **Exploring new data** - load a file, look at it, filter, count, step by step:
  like running SQL queries one after another in a worksheet.
- **Ad-hoc analysis** - a question from management, answered with a table and a
  chart, with the explanation next to them.
- **Reports and model documentation** - the code, the result and the comment in
  one file: a colleague can run it again and get the same numbers.
- **Trying an idea** - test the logic of a calculation on a few rows before it goes
  into a script.
- **Learning** - try one line, see the result at once.

Notebooks are not the right tool for a job that runs every month without a person,
or for code that many reports share - for that you write a script or a module
(see "Script or notebook?" at the end of this section, and lecture 10).

::: tip Try it without installing
[jupyter.org/try](https://jupyter.org/try) opens JupyterLab in the browser, with
nothing to install. Use it only with made-up data, never with the bank's data.
:::

### Cells

| Cell type | What it holds |
|---|---|
| Code | Python code; the output is shown below the cell |
| Markdown | text with headings, lists, tables, links ([Markdown syntax](https://www.markdownguide.org/basic-syntax/)); HTML works too |
| Raw | text that is not run or formatted |

### The kernel

The **kernel** is the Python process behind the notebook. It keeps the variables
**between cells**: a cell can use a variable from a cell above. (On this site, every
example runs on its own - in a notebook they do not.)

- The number in `[3]` next to a cell is the order in which the cells ran.
- If you run cells out of order, or delete a cell, the kernel still remembers its
  variables. Before you trust a result: **Restart** the kernel and **Run All**.

### Notebooks in VS Code

1. `Ctrl+Shift+P` > **Create: New Jupyter Notebook** (or a new file `analysis.ipynb`).
2. **Select Kernel** (top right) > **Python Environments** > the `.venv` of the project.
3. Write code in a cell, `Shift+Enter` runs it and goes to the next cell.

Or in the browser: `jupyter lab` in the terminal (with the venv active) opens
JupyterLab.

A cell with a chart - the same works in a notebook:

```python run
import pandas as pd
import matplotlib.pyplot as plt

loans = pd.read_csv("data/loans.csv")
by_product = loans.groupby("product")["outstanding"].sum() / 1_000_000
by_product.sort_values().plot.barh(title="Outstanding by product, million EUR")
plt.tight_layout()
plt.show()
```

### Keyboard shortcuts

A cell is in **edit mode** (you type in it) or in **command mode** (you work with
whole cells). `Esc` goes to command mode, `Enter` to edit mode.

| Mode | Keys | Action |
|---|---|---|
| both | `Shift+Enter` | run the cell, go to the next one |
| both | `Ctrl+Enter` | run the cell, stay on it |
| both | `Ctrl+S` | save |
| command | `A` / `B` | insert a cell above / below |
| command | `M` / `Y` | change the cell to Markdown / code |
| command | `D D` | delete the cell |
| command | `Z` | undo the delete |
| command | `C` / `X` / `V` | copy / cut / paste cells |
| edit | `Tab` | completion, or indent |
| edit | `Shift+Tab` | help for the function (JupyterLab) |
| edit | `Ctrl+/` | comment the lines |

All commands: the Command Palette - `Ctrl+Shift+P` in VS Code, `Ctrl+Shift+C` in
JupyterLab. All shortcuts: **Help > Show Keyboard Shortcuts** (JupyterLab).

### Magic commands

Lines that start with `%` (one line) or `%%` (the whole cell) are commands of the
notebook, not Python ([IPython magics](https://ipython.readthedocs.io/en/stable/interactive/magics.html)):

| Magic | What it does |
|---|---|
| `%pip install seaborn` | installs a package into the kernel's environment |
| `%timeit sum(range(1000))` | measures how long a line takes |
| `%%time` | measures the whole cell |
| `%%html` | the cell is HTML (for example an embedded video) |
| `!dir` (Windows), `!ls` | runs a command of the system |

### Script or notebook?

| Notebook | Script (`.py`) |
|---|---|
| exploring data, trying ideas | a job that runs again and again |
| results with tables and charts next to the code | runs from the terminal or a scheduler |
| sharing an analysis with text | easy to review and version in Git |

Often both: explore in a notebook, then move the finished code into a script.

## 8. The structure of a program

### Statements, one per line

A program is a list of **statements**, run **from top to bottom**. In Python:

- a statement ends at the **end of the line** - no `;` as in SQL and SAS (you *can*
  put `;` between two statements on one line, but nobody does);
- a long statement continues on the next line while a bracket `(`, `[` or `{` is
  open (or after a `\` at the end of the line - avoid it);
- an **expression** is a piece of code that gives a value: `42`, `rate`,
  `outstanding * rate / 100`.

```python run
outstanding = 1044231.30
rate = 8.83
yearly_interest = (outstanding
                   * rate
                   / 100)
print(yearly_interest)
```

### Indentation makes the blocks

SAS has `do; ... end;`, SQL has `BEGIN ... END`. In Python a **block** - the lines
that belong to an `if`, a loop or a function - is the lines **indented** under a line
that ends with `:`. The indentation is not decoration: it **is** the syntax.

The same task - the sum and the product of four numbers - in SAS and in Python:

```sas
data _null_;
    total = 0;
    product = 1;
    do i = 1 to 4;
        total = total + i;
        product = product * i;
    end;
    put total= product=;
run;
```

```python run
numbers = [1, 2, 3, 4]
product = 1

for i in numbers:
    product = product * i      # inside the loop: indented

total = sum(numbers)
print(total, product)
```

(Loops are the topic of session 2.) More side-by-side examples of languages:
[rosettacode.org](https://rosettacode.org/wiki/Category:Programming_Tasks).

Rules:

- use **4 spaces** per level ([PEP 8](https://peps.python.org/pep-0008/#indentation));
  VS Code inserts 4 spaces when you press `Tab` in a `.py` file;
- all lines of one block have the **same** indentation;
- never mix tabs and spaces - Python stops with `TabError: inconsistent use of tabs
  and spaces in indentation`.

An indentation where none is expected:

```python run
loan_id = "L000001"
    stage = 1
print(loan_id, stage)
```

`IndentationError: unexpected indent` - and nothing runs, not even the first line
(the syntax is checked before the program starts, section 3).

A wrong indentation can also give no error at all - only a wrong result. Find the
bug:

```python run
days_past_due = 120

if days_past_due > 90:
    print("*" * 5)
    print("Non-performing")
else:
    print("-" * 5)
print("Performing")
```

::: details Answer
`print("Performing")` is not indented, so it is not part of the `else` block: it
runs always, also for a loan 120 days past due. It needs 4 spaces in front.
:::

### Comments

Everything after `#` up to the end of the line is a **comment**: Python ignores it.

```python run
# The report date of the sample data
report_date = "2026-09-30"

stage = 3          # 1, 2 or 3 (IFRS 9)
# print("not run")
print(report_date, stage)
```

Comments are for people:

- explain **why**, not what - the code already says what;
- a short description at the top of a file: what it does, its input, its output;
- to switch off lines while you look for a bug (`Ctrl+/` in VS Code).

SAS has `/* ... */` and `* ... ;`, SQL has `--` and `/* ... */`. Python has only `#`
(a text in triple quotes is sometimes used for longer notes - more in session 4).
Style: [PEP 8 - Comments](https://peps.python.org/pep-0008/#comments).

### `print()`: show values

[`print()`](https://docs.python.org/3/library/functions.html#print) writes values to
the screen, separated by spaces, and ends with a new line. Two options change that:
`sep` (the separator) and `end` (what comes at the end).

```python run
print("L000001", "investment", 1044231.30)
print("L000001", "investment", 1044231.30, sep=";")
print("2026", "09", "30", sep="-")

print("Loading", end="")
print("...", end="")
print(" done")
print()            # an empty line
print("end")
```

### `input()`: ask the user

[`input()`](https://docs.python.org/3/library/functions.html#input) shows a message,
waits for the user to type a line and press `Enter`, and returns what was typed - always
as **text** (`str`), even when the user types a number. Convert it yourself (section
12):

```python
amount_text = input("Amount: ")          # the user types 2500
print(type(amount_text))                 # <class 'str'>
amount = float(amount_text)
print("Amount with 10% fee:", amount * 1.1)
```

`input()` does not work on this site - try it in VS Code (`python file.py`) or in a
notebook. In analysis work you seldom need it: the data comes from files and
databases.

### Escape sequences

Inside a string, a backslash `\` starts an **escape sequence** - a character you
cannot type directly:

| Sequence | Result |
|---|---|
| `\n` | a new line |
| `\t` | a tab |
| `\'` | `'` |
| `\"` | `"` |
| `\\` | one `\` |

```python run
print("line 1\nline 2")
print("L000001\tinvestment\t1044231.30")
print('Client\'s rating')
print("Client's rating")          # or simply use the other quotes
print("C:\\data\\loans.csv")
```

Windows paths are a trap: in `"C:\new\table.csv"`, `\n` is a new line and `\t` is a
tab. Write the path with `\\`, with `/` (Python accepts it on Windows too), or as a
**raw string** `r"..."`, where `\` is just a character:

```python run
print("C:\new\table.csv")         # wrong
print(r"C:\new\table.csv")        # right: a raw string
print("C:/new/table.csv")         # right: forward slashes
```

All escape sequences:
[String and bytes literals](https://docs.python.org/3/reference/lexical_analysis.html#escape-sequences).
Since Python 3.12 an unknown escape like `"\d"` gives a `SyntaxWarning`.

## 9. Values and types

Every value in Python has a **type**. The type decides what the value can do:
`1 + 2` adds numbers, `"1" + "2"` joins texts.

```python run
print(1 + 2)
print("1" + "2")
print(3 * 4)
print(3 * "4")
print(True + True)
```

The basic types:

| Type | Values | SQL | SAS |
|---|---|---|---|
| `int` | whole numbers: `42`, `-7`, `1_000_000` | `INTEGER`, `BIGINT` | numeric |
| `float` | numbers with a fraction: `8.83`, `0.0005`, `1.5e-3` | `FLOAT`, `DOUBLE` | numeric (it is a float) |
| `str` | text: `"EUR"`, `'L000001'` | `VARCHAR`, `CHAR` | character |
| `bool` | `True`, `False` | `BOOLEAN`, `BIT` | 1 / 0 |
| `NoneType` | `None` - "no value" | `NULL` | missing (`.`, `" "`) |

`type()` gives the type of a value:

```python run
for value in [42, 8.83, "EUR", True, None]:
    print(repr(value), type(value).__name__)
```

### Everything is an object

In Python every value - a number, a text, `True`, even a function - is an
**object**: a piece of memory that knows its **type** and its **value**. That is
why values have methods (functions that belong to them):

```python run
print(type(1))
print(type(1.0004))
print(type("double quotes"), type('single quotes'), type("""triple quotes"""))
print(type([]))
print((8.83).is_integer())
print("eur".upper())
```

### `int` - whole numbers

```python run
print(42, +42, -42)
print(1_000_000 + 2_000_000)     # _ only makes long numbers readable
print(2 ** 100)                  # no limit on the size
```

A Python `int` has no maximum: it grows as needed. (SQL `INTEGER` stops at about 2.1
billion, `BIGINT` at 9.2 * 10**18.)

### `float` - numbers with a fraction

```python run
print(3.1234, -0.255)
print(.44, -.55)                 # the 0 in front may be left out
print(1.5e-3)                    # scientific notation: 1.5 * 10**-3
print(0.00005)                   # very small numbers are shown that way
print(1044231.30)                # the trailing 0 is not kept
```

A `float` is a binary floating-point number of 64 bits (IEEE 754 "double") - exactly
the same as a SAS numeric value. It has about 15 - 17 significant digits. Most
decimal fractions cannot be stored exactly - section 14 shows what that means for
money.

Python also has `complex` numbers (`3 + 4j`), for engineering and science; you will
not need them in this course.

### `str` - text

A string is a **sequence of characters** (Unicode - Cyrillic works too), in single or
double quotes - there is no difference. Triple quotes `"""..."""` or `'''...'''` allow
several lines:

```python run
product = "investment"
region = 'Пловдив'
note = """The loan was restructured
in March 2026."""
print(product, region)
print(note)
print(len(region))                # the number of characters
```

A string in single quotes cannot continue on the next line:

```python run
note = 'The loan was restructured
in March 2026.'
```

### `bool` - `True` and `False`

The result of a comparison is a `bool`. Note the capital letters: `True`, `False`.

```python run
days_past_due = 120
is_late = days_past_due > 0
is_non_performing = days_past_due > 90
print(is_late, is_non_performing)
print(type(is_late))
```

A `bool` is a kind of `int`: `True` is `1` and `False` is `0`. So you can count with
it - like `sum(dpd > 90)` in SAS SQL:

```python run
print(True + True + False)
print(sum([120 > 90, 35 > 90, 200 > 90]))   # how many are over 90
```

### `None` - no value

`None` means "no value (yet)" - like `NULL` in SQL and a missing value in SAS.

```python run
industry = None             # retail clients have no industry code
print(industry)
print(industry is None)     # the right way to test for None
print(type(industry))
```

::: warning `None` is not `NULL`
In SQL, `NULL = NULL` is not true, and you must write `IS NULL`. In SAS, a missing
`.` is smaller than every number, so `if x < 0` is true for missing values. In
Python, `None == None` is `True`, and `None < 0` is an error. Test with
`x is None`. (pandas has its own missing values, `NaN` and `NA` - session 14.)
:::

## 10. Variables

### A name for a value

A **variable** is a **name** for a value. The **assignment** `=` evaluates the
expression on the right and gives the result a name:

```python run
loan_id = "L000001"
outstanding = 1044231.30
rate = 8.83

interest = outstanding * rate / 100
print(loan_id, interest)
```

- There is no declaration: a variable exists from its first assignment (unlike SAS
  `LENGTH` or a SQL `DECLARE`).
- A name you have not assigned is an error:

```python run
outstanding = 1044231.30
print(outstandng)
```

### Names, not boxes

In many languages a variable is a box that holds a value. In Python it is more
exact to say: the value is an **object** in memory, and the variable is a **name**
(a label) **bound** to that object. Assignment binds a name to an object;
`id()` gives the identity of the object (in CPython, its memory address):

```python run
x = 5
y = x            # y is bound to the same object as x
print(id(x), id(y))

x = 3            # x is bound to a new object; y still to 5
print(x, y)
print(id(x), id(y))
```

A new assignment does not change the old object: it moves the name to a new one.
An object that has no name any more is deleted automatically by the **garbage
collector** - you never free memory yourself.

::: info Animation
**Names and objects:**
[1. A name and an object](../animations/namesAndObjects.html#1){target="_blank"},
[2. A new value](../animations/namesAndObjects.html#2){target="_blank"},
[3. Two names, one object](../animations/namesAndObjects.html#3){target="_blank"}
:::

### Dynamic typing

The **type belongs to the object**, not to the name. The same name can be bound to
an `int` now and to a `str` later:

```python run
value = 42
print(type(value))
value = "42"
print(type(value))
```

In SAS, the type of a variable is fixed in the DATA step; in SQL, the type of a
column is fixed in the table. Python checks types only when the code runs - a
mistake shows up as a `TypeError` at that line. Keep one type per name: it makes the
code easier to read. (*Type hints*, like `rate: float = 8.83`, document the intended
type - session 4.)

::: info Animation
**Names and objects:** [5. Types belong to objects](../animations/namesAndObjects.html#5){target="_blank"}
:::

### Rules for names

Otherwise: `SyntaxError`.

- letters, digits and `_`; no spaces, no `-`;
- must not start with a digit;
- must not be a **keyword** (`if`, `for`, `class`, `None`, `True`, ...);
- names are **case-sensitive**: `rate`, `Rate` and `RATE` are three different
  names - not like SAS and SQL, where case does not matter.

```python run
import keyword

print(keyword.kwlist)      # the words you cannot use as names
```

```python run
first_name = "Ada"
print(first_Name)          # NameError: a different name
```

```python run
sur-name = "Byron"         # SyntaxError: "-" is minus
```

### Naming conventions (PEP 8)

[PEP 8](https://peps.python.org/pep-0008/#naming-conventions) is the style guide of
Python. For names:

| What | Style | Example |
|---|---|---|
| variables, functions | `snake_case`: small letters, words joined with `_` | `days_past_due`, `client_since` |
| constants (values that do not change) | `UPPER_SNAKE_CASE` | `REPORT_DATE = "2026-09-30"` |
| classes (session 11) | `CapWords` | `Loan`, `RatingScale` |

- Names that say what is inside: `outstanding`, not `x` or `data2`.
- Booleans as a question: `is_late`, `has_collateral`.
- `camelCase` (`daysPastDue`) is used only in old code that already has it.
- Python has no real constants: `UPPER_CASE` only tells other people "do not change
  this".
- Python allows Cyrillic letters in names, but write names in English.

### Assignment, in more forms

```python run
# several names at once
loan_id, stage = "L000001", 1
print(loan_id, stage)

# the same value for several names
x = y = 0
print(x, y)

# swap two values - no helper variable needed
a, b = 10, 20
a, b = b, a
print(a, b)
```

**Augmented assignment** changes a variable using its old value:

| Statement | Means |
|---|---|
| `total += 100` | `total = total + 100` |
| `total -= 100` | `total = total - 100` |
| `total *= 2` | `total = total * 2` |
| `total /= 2` | `total = total / 2` |
| `total //= 2`, `total %= 2`, `total **= 2` | the same with `//`, `%`, `**` |

```python run
total = 0
total += 1044231.30
total += 651927.30
total += 644.25
print(total)
```

`del name` removes a name (the object goes away when no name points to it):

```python run
temp = 42
del temp
print(temp)       # NameError
```

::: info Animation
**Names and objects:**
[4. `x = x + 1`](../animations/namesAndObjects.html#4){target="_blank"},
[6. Several names at once](../animations/namesAndObjects.html#6){target="_blank"},
[7. `is` and `==` (advanced)](../animations/namesAndObjects.html#7){target="_blank"}
:::

## 11. Numbers and operators

### Arithmetic operators

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+` | add | `7 + 2` | `9` |
| `-` | subtract | `7 - 2` | `5` |
| `*` | multiply | `7 * 2` | `14` |
| `/` | divide - always a `float` | `7 / 2` | `3.5` |
| `//` | floor division: the whole part, rounded down | `7 // 2` | `3` |
| `%` | modulo: the remainder | `7 % 2` | `1` |
| `**` | power | `7 ** 2` | `49` |
| `-x` | minus | `-7` | `-7` |

```python run
print(5 - 3, 5 * 3, 5 / 3, 5 // 3, 5 % 3, 5 ** 3)
print(6 / 3)              # a float, even when it divides exactly
print(type(6 / 3))
print(2 + 3.0)            # int and float give a float
```

`//` and `%` together split a number into units. 125 days past due are how many
months of 30 days, and how many days more?

```python run
days_past_due = 125
months = days_past_due // 30
days = days_past_due % 30
print(months, "months and", days, "days")
print(divmod(days_past_due, 30))      # both at once
```

::: warning Python 2 division
In Python 2, `5 / 3` was `1` (like `//` now). In Python 3 it is `1.6666666666666667`.
If old code divides whole numbers, check which one it meant.
:::

::: details Advanced: `//` and `%` with negative numbers
`//` rounds **down**, towards minus infinity: `-7 // 2` is `-4`, not `-3`, and
`-7 % 2` is `1`. SAS `INT()` and `int()` in Python cut the fraction towards zero:
`int(-3.5)` is `-3`. For negative values, check which one you need.

```python run
print(-7 // 2, -7 % 2, int(-7 / 2))
```
:::

### Order of operations

As in mathematics and in SQL:

| Priority | Operators |
|---|---|
| 1 (first) | `( )` |
| 2 | `**` |
| 3 | `-x` (minus) |
| 4 | `*`, `/`, `//`, `%` |
| 5 | `+`, `-` |
| 6 | comparisons: `==`, `!=`, `<`, `<=`, `>`, `>=` |
| 7 | `not` |
| 8 | `and` |
| 9 (last) | `or` |

Operators of the same priority run from left to right - except `**`, which runs
from right to left. When in doubt, add brackets: they also make the code easier to
read.

```python run
print(1000 + 2000 * 0.05)       # 1100.0
print((1000 + 2000) * 0.05)     # 150.0
print(-2 ** 2)                  # -4: ** comes before the minus
print(2 ** 3 ** 2)              # 512: 3 ** 2 first
```

::: info Animation
**How an expression is evaluated:**
[1. Precedence](../animations/expressionEvaluation.html#1){target="_blank"},
[2. Brackets](../animations/expressionEvaluation.html#2){target="_blank"},
[3. `**` and minus](../animations/expressionEvaluation.html#3){target="_blank"},
[4. `//` and `%`](../animations/expressionEvaluation.html#4){target="_blank"}
:::

### Comparison operators

| Python | SQL | SAS | Meaning |
|---|---|---|---|
| `==` | `=` | `=`, `EQ` | equal |
| `!=` | `<>`, `!=` | `^=`, `NE` | not equal |
| `<`, `<=` | `<`, `<=` | `<`, `<=` (`LT`, `LE`) | less (or equal) |
| `>`, `>=` | `>`, `>=` | `>`, `>=` (`GT`, `GE`) | greater (or equal) |

`=` gives a name, `==` compares. The result is a `bool`. Comparisons can be
**chained** - like `BETWEEN` in SQL:

```python run
days_past_due = 45
print(days_past_due == 0)
print(days_past_due != 0)
print(30 < days_past_due <= 90)      # the same as 30 < dpd and dpd <= 90
print("EUR" == "eur")                # texts: case matters
```

### Logical operators

`and`, `or` and `not` combine conditions - in small letters, as words:

```python run
days_past_due = 45
rating = 10
print(days_past_due > 90 or rating == 10)     # stage 3?
print(days_past_due > 0 and rating < 5)
print(not days_past_due > 90)
```

::: warning `&` and `|` are not `and` and `or`
In SAS, `&` and `|` mean AND and OR. In Python they are different (bit) operators.
pandas uses them for conditions on whole columns (session 15) - but for single
values, write `and`, `or`, `not`.
:::

`if` with conditions, and the details of `and` / `or`, come in session 2.

::: info Animation
**How an expression is evaluated:**
[5. Chained comparisons](../animations/expressionEvaluation.html#5){target="_blank"},
[6. `and` / `or`](../animations/expressionEvaluation.html#6){target="_blank"}
:::

### Operators on strings

`+` joins two strings (like `||` in SQL and SAS), and `*` repeats a string:

```python run
print("ala" + "bala")
print("1" + "2")
print("-" * 30)
print("ab" * 3)
```

Python does not mix types for you - "apples with oranges" is an error:

```python run
print("Stage " + 3)
```

```python run
print("ab" * "3")
```

The fix is an explicit conversion, `"Stage " + str(3)` (section 12), or an f-string
(section 13).

::: info Animation
**How an expression is evaluated:** [7. Mixed types](../animations/expressionEvaluation.html#7){target="_blank"}
:::

### A first look at string methods

Strings have many **methods** - functions you call with a dot after the value.
A few, for a first look (session 7 has them all):

```python run
print("ada".capitalize())
print("alabala".count("a"))
print("Alabala".count("a"))        # "A" is not "a"
print("AlabAla".find("a"))          # the position of the first "a", from 0
print("alabala".replace("a", "o"))
print("L000001,C0080,investment".split(","))
print("  EUR ".strip())
```

Reference: [String methods](https://docs.python.org/3/library/stdtypes.html#string-methods).

### Built-in functions for numbers

Ready to use, without `import`:

```python run
print(abs(2 - 5))
print(max(1, 2, 3), min(1, 2, 3))
print(round(2.51), round(2.49))
print(round(8.8349, 2))
print(sum([1044231.30, 651927.30, 644.25]))
print(pow(2, 10))
```

`round()` has a surprise for people from SAS and SQL - see section 14.

### The `math` module

More functions are in the [`math`](https://docs.python.org/3/library/math.html) module.
Import it once, at the top of the file:

```python run
import math

print(math.sqrt(16))
print(math.pi)
print(math.floor(2.9), math.ceil(2.1))     # down, up
print(math.floor(-2.5), math.ceil(-2.5))
print(math.pow(2, 3))                      # always a float (2 ** 3 is an int)
print(math.log(100, 10), math.exp(1))
```

On the portfolio: the PD of a rating from a score with the logistic function, and
the expected loss `EL = PD * LGD * EAD`:

```python run
import math

score = -4.2
pd_value = 1 / (1 + math.exp(-score))     # the logistic function
lgd = 0.45
ead = 1044231.30

expected_loss = pd_value * lgd * ead
print(pd_value)
print(round(expected_loss, 2))
```

(`pd` is the usual short name for pandas, so the variable is `pd_value`.)

## 12. Converting between types

### The functions

The name of a type is also a function that **converts** a value to it:

| Function | Gives | Examples |
|---|---|---|
| `int(x)` | an `int` | `int("42")` -> `42`, `int(3.99)` -> `3` (cuts, does not round) |
| `float(x)` | a `float` | `float("8.83")` -> `8.83`, `float(5)` -> `5.0` |
| `str(x)` | a `str` | `str(1044231.3)` -> `"1044231.3"` |
| `bool(x)` | a `bool` | `bool(0)` -> `False`, `bool("no")` -> `True` |

![The four basic types and the conversions between them, with examples and the conversions that fail](/diagrams/type-conversions.svg){.diagram}

### Text to numbers

Data from files, `input()`, Excel exports and the web often comes as **text**. A
row of `loans.csv`, before any conversion, is only a string:

```python run
row = "L000002,C0132,investment,EUR,2019-04-16,2029-04-16,1977400.00,651927.30,5.44,35,2"
print(row.split(","))
```

Each piece is a `str`. You cannot calculate with them before you convert them:

```python run
outstanding_text = "651927.30"
rate_text = "5.44"
days_text = "35"

outstanding = float(outstanding_text)
rate = float(rate_text)
days_past_due = int(days_text)

print(outstanding * rate / 100)
print(days_past_due > 30)
```

What `int()` and `float()` accept, and what not:

```python run
print(int("42"), int(" 42 "), int("0042"), int("-7"), int("1_000"))
print(float("8.83"), float("1e3"), float(" 5 "))
```

```python run
print(int("3.5"))       # ValueError: not a whole number - use int(float("3.5"))
```

```python run
print(float("1 044 231,30"))     # ValueError: Bulgarian format
```

Numbers written the Bulgarian way - a space between the thousands, a comma for the
fraction - must be cleaned first (more string methods in session 7):

```python run
text = "1 044 231,30"
clean = text.replace(" ", "").replace(",", ".")
print(clean, float(clean))
```

::: warning SAS converts, Python does not
SAS converts `"5"` to `5` by itself and writes a NOTE to the log. Python never
converts text to numbers by itself: `"5" + 5` is a `TypeError`. That is "explicit is
better than implicit" - you will not get a silent wrong number.
:::

### Between numbers

```python run
print(float(5))          # 5.0
print(int(3.99))         # 3: int() cuts the fraction
print(int(-3.99))        # -3: towards zero
print(round(3.99))       # 4: round() rounds
print(2 + 3.5)           # int + float: the int becomes a float by itself
```

Python converts automatically only where nothing is lost: `int` to `float` in an
expression with a `float`, and `bool` to `int` (`True + 1` is `2`).

### Numbers to text

```python run
outstanding = 1044231.30
print(str(outstanding))              # the trailing 0 is lost
print("Outstanding: " + str(outstanding))
print(f"Outstanding: {outstanding:.2f}")   # better: an f-string, section 13
```

### To `bool`: truthy and falsy

`bool()` gives `False` for "empty" values and `True` for everything else:

| `False` (falsy) | `True` (truthy) |
|---|---|
| `0`, `0.0` | every other number, also `-1` |
| `""` (an empty string) | every non-empty string, also `"0"`, `"False"`, `" "` |
| `None` | |
| empty collections: `[]`, `{}` | non-empty collections |

```python run
print(bool(0), bool(0.0), bool(""), bool(None))
print(bool(-1), bool("0"), bool("False"), bool(" "))
```

`bool("False")` is `True`! To read "yes" / "no" or "True" / "False" from a file,
compare the text:

```python run
restructured_text = "False"
restructured = restructured_text == "True"
print(restructured, type(restructured))
```

## 13. Strings and f-strings

### Joining is hard to read

```python run
client_id = "C0080"
product = "investment"
outstanding = 1044231.30

print("Client " + client_id + ", product " + product + ", outstanding " + str(outstanding) + " EUR")
```

### f-strings

An **f-string** has an `f` before the quotes. Inside it, `{ }` hold any Python
expression; its value is put into the text:

```python run
client_id = "C0080"
product = "investment"
outstanding = 1044231.30
rate = 8.83

print(f"Client {client_id}, product {product}, outstanding {outstanding} EUR")
print(f"Yearly interest: {outstanding * rate / 100}")
print(f"{client_id=}")              # name=value, for checking values
```

Several lines, with triple quotes:

```python run
loan_id = "L000001"
stage = 1
print(f"""Loan:  {loan_id}
Stage: {stage}
Late:  {stage > 1}""")
```

### Formatting the values

After a `:` inside the `{ }` comes a **format specification** - like a SAS format:

| f-string | Result | SAS format |
|---|---|---|
| `f"{1044231.3:.2f}"` | `1044231.30` | `12.2` |
| `f"{1044231.3:,.2f}"` | `1,044,231.30` | `COMMA12.2` |
| `f"{0.0883:.2%}"` | `8.83%` | `PERCENT8.2` |
| `f"{7:03d}"` | `007` | `Z3.` |
| `f"{0.00049:.2e}"` | `4.90e-04` | `E8.` |
| `f"{1044231.3:>15,.2f}"` | `   1,044,231.30` (15 characters, right) | width `15.` |
| `f"{'EUR':<6}"` | `EUR   ` (6 characters, left) | `$6.` |
| `f"{'EUR':^9}"` | `   EUR   ` (centred) | |
| `f"{'EUR':*^9}"` | `***EUR***` (filled with `*`) | |

```python run
outstanding = 1044231.3
pd_value = 0.0049
day = 5

print(f"{outstanding:.2f}")
print(f"{outstanding:,.2f}")
print(f"{pd_value:.2%}")
print(f"Day of the month: {day:02d}")
print(f"--->{123:>10}<---")
print(f"--->{123:^10}<---")
print(f"--->{123:*^10}<---")

precision = 3
print(f"{12.34567:.{precision}f}")      # the format from a variable
```

The pattern is `{value:[fill][align][width][,][.precision][type]}`: align `<` left,
`>` right, `^` centre; type `d` whole number, `f` fixed point, `%` percent, `e`
scientific. All options: [Format Specification Mini-Language](https://docs.python.org/3/library/string.html#formatspec).

The Bulgarian way - a space between the thousands and a comma for the fraction - is
two replacements away:

```python run
outstanding = 1044231.3
text = f"{outstanding:,.2f}"
print(text.replace(",", " ").replace(".", ","))
```

### A small report

Fixed widths make columns:

```python run
print(f"|{'=' * 10}|{'=' * 10}|")
print(f"|{1:>10}|{1:<10}|")
print(f"|{23:>10}|{23:<10}|")
print(f"|{456:>10}|{456:<10}|")
print(f"|{'=' * 10}|{'=' * 10}|")
```

The same with loans:

```python run
print(f"{'loan':<10}{'product':<13}{'outstanding':>15}{'rate':>8}")
print("-" * 46)
print(f"{'L000001':<10}{'investment':<13}{1044231.30:>15,.2f}{0.0883:>8.2%}")
print(f"{'L000002':<10}{'investment':<13}{651927.30:>15,.2f}{0.0544:>8.2%}")
print(f"{'L000003':<10}{'credit_card':<13}{644.25:>15,.2f}{0.0479:>8.2%}")
```

### Older ways you will meet

Code written before f-strings (Python 3.6, 2016) uses `str.format()` or `%`. Read
them; write f-strings.

```python run
name, year = "Ada Byron", 1852

print("{} died in {}".format(name, year))          # str.format()
print("{1} died in {0}".format(year, name))        # by position
print("{:>10.2f}|".format(3.14159))                # the same format specification

print("%s died in %d" % (name, year))              # %-formatting, the oldest
print("%.2f" % 3.14159)
```

## 14. Floats, rounding and `Decimal`

### Why `0.1 + 0.2` is not `0.3`

```python run
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(f"{0.1:.30f}")
```

A `float` is stored in **binary**. Like 1/3 = 0.333... in decimal, 1/10 has no
end in binary: it is cut after 53 binary digits, so `0.1` in memory is a tiny bit
more than 0.1. Usually you do not see it, because `print()` shows the shortest
text that gives the same number. In sums of many values the small errors add up.
Read more: [Floating Point Arithmetic: Issues and Limitations](https://docs.python.org/3/tutorial/floatingpoint.html).

SAS has the same floats and the same effect - you may know it from comparisons
that need `ROUND(x, 0.01)` or a "fuzz".

Compare floats with a tolerance, not with `==`:

```python run
import math

print(math.isclose(0.1 + 0.2, 0.3))
print(abs((0.1 + 0.2) - 0.3) < 1e-9)
```

### `round()` rounds half to even

```python run
print(round(0.5), round(1.5), round(2.5), round(3.5))
print(round(2.675, 2))
```

- `round()` rounds a 5 to the **even** neighbour: `round(2.5)` is `2`. This is
  "banker's rounding" - it does not push sums up. SAS `ROUND`, and SQL `ROUND` on
  `DECIMAL` / `NUMERIC` values, round a 5 **away from zero** (`2.5` -> `3`).
- `round(2.675, 2)` gives `2.67`, because `2.675` in binary is a tiny bit less
  than 2.675.

For results that must match SAS, SQL or the accounting system to the cent, use
`Decimal`.

### `Decimal`: exact decimal numbers

The [`decimal`](https://docs.python.org/3/library/decimal.html) module of the
standard library calculates in **decimal**, like a person on paper - the same as
`DECIMAL(18, 2)` / `NUMERIC` in SQL.

```python run
from decimal import Decimal

print(0.1 + 0.2)
print(Decimal("0.1") + Decimal("0.2"))
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
```

Create a `Decimal` **from a string**. From a float, it takes over the float's error -
and shows the exact value the float really has:

```python run
from decimal import Decimal

print(Decimal("0.1"))
print(Decimal(0.1))
```

### Rounding money with `quantize`

`quantize()` rounds to the places of the given value; `rounding` says how.
`ROUND_HALF_UP` is the rounding of SAS, SQL and the schoolbook:

```python run
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

cent = Decimal("0.01")

print(Decimal("2.675").quantize(cent, rounding=ROUND_HALF_UP))     # 2.68
print(round(2.675, 2))                                             # float: 2.67

print(Decimal("2.665").quantize(cent, rounding=ROUND_HALF_UP))     # 2.67: 5 goes up
print(Decimal("2.665").quantize(cent, rounding=ROUND_HALF_EVEN))   # 2.66: 5 goes to even
```

The yearly interest of three loans, to the cent:

```python run
from decimal import Decimal, ROUND_HALF_UP

cent = Decimal("0.01")
total = Decimal("0")

for outstanding, rate in [("1044231.30", "8.83"), ("651927.30", "5.44"), ("644.25", "4.79")]:
    interest = Decimal(outstanding) * Decimal(rate) / 100
    interest = interest.quantize(cent, rounding=ROUND_HALF_UP)
    print(interest)
    total += interest

print("Total:", total)
```

Rules for `Decimal`:

- `Decimal` with `int` works; `Decimal` with `float` is a `TypeError` - convert the
  float with `Decimal(str(x))`.
- The result of a division has up to 28 significant digits (the default
  *precision*); round it with `quantize()` when you need cents.
- `Decimal` is slower than `float`. Use it for **money that must add up** to the
  cent: balances, interest, reconciliations with the general ledger. For rates, PDs,
  statistics and models, `float` is right.
- pandas works with `float`: there, round the **results** (session 15).

```python run
from decimal import Decimal

print(Decimal("100.50") * 2)
print(Decimal("100.50") * 1.1)      # TypeError: Decimal and float
```

## 15. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework) in VS Code (first time: see [How to use these pages](/how-to#practice-and-homework); before the session: `git pull upstream main`) and run the tasks from the terminal, in the repository root:

```bash
python 01-intro-syntax-types/practice/task1-first-values.py
```

Each file explains the task at the top. Write your code between the
`your code` lines; the checks at the bottom print `OK` or `FAIL`.

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-first-values.py` | Variables and types for one loan |
| 2 | `task2-predict-types.py` | Predict the value and the type of 14 expressions, then check |
| 3 | `task3-calculations.py` | The length of this course in hours; days past due in months and days; interest |
| 4 | `task4-convert-text.py` | Convert the text fields of a CSV row, also a number in Bulgarian format |
| 5 | `task5-fstrings.py` | Format amounts, percents and ids; a report line with fixed widths |
| 6 | `task6-decimal.py` | Interest to the cent with `Decimal`, rounded the SAS way |

In `task2-predict-types.py`, replace each `"?"` with your prediction **before**
you run the file - the point is to think first.

## Summary

| Topic | Remember |
|-------|----------|
| Python | a free, general-purpose language; CPython; a new version every October; you use 3.12 / 3.13 |
| How it runs | syntax check -> bytecode -> the Python virtual machine; a `SyntaxError` stops everything before the first line |
| Project setup | `py -m venv .venv`, activate, `pip install -r requirements.txt`; one venv per project |
| Running code | `python file.py` in the terminal; the REPL `>>>`; Jupyter notebooks (the kernel keeps the variables) |
| Syntax | one statement per line; blocks by indentation (4 spaces); comments with `#` |
| Types | `int`, `float`, `str`, `bool`, `None`; `type(x)`; everything is an object |
| Variables | a name bound to an object; `=` binds; the type belongs to the object; `snake_case` |
| Operators | `+ - * / // % **`; `/` gives a float; `== != < <= > >=`; `and or not` |
| Conversions | `int()`, `float()`, `str()`, `bool()`; text never becomes a number by itself; `bool("False")` is `True` |
| f-strings | `f"{x:,.2f}"`, `f"{p:.2%}"`, `f"{n:05d}"`, `f"{s:<10}"`, `f"{x=}"` |
| Money | floats are binary: `0.1 + 0.2 != 0.3`; `round()` rounds half to even; `Decimal("...")` + `quantize(..., ROUND_HALF_UP)` |

## Homework

1. `01-intro-syntax-types/homework.py` (in the homework repository): a **loan card** -
   convert the text fields of one loan, calculate the repaid share, the interest
   and the monthly payment, and print the card. Every check must print `OK`.
2. The practice tasks you did not finish in class - recommended, the next tasks
   build on them.
3. Optional: write `payment.py`, which asks for the amount, the yearly rate in
   percent and the number of years with `input()`, and prints the monthly payment
   (the formula is in `homework.py`), formatted with two decimals and a thousands
   separator. Run it in the terminal.
4. Optional: create a notebook `01-practice.ipynb` in your Homework folder, read
   `data/loans.csv` with pandas (as at the top of this page), and show
   `loans.head()` and `loans.describe()`.

## Read more

- Python: [the official tutorial](https://docs.python.org/3/tutorial/), chapters 1 - 3;
  [Built-in types](https://docs.python.org/3/library/stdtypes.html);
  [Built-in functions](https://docs.python.org/3/library/functions.html)
- Style: [PEP 8](https://peps.python.org/pep-0008/)
- Setup: [Virtual environments and packages](https://docs.python.org/3/tutorial/venv.html),
  [Installing packages](https://packaging.python.org/en/latest/tutorials/installing-packages/),
  [Using Python on Windows](https://docs.python.org/3/using/windows.html)
- VS Code: [Python in VS Code](https://code.visualstudio.com/docs/languages/python),
  [Jupyter notebooks in VS Code](https://code.visualstudio.com/docs/datascience/jupyter-notebooks),
  [Tips and tricks](https://code.visualstudio.com/docs/editing/getting-started/tips-and-tricks),
  [VS Code - setup and basics (video)](https://www.youtube.com/watch?v=SYRwSyjD8oI),
  [the default terminal: cmd instead of PowerShell](https://code.visualstudio.com/docs/terminal/profiles)
- Jupyter: [Project Jupyter](https://jupyter.org/),
  [Jupyter documentation](https://docs.jupyter.org/en/latest/),
  [JupyterLab documentation](https://jupyterlab.readthedocs.io/en/stable/)
- Formatting: [f-strings in the tutorial](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals),
  [Format Specification Mini-Language](https://docs.python.org/3/library/string.html#formatspec)
- Numbers: [Floating point arithmetic](https://docs.python.org/3/tutorial/floatingpoint.html),
  [decimal](https://docs.python.org/3/library/decimal.html),
  [math](https://docs.python.org/3/library/math.html)
- Videos for later: [NumPy for beginners (SciPy 2018)](https://www.youtube.com/watch?v=V0D2mhVt7NE),
  [JupyterLab - get started](https://jupyterlab.readthedocs.io/en/stable/getting_started/overview.html)
  (the documentation)

**Next session:** conditional statements and loops - `if` / `elif` / `else`, the
Python `CASE WHEN`, and `for` / `while` loops over the rows of a file.
