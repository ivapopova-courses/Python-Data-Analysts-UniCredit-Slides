---
outline: [2, 3]
---

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

The tasks and the final project run on your own computer. The setup on this page
is for **Windows**, with the Command Prompt (cmd) as the terminal. You need:

| Program | Version | What for |
|---|---|---|
| [Python](https://www.python.org/downloads/windows/) | 3.12 or newer, 64-bit | the language |
| [Visual Studio Code](https://code.visualstudio.com/) | latest | the editor, with the extensions below |
| [Git](https://git-scm.com/downloads) | latest | versions of your code; the tasks come with it |
| [GitHub](https://github.com/signup) account | free | your own copy of the tasks |

Any Python from 3.12 on works: if you already have one, keep it. To install
Python, open the [Windows downloads page](https://www.python.org/downloads/windows/),
find the first version under *Stable Releases* that has a **Download Windows
installer (64-bit)** link, and take it - not the "Python install manager". On the
first screen of the installer, tick **Add python.exe to PATH**. Check the tools in the Command Prompt (in VS Code: **Terminal > New
Terminal**, see [VS Code and the terminal](#terminal)):

```cmd
py --version
git --version
```

You see `Python 3.12.x` or a newer version, and `git version 2.x.x`.

The libraries (pandas, NumPy, ...) are installed into a *virtual environment* in
the Homework folder - see [step 9](#create-the-venv) below.

### VS Code extensions {#vscode-extensions}

| Extension | By | What for | Needed |
|---|---|---|---|
| **Python** | Microsoft | run and debug Python; it installs **Pylance**, **Python Debugger** and **Python Environments** too | required |
| **Jupyter** | Microsoft | notebooks inside VS Code | required |
| **Data Wrangler** | Microsoft | see a DataFrame or a CSV file as a table: sort, filter, statistics per column; it writes the pandas code for the cleaning steps you click | lectures 14 - 16 |
| **Rainbow CSV** | mechatroner | each column of a CSV file in its own colour; SQL-like queries on a CSV file | from lecture 9 |
| **SQLite Viewer** | Florian Klampfer | open a SQLite `.db` file and look at its tables | lecture 13 |
| **Spreadsheet Viewer** | MESCIUS | open `.xlsx` files in VS Code (its old name is *Excel Viewer*) | lectures 9, 14, 16 |

**Install them all at once.**

1. Download the list: [extensions.json](./extensions.json){download target="_self"}.
2. In the folder of your project, create a folder named `.vscode` and put the
   file into it (the file must be `.vscode/extensions.json`).
3. Open the project folder in VS Code (**File > Open Folder...**). VS Code asks
   *Do you want to install the recommended extensions...?* - click **Install**.

Missed the question? Open the **Extensions** view (`Ctrl+Shift+X`) and type
`@recommended` in the search box. Under **Workspace Recommendations**, hover over
the header and click the cloud icon (**Install Workspace Recommended Extensions**).

The Homework folder (step 6 below) already has this file, so there VS Code asks by
itself. You can also create the file yourself and paste this content into it:

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
  each, in the order of the lecture. We start them in class if time allows.
  Finish the rest at home if you can - later tasks and the final project reuse
  them.
- **Homework** (`homework.py`): one larger task that puts the topics of the
  lecture together. Do it before the next session - we go through it together at
  the start.

This part of the page shows, step by step, how to get the tasks to your computer,
run them and save your solutions. It is written for Windows, and for people who
have not used a command line before. The setup is done once and takes about 30
minutes. After that, each session needs a few clicks and a few short commands.

**The idea.** A *repository* (or *repo*) is a project folder whose history Git
keeps. In this course you work with three copies of the Homework repository:

![The course repository and your own repository on GitHub, and the folder on your computer: clone once and pull the new tasks from the course repository, push your solutions to your own repository](/diagrams/homework-repos.svg){.diagram width=920 height=380}

- **The course repository** on GitHub. Only the trainer changes it. You download
  it once (**clone**) and then get the new tasks from it (**pull**). In Git its
  name is **`upstream`**.
- **The folder on your computer.** Here you write and run your code, in VS Code.
- **Your own repository** on GitHub. You send your solutions to it (**push**), so
  they are saved online and you can open them from any computer. In Git its name
  is **`origin`**.

**Git** is the program on your computer that keeps the versions of the files.
**GitHub** is the website that keeps the repositories online.

### Before you start {#before-you-start}

Check these four things first:

1. **The programs are installed:** Python 3.12 or newer, VS Code and Git for
   Windows (see [Set up Python on your computer](#setup)). Step 2 below checks
   them.
2. **You have a GitHub account**, and you sent your GitHub user name to the
   trainer.
3. **You accepted the invitation.** The repositories of the course are private.
   When the trainer adds you, GitHub sends you an email for each repository
   (Homework and Labs): *... has invited you to collaborate on ...*. Click **View
   invitation**, then **Accept invitation**. No email? Sign in to GitHub and open
   https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework/invitations.
   An invitation is valid for 7 days; if it expired, write to the trainer.
4. **Test it:** open
   https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework
   in the browser. You see the folders of the tasks: good. You see *404 - page
   not found*: the invitation is not accepted yet, or you are signed in to GitHub
   with another account.

### VS Code and the terminal {#terminal}

You do everything in VS Code. This is the window with the Homework folder open:

![VS Code with the Homework folder: 1 the Explorer, 2 the Run button, 3 the terminal, 4 Source Control, 5 the Python of the folder](/diagrams/vscode-window.svg){.diagram width=950 height=560}

1. **Explorer** - the files of the open folder. The name of the folder is at the
   top: it must be `PYTHON-DATA-ANALYSTS-UNICREDIT-HOMEWORK` when you work on the
   tasks. Click a file to open it.
2. **Run Python File** (the triangle) - runs the file that is open in the
   editor.
3. **Terminal** - here you type commands, and here your code prints its results.
   **+** opens a new terminal, the bin closes it. No terminal? Menu
   **Terminal > New Terminal**.
4. **Source Control** - Git with buttons (see [Save your work](#save-your-work)).
5. **The Python of the folder** - it must show `.venv` (step 10 below).

**The terminal** is a window where you type a command and the computer answers
with text. It is a bit like the SAS log, but you submit one line at a time and the
answer comes right under it. Before the cursor, the terminal always shows the
**prompt**:

![The parts of the prompt: (.venv), the current folder, then your command; under it the answer of the command, then the prompt again](/diagrams/terminal-prompt.svg){.diagram width=920 height=290}

The **current folder** in the prompt is important: a command works on the files of
this folder. Most problems come from a command typed in the wrong folder - so look
at the prompt before you press `Enter`. (`you` stands for your Windows user name.)

How to run a command from this page:

1. Point at the box with the command: a copy button appears at its top right.
   Click it.
2. Click in the terminal and paste with `Ctrl+V` (or a right-click).
3. Press `Enter` and wait until the prompt comes back. Some commands work for a
   few seconds, an installation for a few minutes. Do not type anything in the
   meantime.
4. Compare the answer with the **You see** text of the step. Red text, or a line
   with `error` or `fatal`: stop and find it in
   [If something goes wrong](#if-something-goes-wrong).

Good to know:

- The commands are exact: every space, dot and dash counts. Copy them, do not
  type them.
- `Up` (the arrow key) brings back the last command. Change it with `Left` /
  `Right` and run it again with `Enter`.
- `Ctrl+C` stops a command that hangs; `cls` clears the screen.

**Use the Command Prompt (cmd).** On Windows, the terminal of VS Code is
PowerShell by default. The commands on this page are for the Command Prompt, as
in the setup before the course; in PowerShell, a company laptop may block step 9.
Make the Command Prompt the default once:

1. Press `Ctrl+Shift+P`. A search box opens at the top of the window (the
   **Command Palette**).
2. Type `default profile` and choose **Terminal: Select Default Profile**.
3. Choose **Command Prompt**.
4. Close the open terminal (the bin, 3 in the picture) and open a new one:
   **Terminal > New Terminal**.

You see: the prompt looks like `C:\Users\you>`, without `PS` at the start (`PS`
means PowerShell).

### Set it up once {#set-it-up-once}

You do this only once, at the start of the course. Go step by step, and check the
**You see** of each step before you go on. At the end, your course folder looks
like this:

```text
C:\Users\you\python-course\
    Python-Data-Analysts-UniCredit-Homework\
        .venv\
        01-intro-syntax-types\
            practice\
            homework.py
        02-conditions-and-loops\
        data\
        check.py
        requirements.txt
    Python-Data-Analysts-UniCredit-Labs\
```

- `python-course` - the course folder (step 1).
- `Python-Data-Analysts-UniCredit-Homework` - the tasks (step 5). Open this
  folder in VS Code when you work on them.
- `.venv` - Python with pandas and the other libraries (step 9).
- `practice` and `homework.py` - the practice tasks and the homework of each
  lecture. `data` - the sample data. `check.py` prints `OK` / `FAIL`: do not
  change it.
- `Python-Data-Analysts-UniCredit-Labs` - the code from the lessons (see
  [Code from the lessons](#code-from-the-lessons)).

#### 1. Create the course folder and open it in VS Code

1. Start VS Code. In the menu: **File > Open Folder...** A Windows window for
   choosing a folder opens.
2. Click in the address bar at the top of that window, type `%USERPROFILE%` and
   press `Enter`. This is your user folder, `C:\Users\you`.
3. Click **New folder**, type the name `python-course` and press `Enter`.
4. Select the new folder (one click) and click **Select Folder**.
5. VS Code asks *Do you trust the authors of the files in this folder?* Click
   **Yes, I trust the authors**.
6. Open a terminal: **Terminal > New Terminal**.

You see: the prompt ends with the course folder:

```text
C:\Users\you\python-course>
```

::: tip Why not the Desktop or Documents?
On a company laptop, the Desktop and Documents are often kept in OneDrive.
OneDrive then tries to sync the thousands of small files of the virtual
environment (step 9): that is slow and can lock the files. A folder right in your
user folder is not synced. Do you already have a folder for the course from the
setup before it? Use it, if it is not in OneDrive.
:::

#### 2. Check the tools

Run these two commands, one at a time:

```cmd
py --version
```

You see: `Python 3.12.` (or higher) and a number.

```cmd
git --version
```

You see: `git version 2.` and more numbers.

`... is not recognized as an internal or external command`? See
[If something goes wrong](#if-something-goes-wrong).

#### 3. Tell Git who you are

Git writes your name and email into every version you save. Copy the first
command and paste it into the terminal. **Before** you press `Enter`, change the
text between the quotes to your name: move with the arrow keys, delete with
`Backspace`.

```cmd
git config --global user.name "Your Name"
```

The same for your email. Use the email of your GitHub account:

```cmd
git config --global user.email "you@example.com"
```

You see: nothing. Here, no answer is a good answer. Check both:

```cmd
git config --global --list
```

You see: your name in the line `user.name=...` and your email in the line
`user.email=...`. Steps 2 and 3 are once per computer.

#### 4. Create your own repository on GitHub

In the browser:

1. Sign in to https://github.com.
2. Click **+** at the top right, then **New repository**.
3. **Repository name**: `python-course-homework` (or another name you like).
4. Choose **Private**: only you can see it.
5. Leave everything else as it is: **no** README, **no** `.gitignore`, **no**
   license. The repository must be **empty** - otherwise step 8 fails.
6. Click **Create repository**.
7. GitHub shows a page with *Quick setup* at the top. Check that **HTTPS** is
   selected (not SSH). The address next to it looks like
   `https://github.com/your-user/python-course-homework.git`. Leave this page open
   in the browser: you copy the address from it in step 7.

#### 5. Download the course repository (clone)

In the terminal - the prompt ends with `\python-course>`:

```cmd
git clone https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework.git
```

The first time, a window asks you to sign in to GitHub. Choose **Sign in with
your browser**, sign in in the browser and allow the access (**Authorize**).
Windows remembers it: Git does not ask again.

You see: `Cloning into 'Python-Data-Analysts-UniCredit-Homework'...`, a few lines
with `100%`, and the prompt again. The new folder
`Python-Data-Analysts-UniCredit-Homework` appears in the Explorer.

#### 6. Open the Homework folder in VS Code

1. **File > Open Folder...**
2. Go into `python-course`, select `Python-Data-Analysts-UniCredit-Homework` (one
   click) and click **Select Folder**.
3. VS Code asks if you trust the authors: **Yes, I trust the authors**.
4. If VS Code offers to install the recommended extensions (bottom right), click
   **Install** (see [VS Code extensions](#vscode-extensions)).
5. Open a new terminal: **Terminal > New Terminal**.

You see: the Explorer shows `PYTHON-DATA-ANALYSTS-UNICREDIT-HOMEWORK` at the top,
and the prompt ends with the Homework folder:

```text
C:\Users\you\python-course\Python-Data-Analysts-UniCredit-Homework>
```

From now on, **always open this folder** when you work on the tasks. VS Code
opens the last folder by itself; if not, **File > Open Recent**.

#### 7. Connect your own repository

Now the folder knows only the course repository, under the name `origin`. Rename
it to `upstream`:

```cmd
git remote rename origin upstream
```

You see: nothing.

Now add your own repository as `origin`. On the GitHub page of step 4, copy your
address with its copy button (closed the page? Open your repository on GitHub: it
shows the same page). In the terminal, type `git remote add origin ` (with a space
at the end), paste the address with `Ctrl+V`, and press `Enter`. The whole line
looks like this:

```cmd
git remote add origin https://github.com/your-user/python-course-homework.git
```

Check:

```cmd
git remote -v
```

You see four lines: `origin` with **your** address, `upstream` with the address
of the course:

```text
origin    https://github.com/your-user/python-course-homework.git (fetch)
origin    https://github.com/your-user/python-course-homework.git (push)
upstream  https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework.git (fetch)
upstream  https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework.git (push)
```

#### 8. Send everything to your repository (the first push)

```cmd
git push -u origin main
```

You see: a few lines with `100%`, and at the end:

```text
branch 'main' set up to track 'origin/main'.
```

Refresh the page of your repository on GitHub: the folders of the tasks are
there.

#### 9. Create the virtual environment {#create-the-venv}

The tasks of the later lectures need pandas and other libraries. They go into a
*virtual environment*: the folder `.venv` in the Homework folder, with its own
Python and its own libraries ([lecture 1](/lectures/01-intro-syntax-types#virtual-environments)
explains it). Four commands, one at a time:

```cmd
py -m venv .venv
```

You see: no answer, but after a few seconds the folder `.venv` appears in the
Explorer. If VS Code asks whether to use the new environment for this folder,
click **Yes**.

```cmd
.venv\Scripts\activate
```

You see: the prompt now starts with `(.venv)`. The next two commands install into
this environment.

```cmd
python -m pip install --upgrade pip
```

```cmd
pip install -r requirements.txt
```

This takes a few minutes. You see many lines; the last one starts with
`Successfully installed` and lists the libraries (pandas, numpy, ...). A
`WARNING` or a `[notice]` line is fine; an `ERROR` is not - see
[If something goes wrong](#if-something-goes-wrong).

The folder `.venv` stays only on this computer: Git does not save it (it is
listed in `.gitignore`).

#### 10. Choose the Python of the folder

1. Press `Ctrl+Shift+P`, type `select interpreter` and choose **Python: Select
   Interpreter**.
2. Choose the line with `.venv` (`.\.venv\Scripts\python.exe`).

You see: the status bar at the bottom of the window (5 in the picture) shows the
version of Python and `.venv`. From now on VS Code runs the tasks with this
Python, and a new terminal starts with `(.venv)` by itself.

#### 11. Run the first task

1. In the Explorer, open the folder `01-intro-syntax-types`, then `practice`, and
   click `task1-first-values.py`.
2. Press `Ctrl+Shift+B`.

You see, in the terminal:

```text
FAIL loan_id: got None (NoneType), expected 'L000001' (str)
FAIL currency: got None (NoneType), expected 'EUR' (str)
...
0 of 8 checks passed
```

`FAIL` is right here: you have not written any code yet. **The setup is done.**

### Work on a task {#work-on-a-task}

Every time:

1. Open VS Code. It opens the last folder: check that the Explorer shows
   `PYTHON-DATA-ANALYSTS-UNICREDIT-HOMEWORK` at the top (if not:
   **File > Open Recent**).
2. In the Explorer, open the folder of the lecture and the task, for example
   `02-conditions-and-loops`, `practice`, `task1-predict-logic.py`.
3. A task has parts. Read the description of the first part (the `#` comments
   right before its code). Write your code between the lines
   `# ---- your code ... ----` and `# ---- end of your code ----`. Change
   nothing else in the file.
4. Run the file: `Ctrl+Shift+B`, or the triangle at the top right (**Run Python
   File**, 2 in the picture). Both save the file first.
5. Read the result in the terminal: `OK` or `FAIL` for each check, and at the end
   a line like `5 of 8 checks passed`. A `FAIL` line shows what your code gave
   (`got ...`) and what the check expects (`expected ...`). Fix your code and run
   the file again.
6. Then go on with the next part: it starts right after the checks of this one.

Another way to run a task: in the terminal, with `(.venv)` at the start of the
prompt, type `python` and the path of the file:

```cmd
python 02-conditions-and-loops\practice\task1-predict-logic.py
```

You do not have to type the path: right-click the file in the Explorer >
**Copy Relative Path**, then type `python ` in the terminal (with a space) and
paste with `Ctrl+V`.

### Save your work {#save-your-work}

Save your solutions in your own repository at the end of each working day, and
always before a session. Three commands, in the terminal of the Homework folder:

```cmd
git add .
```

Chooses all changed files for the next version. Mind the dot at the end.

```cmd
git commit -m "Session 2 practice"
```

Saves a version on your computer, with a short message. Change the text between
the quotes as you like.

```cmd
git push
```

Sends the new versions to your repository on GitHub.

You see: after `git push`, a few lines and at the end `main -> main`. Refresh your
repository on GitHub: your changes are there. If `git commit` says
`nothing to commit, working tree clean`, there is nothing new to save: did you
save the file (`Ctrl+S`)?

::: tip The same with buttons
Open **Source Control** (4 in the picture, or `Ctrl+Shift+G`). Type a message in
the box at the top and click **Commit**. If VS Code asks *Would you like to stage
all your changes and commit them directly?*, click **Yes**. Then click **Sync
Changes** (and **OK**, if VS Code asks).
:::

### Get the new tasks {#get-the-new-tasks}

The trainer adds the folder of each lecture on the morning of its session. To get
it:

1. Save your work first: the three commands of [Save your work](#save-your-work).
2. Get the new tasks from the course repository:

   ```cmd
   git pull --no-rebase --no-edit upstream main
   ```

3. Send them to your own repository too:

   ```cmd
   git push
   ```

You see: after the pull, a line like `Merge made by the 'ort' strategy.` (or
`Fast-forward`) and the list of the new files. The new folder, for example
`03-lists-tuples-sets`, appears in the Explorer. Your own files do not change.

The parts of the pull command: `upstream main` - from the course repository;
`--no-rebase` - join the new tasks with your work; `--no-edit` - do not ask for a
message. Without them, Git stops with an error or opens an editor.

### If something goes wrong {#if-something-goes-wrong}

Read the last lines in the terminal: the error is usually there. Find it below.
Still stuck? Write to the trainer: the step, the command, and a screenshot of the
terminal (`Win+Shift+S` takes a screenshot of a part of the screen).

- **`'git' is not recognized as an internal or external command`** - Git is not
  installed, or VS Code was open while you installed it. Install
  [Git for Windows](https://git-scm.com/downloads/win) with the default settings,
  then close VS Code completely and start it again.
- **`'py' is not recognized as an internal or external command`** - Python was
  installed without its launcher `py`. Use `python` instead of `py` (step 9:
  `python -m venv .venv`). If `python --version` does not work either, install
  Python again, with **Add python.exe to PATH** ticked (see
  [Set up Python on your computer](#setup)).
- **The prompt starts with `PS`**, or **`running scripts is disabled on this
  system`** after `.venv\Scripts\activate` - the terminal is PowerShell. Make the
  Command Prompt the default ([VS Code and the terminal](#terminal)), open a new
  terminal and run the command again.
- **`remote: Repository not found.`** (step 5) - you have no access yet: accept
  the invitation ([Before you start](#before-you-start)). Already accepted? Then
  Git is probably signed in with another GitHub account. In the Windows Start
  menu, open **Credential Manager** > **Windows Credentials**, remove the entry
  `git:https://github.com`, and run the command again: Git asks you to sign in.
- **`fatal: destination path 'Python-Data-Analysts-UniCredit-Homework' already
  exists`** (step 5) - you have downloaded it before. Go on with step 6.
- **`fatal: not a git repository`** - the terminal is not in the Homework folder.
  Open the Homework folder (step 6) and a new terminal: the prompt must end with
  `\Python-Data-Analysts-UniCredit-Homework>`.
- **`error: remote origin already exists.`** (step 7) - run `git remote -v` and
  compare with step 7. Is `origin` the address of the course? Run the two
  commands of step 7 again, in their order. Is `origin` a wrong address of yours?
  Type `git remote set-url origin ` (with a space at the end), paste the right
  address and press `Enter`.
- **`! [rejected] main -> main (fetch first)`** (step 8) - your repository on
  GitHub is not empty: it has a README. On GitHub, delete it (in the repository:
  **Settings**, at the bottom **Delete this repository**) and create it again,
  empty (step 4), with the same name. Then run step 8 again.
- **`Author identity unknown`** (commit) - Git does not know who you are. Do step
  3, then run the commit again.
- **`ERROR`** in step 9, with **`ProxyError`**, **`SSLError`** or
  **`CERTIFICATE_VERIFY_FAILED`** - the company network blocks or checks the
  connection to pypi.org, the site of the Python libraries. Ask your IT for the pip
  settings (a proxy or an internal mirror), as for the setup before the course.
- **`ModuleNotFoundError: No module named 'pandas'`** (when you run a task) - the
  task runs with another Python, not the one in `.venv`. Do step 10. In the
  terminal, the prompt must start with `(.venv)`; if it does not, run
  `.venv\Scripts\activate`.
- **`fatal: Need to specify how to reconcile divergent branches.`** (pull) - the
  two options are missing. Use the whole command of
  [Get the new tasks](#get-the-new-tasks).
- **`Your local changes to the following files would be overwritten by merge`**
  (pull) - some changes are not saved in a version yet. Do the three commands of
  [Save your work](#save-your-work), then pull again.
- **`CONFLICT`** (pull) - rare: the same file was changed in both repositories.
  Run `git merge --abort` (everything is as before the pull) and write to the
  trainer.
- **A strange editor fills the terminal** (lines that start with `~`, or
  `-- INSERT --` at the bottom) - Git asks for a message in the editor Vim. Press
  `Esc`, type `:wq` and press `Enter`. Next time, use the commands exactly as on
  this page (`git commit -m "..."`, `git pull --no-rebase --no-edit ...`).

## Code from the lessons

The code written during the lessons is in the **Labs repository**:
https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Labs

You only download it. Do not write your own code there - use the Homework folder
for that.

**Once** (after you accepted its invitation, see [Before you start](#before-you-start)):

1. Open the course folder `python-course` in VS Code (**File > Open Folder...**),
   **not** the Homework folder: the Labs folder must be next to the Homework
   folder, not inside it.
2. **Terminal > New Terminal**. The prompt ends with `\python-course>`.
3. Download it:

   ```cmd
   git clone https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Labs.git
   ```

Did it land inside the Homework folder? Close VS Code and move the folder
`Python-Data-Analysts-UniCredit-Labs` one level up, into `python-course`, in the
File Explorer of Windows.

**After each lesson:** open the Labs folder in VS Code (**File > Open Recent**),
open a terminal and get the new code:

```cmd
git pull
```

## Find things

- The search box (top left, or `Ctrl+K`) searches all lectures.
- The list on the right side of a lecture ("In this lecture") jumps to a section.
- The moon / sun switch at the top changes between dark and light mode.
- The **EN / BG** button next to it opens the same page in English or in Bulgarian.
- The navigation on the left and the "In this lecture" column on the right can
  be made narrower or wider: drag their inner edge. Double-click the edge to go
  back to the default width.
