# How to use these pages

## Run the examples

Most code examples have a bar under them:

- **Run** executes the code in your browser and shows what it prints. Like in a
  Jupyter notebook, the value of the last line is shown too.
- **Edit** turns the example into an editor. Change the code and press **Run**
  again (or `Ctrl+Enter`).
- **Reset** brings back the original code.

Try it:

```python run
course = "Python for Data Analysts"
print("Welcome to", course)
len(course)
```

The first **Run** on a page loads Python into the browser and takes a few
seconds; after that it is fast. Examples that use pandas or NumPy load them the
first time too.

Every example runs on its own: a variable from one example does not exist in the
next one. The sample data files are available in every example, in the folder
`data/`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.head()
```

::: info The sample data is made up
All clients, loans and values in it are invented; only the shape is typical of
the data of a bank. What is in each file: [Sample data](./sample-data).
:::

## Set up Python on your computer {#setup}

The tasks and the final project run on your own computer. You need:

| Program | Version | What for |
|---|---|---|
| [Python](https://www.python.org/downloads/windows/) | 3.12 or 3.13, 64-bit | the language |
| [Visual Studio Code](https://code.visualstudio.com/) | latest | the editor, with the extensions below |
| [Git](https://git-scm.com/downloads) | latest | versions of your code; the tasks come with it |
| [GitHub](https://github.com/signup) account | free | your own copy of the tasks |

On Windows, open the [Windows downloads page](https://www.python.org/downloads/windows/),
find the newest **Python 3.13.x** under *Stable Releases* and take **Download Windows
installer (64-bit)** - not the "Python install manager" and not the newest Python
(3.15) at the top. On the first screen of the installer, tick **Add python.exe to
PATH**. Check the tools in a terminal (in VS Code: **Terminal > New Terminal**):

::: code-group
```powershell [Windows]
py --version     # Python 3.12.x or 3.13.x
git --version    # git version 2.x.x
```
```bash [Linux / macOS]
python3 --version     # Python 3.12.x or 3.13.x
git --version         # git version 2.x.x
```
:::

The libraries (pandas, NumPy, ...) are installed into a *virtual environment* in
the Homework folder - see step 8 below.

### VS Code extensions {#vscode-extensions}

| Extension | By | What for | Needed |
|---|---|---|---|
| **Python** | Microsoft | run and debug Python; it installs **Pylance**, **Python Debugger** and **Python Environments** too | required |
| **Jupyter** | Microsoft | notebooks inside VS Code | required |
| **Data Wrangler** | Microsoft | see a DataFrame or a CSV file as a table: sort, filter, statistics per column; it writes the pandas code for the cleaning steps you click | lectures 14 - 16 |
| **Rainbow CSV** | mechatroner | each column of a CSV file in its own colour; SQL-like queries on a CSV file | from lecture 9 |
| **SQLite Viewer** | Florian Klampfer | open a SQLite `.db` file and look at its tables | lecture 13 |
| **Spreadsheet Viewer** | MESCIUS | open `.xlsx` files in VS Code (its old name is *Excel Viewer*) | lectures 9, 14, 16 |

**Install them all at once.** The Homework repository has this list in the file
`.vscode/extensions.json`. When you open the Homework folder in VS Code (step 7
below), VS Code asks *Do you want to install the recommended extensions...?* -
click **Install**. Missed the question? Open the **Extensions** view
(`Ctrl+Shift+X`), type `@recommended` in the search box and click the cloud icon
(**Install Workspace Recommended Extensions**).

To get the same list in another project, create the file `.vscode/extensions.json`
in its folder with this content:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-toolsai.jupyter",
    "ms-toolsai.datawrangler",
    "mechatroner.rainbow-csv",
    "qwtel.sqlite-viewer",
    "GrapeCity.gc-excelviewer"
  ]
}
```

One at a time: search for the name in the **Extensions** view and click
**Install**.

::: info On a company laptop
Some companies block the extension Marketplace or allow only approved extensions.
If **Install** does not work, ask your IT for the extensions in the table.
:::

## Practice and homework in VS Code {#practice-and-homework}

The practice tasks and the homework are in the **Homework repository**:
https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework

Each lecture has a folder there (`01-intro-syntax-types/`, ...) with two kinds of
tasks:

- **Practice tasks** (`practice/task1-....py`, ...): short exercises, one topic
  each, in the order of the lecture. We start them in class. Finish the rest at
  home if you can - later tasks and the final project reuse them.
- **Homework** (`homework.py`): one larger task that puts the topics of the
  lecture together. Do it before the next session - we go through it together at
  the start.

### Set it up once

You do this only once, at the start of the course. It takes about 20 minutes.

**The idea.** A *repository* (or *repo*) is a project folder whose history Git
keeps. In this course you work with three copies of the Homework repository:

```text
  course repository on GitHub             your own repository on GitHub
  (name in Git: upstream)                 (name in Git: origin)
             |                                        ^
             |  git pull upstream main                |  git push
             |  (new tasks)                           |  (your solutions)
             v                                        |
             +------->  the folder on your computer --+
                        (here you write the code)
```

- **`upstream`** is the course repository. Only the trainer can change it. You
  only **pull** from it - this is how you get the new tasks.
- **`origin`** is your own repository. You **push** your solutions to it, so they
  are saved online and you can open them from any computer.

#### 1. Check the tools

See [Set up Python on your computer](#setup) above.

#### 2. Tell Git who you are

Git writes your name and email into every commit (every saved version):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use the same email as in your GitHub account.

#### 3. Create your own repository on GitHub

1. Sign in to https://github.com.
2. Click **+** (top right), then **New repository**.
3. **Repository name**: for example `python-course-homework`.
4. Choose **Private** (only you can see it).
5. Leave everything else as it is: **no** README, **no** `.gitignore`, **no**
   licence. The repository must be **empty** - otherwise step 5 fails.
6. Click **Create repository** and copy the web address GitHub shows, like
   `https://github.com/your-user/python-course-homework.git`.

#### 4. Download the course repository and connect your own

In VS Code, open the folder where you keep the course (**File > Open Folder**),
then open a terminal (**Terminal > New Terminal**) and type the commands one at a
time:

```bash
git clone https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework.git
cd Python-Data-Analysts-UniCredit-Homework
git remote rename origin upstream
git remote add origin https://github.com/your-user/python-course-homework.git
```

In the last command, paste **your** address from step 3.

#### 5. Send everything to your repository (the first push)

```bash
git push -u origin main
```

The first time, GitHub asks you to sign in: choose to sign in with the browser
and allow the access.

#### 6. Check the result

```bash
git remote -v
```

`origin` must show **your** address, `upstream` the course address.

#### 7. Open the folder in VS Code

**File > Open Folder** and choose `Python-Data-Analysts-UniCredit-Homework` (the
folder itself, not the folder above it). Always open this folder when you work on
the tasks: then the terminal starts in the right place.

The first time, VS Code asks if you trust the authors of the folder (click **Yes**)
and offers to install the recommended extensions (click **Install** - see
[VS Code extensions](#vscode-extensions)).

#### 8. Create the virtual environment

In the terminal of VS Code, in the Homework folder:

::: code-group
```powershell [Windows]
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```
```bash [Linux / macOS]
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```
:::

PowerShell says *running scripts is disabled on this system*? Run
`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`, then activate
again (more in [lecture 1](/lectures/01-intro-syntax-types#virtual-environments)).

The prompt now starts with `(.venv)`. In VS Code, choose the interpreter once:
`Ctrl+Shift+P` > **Python: Select Interpreter** > the one in `.venv`. Git ignores
the `.venv` folder.

### Work on a task

Open the terminal (`` Ctrl+` ``) in the repository root and run a task:

```bash
python 01-intro-syntax-types/practice/task1-first-values.py
```

Every task checks your code, prints `OK` or `FAIL` for each check and ends with a
line like `5 of 7 checks passed`.

Save your work in your own repository:

```bash
git add .
git commit -m "Session 1 practice"
git push
```

### Get the new tasks

Before each session, commit your work, then:

```bash
git pull upstream main
```

The new lecture folders appear next to your work. Existing files are not changed,
so there are no conflicts.

## Code from the lessons

The code written during the lessons is in the **Labs repository**:
https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Labs

Clone it once, and after each lesson run `git pull` in it to get the new code. Do
not write your own code there - use the Homework repository for that.

```bash
git clone https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Labs.git
cd Python-Data-Analysts-UniCredit-Labs
git pull          # after each lesson
```

## Find things

- The search box (top left, or `Ctrl+K`) searches all lectures.
- The list on the right side of a lecture ("In this lecture") jumps to a section.
- The moon / sun switch at the top changes between dark and light mode.
- The **EN / BG** button next to it opens the same page in English or in Bulgarian.
- The navigation on the left and the "In this lecture" column on the right can
  be made narrower or wider: drag their inner edge. Double-click the edge to go
  back to the default width.
