---
title: 8. Error handling and file handling
---

# 8. Error handling and file handling

<div class="lecture-meta">
  <span>Session 8</span><span>practice: <code>08-errors-and-files/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- read a traceback, and know the common exceptions of data work;
- catch an error with `try` / `except` and go on - instead of stopping the whole
  script;
- raise errors with a clear message when the data is wrong;
- work with files and folders through `pathlib`;
- read and write text, CSV and JSON files, also in cp1251 (old Windows Cyrillic).

From SAS to Python - a bad value in the data. SAS writes a NOTE to the log, sets the
value to missing and goes on:

```sas
data payments;
    infile 'payments_2026-09.csv' dsd firstobs=2 truncover;
    input payment_id :$6. loan_id :$7. pay_date :yymmdd10. amount currency :$3.;
run;
/* NOTE: Invalid data for amount in line 35 31-36.
   _ERROR_=1 _N_=34 */
```

**One bad value.** Python stops at the first bad value - unless you tell it what to do:

```python run
import csv

good, bad = [], []
with open("data/payments_2026-09.csv", encoding="utf-8") as file:
    for line_no, row in enumerate(csv.DictReader(file), start=2):
        try:
            amount = float(row["amount"])
        except (TypeError, ValueError):
            bad.append((line_no, row["amount"]))
            continue
        good.append(amount)

print(len(good), "amounts read; bad values:", bad)
```

Sections 2 - 4 show how this works: catch the error, say what is wrong, and decide
when to go on and when to stop.

## 1. Errors and exceptions

### Two kinds of errors

- A **syntax error**: the code is not valid Python. Nothing runs - Python checks the
  whole file first ([session 1](./01-intro-syntax-types.md#_3-how-python-runs-your-code)).
- An **exception**: the code is valid, but something goes wrong **while it runs**: a
  text that is not a number, a missing file, a missing key. The script stops at that
  line - unless the exception is **caught**.

```python run
print("before")
amount = float("12O.50")          # the letter O, not a zero
print("after")                    # never runs
```

### Read the traceback from the bottom

When an exception is not caught, Python prints a **traceback**: the way the program
went to the error, the last call at the bottom.

```python run
def parse_amount(text):
    return float(text.replace(",", "."))

def total(values):
    return sum(parse_amount(v) for v in values)

print(total(["10,50", "n/a", "5"]))
```

Read it **from the bottom up**:

1. The last line: the **type** of the exception and its **message** -
   `ValueError: could not convert string to float: 'n/a'`. Often this is enough.
2. Above it: the line of **your** code where it happened, and the function.
3. Higher: who called that function, and so on, up to the first call.

### The exceptions you will often meet

| Exception | When | A data example |
|---|---|---|
| `ValueError` | the type is right, the value is wrong | [`float("n/a")`](https://docs.python.org/3/builtins/functions.html#float), [`int("12.5")`](https://docs.python.org/3/builtins/functions.html#int), [`strptime("31.09.2026", ...)`](https://docs.python.org/3/library/datetime.html#datetime.datetime.strptime) |
| `TypeError` | the type is wrong | `"5" + 1`, [`float(None)`](https://docs.python.org/3/builtins/functions.html#float), `None * 2` |
| `KeyError` | a dictionary has no such key | `rating_of["C9999"]` |
| `IndexError` | a list has no such position | `fields[5]` of a short row |
| `ZeroDivisionError` | division by zero | the average of an empty group |
| `FileNotFoundError` | no such file | a wrong path, a file not delivered yet |
| `UnicodeDecodeError` | the wrong encoding | a cp1251 file read as UTF-8 |
| `AttributeError` | an object has no such method | `None.strip()` |

```python run
tests = [lambda: int("12.5"), lambda: "5" + 1, lambda: {"a": 1}["b"],
         lambda: [1, 2][5], lambda: 1 / 0, lambda: open("no_such_file.csv")]

for test in tests:
    try:
        test()
    except Exception as error:
        print(f"{type(error).__name__:<20}{error}")
```

(`try` / `except` are explained in the next section.)

**Errors from the data.** An error can also come from the data, not from your code - a value that is `None`:

```python run
city = None                       # a missing value from a lookup
print(city.strip())               # AttributeError: 'NoneType' object has no attribute 'strip'
```

## 2. `try` / `except`

### Catch an exception

Put the code that can fail in a `try` block. If an exception happens there, Python
jumps to the `except` block that matches its type - and the script goes on:

```python run
for text in ["12.50", "12O.50", "7"]:
    try:
        amount = float(text)
        print("ok:  ", amount)
    except ValueError:
        print("bad: ", text)
print("the script goes on")
```

The rest of the `try` block after the error does **not** run.

### `as error`: the message

`except ValueError as error` gives the exception object a name. [`str(error)`](https://docs.python.org/3/builtins/stdtypes.html#str) is the
message - write it into your report:

```python run
from datetime import datetime

try:
    datetime.strptime("31.09.2026", "%d.%m.%Y")
except ValueError as error:
    print("bad date:", error)
```

### Catch several kinds of errors

You can have several `except` blocks for different types:

```python run
rates = {"EUR": 1.0, "USD": 1.165}

def to_eur(amount_text, currency):
    try:
        return float(amount_text) / rates[currency]
    except ValueError:
        return "bad amount"
    except KeyError:
        return "unknown currency"

print(to_eur("100", "USD"), to_eur("abc", "USD"), to_eur("100", "BGN"))
```

You can also use a **tuple** of error types to catch several errors at once:

```python run
def to_float(value):
    """A number from text; None for empty, None or bad values."""
    try:
        return float(value)
    except (TypeError, ValueError):      # float(None) is a TypeError
        return None

print([to_float(v) for v in ["12.5", "", None, "n/a", " 7 "]])
```

`to_float` is a small helper function that you can use in every loader: "a number, or `None`" -
like an informat with the `??` modifier in SAS, which reads a bad value as missing
without a note.

### The traps: catching too much

A bare `except:` (or `except Exception:`) catches **everything** - also your own typos.
The script then gives a wrong result without a word:

```python run
def safe_total(values):
    total = 0
    for v in values:
        try:
            total += flaot(v)          # a typo: NameError - but it is hidden!
        except:
            pass
    return total

print(safe_total(["10", "20", "30"]))  # 0 - and no error
```

### Rules

- Catch the **specific** exception you expect (`ValueError`, `KeyError`), not all.
- Keep the `try` block **small**: only the line that can fail.
- Never `pass` silently in a loader: count the error, or write it somewhere.

## 3. `try`, `except`, `else` and `finally`

The full form has two more parts:

```text
try:
    code that can fail
except SomeError:
    runs if that error happened
else:
    runs if NO error happened
finally:
    runs ALWAYS - after an error, without one, even after a return
```

`else` keeps the `try` block small: only the risky line is inside, the code that
**uses** the result is in `else`. `finally` is for clean-up that must happen
whatever comes - closing a connection ([lecture 12](./12-databases.md#close-the-connection-always)), writing the last log line.

In the next example, `finally` makes sure that a loan never stays marked as "under review"
after its processing ends - even after an unexpected exception.

```python run
active_reviews = set()

for loan_id, income in [("L001", "2500"), ("L002", "unknown")]:
    active_reviews.add(loan_id)

    try:
        monthly_income = float(income)
    except ValueError:
        print(loan_id, "-> invalid income; manual review needed")
    else:
        print(loan_id, "-> monthly income:", monthly_income)
    finally:
        active_reviews.remove(loan_id)
```

::: tip Try it
Predict the output, then run:

```python run
def f(x):
    try:
        return 10 / x
    except ZeroDivisionError:
        return "zero"
    finally:
        print("finally for", x)

print(f(2))
print(f(0))
```
:::

::: details Answer
```text
finally for 2
5.0
finally for 0
zero
```

`finally` runs **before** the function returns, so its line comes first. The
`return` value is printed only after `f` has ended. With `0`, the `except` block
returns `"zero"`, and `finally` still runs.
:::

## 4. `raise`

### `raise`: stop with a clear message

Your own checks can **raise** an exception, with a message that says what is wrong
and where. In SAS: `PUTLOG "ERROR: ..."` and `ABORT`.

```python run
def check_stage(stage):
    if stage not in (1, 2, 3):
        raise ValueError(f"stage must be 1, 2 or 3, got {stage!r}")
    return stage

print(check_stage(2))
print(check_stage(4))
```

A good message names the **value** and the **rule**. "Error" alone helps nobody at
the end of a month.

::: tip Try it
Write `check_currency(code)` that returns the code in capitals if it is one of `EUR`,
`USD`, `GBP` (any case, spaces at the ends allowed), and raises a `ValueError` with the
value in the message otherwise.
:::

::: details Answer
```python run
def check_currency(code):
    clean = code.strip().upper()
    if clean not in ("EUR", "USD", "GBP"):
        raise ValueError(f"currency must be EUR, USD or GBP, got {code!r}")
    return clean

print(check_currency(" usd "))
print(check_currency("BGN"))
```

Clean the value first, then check it. The message shows the original value with
`!r`, so the spaces and the case of the input are visible too.
:::

### All problems of a row, not only the first

A check that raises, like `check_stage` above, stops at the **first** broken rule of a row. For a data
quality report you may want **every** problem - collect the messages in a list
instead of raising:

```python run
def problems_of(payment):
    """All broken rules of one payment (a dict of text fields)."""
    found = []
    if not payment.get("loan_id", "").startswith("L"):
        found.append("bad loan id")
    try:
        if float(payment.get("amount", "")) <= 0:
            found.append("amount not positive")
    except ValueError:
        found.append("amount not a number")
    if payment.get("currency") not in ("EUR", "USD"):
        found.append("unknown currency")
    return found

print(problems_of({"loan_id": "L000001", "amount": "100", "currency": "EUR"}))
print(problems_of({"loan_id": "X1", "amount": "n/a", "currency": "BGN"}))
```

### When to stop, when to go on

| Situation | What to do |
|---|---|
| a bad row in a big input | go on: reject the row, count it, report it |
| too many bad rows (say more than 1%) | stop: the input is broken |
| a missing input file, a wrong report date | stop: a report on wrong input is worse than no report |
| a possible bug in your code | stop: do not catch it |

## 5. Paths with `pathlib`

### What is a path?

A **path** tells Python where to find a file or a folder - for example, the CSV file
with the loans.

A path can be:

- **absolute**: the full location, from the top of the disk. For example
  `C:/RiskAnalysis/data/loans.csv` on Windows, or
  `/home/maria/RiskAnalysis/data/loans.csv` on Linux and macOS.
- **relative**: a location that starts from the **current working directory** - the
  folder where Python "stands" when the script runs. For example `data/loans.csv`.

Common relative paths. In this example, the current folder is `reports`:

```text
RiskAnalysis/
├── data/
│   └── loans.csv          <- ../data/loans.csv
└── reports/               <- the current folder
    ├── loans.csv          <- loans.csv or ./loans.csv
    └── data/
        └── loans.csv      <- data/loans.csv
```

| Path | Where it points |
|---|---|
| `loans.csv` | the file `loans.csv` in the current folder |
| `./loans.csv` | the same file: `.` means "the current folder" |
| `data/loans.csv` | the file `loans.csv` in the folder `data`, inside the current folder |
| `../data/loans.csv` | `..` means "one folder up": the folder `data` next to the current folder |

So far we wrote `open("data/loans.csv")` - a relative path. It works because you run
the scripts from the folder of the homework repository, and `data` is in that folder:

```text
Homework/                      <- the current folder (you run python from here)
├── data/
│   ├── loans.csv
│   └── clients.csv
└── 08-errors-and-files/
    └── homework.py
```

::: warning The same script, another folder: `FileNotFoundError`
A relative path depends on the folder you run the script **from**, not on the folder
where the script is. If you open a terminal in `Homework/08-errors-and-files/` and run
`python homework.py`, Python looks for `08-errors-and-files/data/loans.csv` - and
there is no such file. Run the scripts from the repository folder, as the first line
of each task file says.
:::

### A `Path` object

The module [`pathlib`](https://docs.python.org/3/library/pathlib.html) gives a **`Path` object**. The operator `/` joins the parts of a
path (here it is not a division), with the right separator for Windows (`\`) or
Linux / macOS (`/`):

```python run
from pathlib import Path

print(Path.cwd())                         # the current working directory

loans_file = Path("data") / "loans.csv"
print(loans_file)
print(loans_file.exists())                # does the file exist?
print(loans_file.name, loans_file.suffix) # the file name and its type
```

In SAS a `LIBNAME` or a `FILENAME` gives a name to a location; in Python you keep the
location in a variable:

| SAS | Python |
|---|---|
| `LIBNAME src "C:\data";` | `src = Path(r"C:\data")` |
| `FILENAME f "C:\data\loans.csv";` | `f = src / "loans.csv"` |
| `%SYSFUNC(FEXIST(f))` | [`f.exists()`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.exists) |

::: warning Windows paths in Python code
A Windows path in a normal string has backslashes - and `"\n"`, `"\t"` are special
characters ([lecture 7](./07-text-and-regex.md#writing-a-regex-in-python)). Use a raw string, or forward slashes, which Windows also
accepts:

```python
Path(r"C:\Users\maria\reports\new_loans.csv")     # a raw string
Path("C:/Users/maria/reports/new_loans.csv")      # forward slashes
```
:::

### The output folder

A report script writes its results into a folder, for example `out`. [`mkdir`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.mkdir) creates
it; `exist_ok=True` means "no error if it is already there", so the script can run
every month. For a small file, `write_text` and `read_text` write and read the whole
text in one step:

```python run
from pathlib import Path

Path("out").mkdir(exist_ok=True)

note = Path("out") / "readme.txt"
note.write_text("Created by the monthly report.\n", encoding="utf-8")
print(note.read_text(encoding="utf-8"))
```

### Say which file is missing

If a file is not there, `open` raises a `FileNotFoundError` (section 1). In a monthly
job this often means "the input is not delivered yet". Say **which** file is missing:

```python run
from pathlib import Path

path = Path("data") / "payments_2026-10.csv"
try:
    with open(path, encoding="utf-8") as file:
        rows = file.readlines()
except FileNotFoundError:
    print(f"ERROR: the input {path} is not delivered yet")
```

::: tip Try it
Change the file name to `payments_2026-09.csv` and print `len(rows)` after the
`try` block. Then check with `exists()`, without `open`, which of `loans.csv`,
`clients.csv` and `payments_2026-10.csv` are in `data/`.
:::

::: details Answer
```python run
from pathlib import Path

path = Path("data") / "payments_2026-09.csv"
try:
    with open(path, encoding="utf-8") as file:
        rows = file.readlines()
except FileNotFoundError:
    print(f"ERROR: the input {path} is not delivered yet")

print(len(rows))

for name in ["loans.csv", "clients.csv", "payments_2026-10.csv"]:
    print(name, (Path("data") / name).exists())
```

`len(rows)` counts all lines, the header too. With the missing October file,
`print(len(rows))` raises a `NameError`: the `except` block ran, so `rows` was never
created.
:::

## 6. Text files

### Open, read, close: `with`

To work with a file, a program **opens** it, **reads** or **writes**, and **closes**
it. In Python, `with open(...)` does all three:

```python run
with open("data/rating_scale.csv", encoding="utf-8") as file:   # open the file
    first_line = file.readline()                                # read from it
                                                                # here the file is closed
print(first_line)
```

- [`open(path, encoding=...)`](https://docs.python.org/3/builtins/functions.html#open) opens the file and gives a **file object**;
- `as file` gives the file object a name - `file` is just a variable;
- the indented block works with the file;
- at the end of the block, `with` **closes** the file - also when an exception
  happens inside. Without `with`, an error can leave the file open (and on Windows,
  locked).

You have used it since [session 2](./02-conditions-and-loops.md#the-rows-of-a-file).

The **mode** says what you want to do:

| Mode | Means |
|---|---|
| `"r"` | read (the default) |
| `"w"` | write - a new file, or **empty** an existing one |
| `"a"` | append at the end |
| `"x"` | write a new file - an error if it exists |

**Write a file.** Always give the `encoding` (why: see [Encodings](#encodings-utf-8-cp1251-and-cyrillic) below):

```python run
from pathlib import Path

Path("out").mkdir(exist_ok=True)

with open("out/log.txt", "w", encoding="utf-8") as file:
    file.write("2026-09-30 report started\n")
    print("2026-09-30 loans loaded: 400", file=file)       # print into a file

with open("out/log.txt", "a", encoding="utf-8") as file:
    file.write("2026-09-30 report finished\n")

with open("out/log.txt", encoding="utf-8") as file:
    for line in file:
        print(line.rstrip())
```

::: danger `"w"` empties the file at once
The file is emptied when it is **opened** with `"w"` - before anything is written. To
add lines to a log, use `"a"`:

```python run
from pathlib import Path

Path("out").mkdir(exist_ok=True)
Path("out/history.txt").write_text("2026-08-31 report done\n", encoding="utf-8")

with open("out/history.txt", "w", encoding="utf-8") as file:   # meant: add a line
    file.write("2026-09-30 report done\n")

print(Path("out/history.txt").read_text(encoding="utf-8"))     # August is gone
```
:::

### Read a big file line by line

For big files, loop over the file object: only one line is in memory at a time.

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    count = 0
    for line in file:              # one line at a time
        count += 1
print(count, "lines")
```

::: tip Try it
Write the 10 loan ids with the largest outstanding into `out/top10.txt`, one per line,
then read the file back and print the number of lines.
:::

::: details Answer
```python run
from pathlib import Path

loans = []
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()                               # skip the header line
    for line in file:
        fields = line.strip().split(",")
        loans.append((float(fields[7]), fields[0]))   # (outstanding, loan_id)

top10 = sorted(loans, reverse=True)[:10]          # the largest first

Path("out").mkdir(exist_ok=True)
with open("out/top10.txt", "w", encoding="utf-8") as file:
    for outstanding, loan_id in top10:
        file.write(loan_id + "\n")

with open("out/top10.txt", encoding="utf-8") as file:
    count = 0
    for line in file:
        count += 1
print(count, "lines")
```

The tuples `(outstanding, loan_id)` sort by their first item, the outstanding.
:::

### Encodings: UTF-8, cp1251 and Cyrillic

A file on disk is **bytes**, not text. An **encoding** is the rule that turns text
into bytes and back. Two encodings you will meet:

- **UTF-8** - every character of every language; the standard of the web, of
  Python source files and of most new files.
- **cp1251** (Windows-1251) - the old Windows encoding for Cyrillic. Exports from old
  systems and Excel files saved as "CSV" on a Bulgarian Windows are often cp1251.

Read a file with the **same** encoding it was written with. The file `regions_bg.csv`
is saved in cp1251 - the file of the `UnicodeDecodeError` in [section 1](#_1-errors-and-exceptions):

```python run
with open("data/regions_bg.csv", encoding="cp1251") as file:
    print(file.read())
```

That is why every [`open()`](https://docs.python.org/3/builtins/functions.html#open) in this course says `encoding="utf-8"`: without it, Python
3.12 - 3.14 on Windows uses the Windows encoding of the computer (often cp1252 or
cp1251), and the same script gives different results on different computers. (From
Python 3.15 on, UTF-8 is the default everywhere. Still write it: the script may run
on an older Python.)

::: details Advanced: the BOM of Excel
Excel saves "CSV UTF-8" with a **BOM** - three invisible bytes at the start. Read
such a file with `encoding="utf-8-sig"`, or the first column name gets an invisible
character in front:

```python run
with open("data/loans_export.csv", encoding="utf-8") as file:
    print(repr(file.readline()[:12]))
with open("data/loans_export.csv", encoding="utf-8-sig") as file:
    print(repr(file.readline()[:12]))
```
:::

## 7. CSV files

### Read: `csv.reader` and `csv.DictReader`

In [section 6](#read-a-big-file-line-by-line) you split each line with
`line.split(",")`. That works for `loans.csv`, but not for every CSV file. When a
value has a comma inside it, the file puts the value in quotes - like the
comments of the credit officers:

```python run
with open("data/loan_comments.csv", encoding="utf-8") as file:
    file.readline()                    # skip the header line
    for i in range(4):                 # the 4th loan line
        line = file.readline()
    print(line.strip())
    print(len(line.strip().split(",")), "parts, but the file has 3 columns")
```

`split(",")` does not know about quotes: it also cuts at the comma in
`340,800`. The module [`csv`](https://docs.python.org/3/library/csv.html) (it
comes with Python) reads CSV files the right way. You used it in
[lecture 7](./07-text-and-regex.md#reading-a-csv-file) as a given pattern; here is
how it works.

**`csv.DictReader`: each row as a dictionary.**  
[`csv.DictReader(file)`](https://docs.python.org/3/library/csv.html#csv.DictReader)
reads the **first line** of the file as the column names. Then it gives each next
line as a **dictionary**: the column name is the key - a record as in
[session 6](./06-dictionaries.md#a-row-as-a-dictionary). It does not read the
whole file at once: like a file, you go through it with `for`, one row at a time.

```python run
import csv

with open("data/loan_comments.csv", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        if row["loan_id"] == "L000215":
            print(row)
            print(row["comment"])
```

The comma inside the quotes is now part of the comment, and the quotes are gone.
You get the values by **name**, not by position: `row["comment"]`, not `fields[2]`.
The script still works if someone adds a column to the file.

Need all the rows, for example to go through them twice? Put them in a list with
`list(...)`, as in lecture 7 - for a small file only, since the whole file is
then in memory:

```python run
import csv

with open("data/rating_scale.csv", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

print(len(rows), "rows")
print(rows[0])
```

**The trap: every value is text.** A CSV file has no types. `DictReader` gives strings, also for numbers - convert them yourself
with `int()` or `float()`:

```python run
import csv

with open("data/loans.csv", encoding="utf-8") as file:
    row = list(csv.DictReader(file))[0]         # the first row

print(repr(row["outstanding"]), repr(row["stage"]))
print(row["outstanding"] + row["outstanding"])                # text: glued
print(float(row["outstanding"]) + float(row["outstanding"]))  # numbers: added
```

::: tip Try it
Read `loans.csv` with `DictReader` and sum the column `outstanding` of the loans
with `stage` equal to 3. Remember: `row["stage"]` is the text `"3"`, not the
number `3`.
:::

::: details Answer
```python run
import csv

total = 0
with open("data/loans.csv", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        if row["stage"] == "3":                 # compare text with text
            total += float(row["outstanding"])

print(round(total, 2))
```

The same in one line, with `sum(... for ...)` from
[lecture 5](./05-lists-advanced.md#sum-for-sum-and-count-with-a-condition) - a
`SUM(...) WHERE` in SQL. The generator takes the rows one at a time, so it works
also for a big file:

```python run
import csv

with open("data/loans.csv", encoding="utf-8") as file:
    total = sum(float(row["outstanding"])
                for row in csv.DictReader(file)
                if row["stage"] == "3")

print(round(total, 2))
```

The `sum` must be **inside** the `with`: after the `with` the file is closed, and
the generator cannot read it any more.

`row["stage"] == 3` is always `False` (text is never equal to a number), and the
sum stays `0` - with no error to warn you.
:::

**`csv.reader`: each row as a list.**
[`csv.reader`](https://docs.python.org/3/library/csv.html#csv.reader) also
understands quotes, but gives each row as a **list**, and the header line is just
the first row. Both take a `delimiter` for files that are not comma-separated -
like `;` in a Bulgarian Excel export:

```python run
import csv

with open("data/loans_export.csv", encoding="utf-8-sig") as file:
    reader = csv.reader(file, delimiter=";")
    header = next(reader)
    first = next(reader)

print(header)
print(first)
```

(`utf-8-sig` removes the BOM that Excel writes at the start - [section 6](#encodings-utf-8-cp1251-and-cyrillic).)

### A lookup table from a file: the rating scale

A nomenclature often lives in a file: `rating_scale.csv` has one row per rating.
Read it **once** into a dictionary **rating -> (grade, PD_mid)** and use it
for every client. The values are text: convert the key with `int` and the PD
bounds with `float`:

```python run
import csv

scale = {}
with open("data/rating_scale.csv", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        pd_mid = (float(row["pd_min"]) + float(row["pd_max"])) / 2
        scale[int(row["rating"])] = (row["grade"], round(pd_mid, 6))

print(scale[4])
grade, pd_value = scale[7]
print(grade, pd_value)
```

**Text keys.** The trap: without `int`, the keys are the strings `"1"`, `"2"`, ... and
`scale[4]` raises `KeyError` - the rating `4` of a client is an int:

```python run
import csv

with open("data/rating_scale.csv", encoding="utf-8") as file:
    text_keys = {row["rating"]: row["grade"] for row in csv.DictReader(file)}

print(list(text_keys)[:3])
print(text_keys.get(4, "not found"), text_keys["4"])
```

::: tip Try it
Build a second dictionary **grade -> description** from the same file, and print
the description of `"CCC"`. Which column is the key now?
:::

::: details Answer
```python run
import csv

descriptions = {}
with open("data/rating_scale.csv", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        descriptions[row["grade"]] = row["description"]

print(descriptions["CCC"])
```

The key is the column `grade`. It is text in the file and text in the lookup, so no
`int` is needed here.
:::

### Write: `csv.writer` and `csv.DictWriter`

Open the file with `newline=""` - the `csv` module writes the line ends itself. Without
it, on Windows every second line of the file is empty:

```python run
import csv
from pathlib import Path

Path("out").mkdir(exist_ok=True)
rows = [("retail", 242, 6837600.42), ("sme", 104, 31446058.29), ("corporate", 54, 93087049.89)]

with open("out/segments.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["segment", "loans", "outstanding"])
    writer.writerows(rows)

print(Path("out/segments.csv").read_text(encoding="utf-8"))
```

**Write dictionaries.** `DictWriter` writes dictionaries; `fieldnames` gives the columns and their order:

```python run
import csv
from pathlib import Path

Path("out").mkdir(exist_ok=True)
records = [{"loan_id": "L000002", "reason": "late, 35 days"}, {"loan_id": "L000070", "reason": "large"}]

with open("out/watch_list.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["loan_id", "reason"])
    writer.writeheader()
    writer.writerows(records)

print(Path("out/watch_list.csv").read_text(encoding="utf-8"))
```

The comma inside `"late, 35 days"` is quoted automatically, so the file reads back
correctly.

| SAS | Python |
|---|---|
| `PROC IMPORT DATAFILE=... DBMS=CSV` | [`csv.DictReader(open(...))`](https://docs.python.org/3/library/csv.html#csv.DictReader) |
| `DLM=';'` | `delimiter=";"` |
| `PROC EXPORT ... DBMS=CSV` | [`csv.writer(...)`](https://docs.python.org/3/library/csv.html#csv.writer), `writerows` |

::: tip Try it
Write the loans of stage 3 into `out/stage3.csv` with `DictWriter`: the columns
`loan_id`, `client_id` and `outstanding`. Read the file back with `DictReader` and
print the number of rows.
:::

::: details Answer
```python run
import csv
from pathlib import Path

Path("out").mkdir(exist_ok=True)
with open("data/loans.csv", encoding="utf-8") as source, \
     open("out/stage3.csv", "w", encoding="utf-8", newline="") as target:
    writer = csv.DictWriter(target, fieldnames=["loan_id", "client_id", "outstanding"])
    writer.writeheader()
    for row in csv.DictReader(source):
        if row["stage"] == "3":
            writer.writerow({"loan_id": row["loan_id"], "client_id": row["client_id"],
                             "outstanding": row["outstanding"]})

with open("out/stage3.csv", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))
print(len(rows), "rows")
print(rows[0])
```

One `with` can open two files: read from one, write into the other, row by row.
The values stay text - there is no need to convert `outstanding` only to write it
again.
:::

## 8. JSON files

### What is JSON?

**JSON** (JavaScript Object Notation) is a text format for data, like CSV. A CSV file
is one table: rows, and the same columns in every row. JSON can hold data **inside
data**: a value can be a list, or a group of named values. Configuration files, the
answers of web APIs and the exports of many tools are JSON.

This is the settings file of our monthly report. Read it as plain text first:

```python run
from pathlib import Path

print(Path("data/report_config.json").read_text(encoding="utf-8"))
```

Only two kinds of brackets build the structure:

- `{ ... }` is an **object**: pairs `"name": value`, separated by commas. It looks
  like a Python dictionary.
- `[ ... ]` is an **array**: values in order, separated by commas. It looks like a
  Python list.

Inside them are simple values: text in double quotes (`"EUR"`), numbers (`0.45`),
`true` / `false` and `null` (no value). Here `"output"` is an object inside the
object, and `"segments"` is an array of texts.

In SAS you read such a file with the JSON engine (`LIBNAME ... JSON`), which turns it
into tables. In SQL, many databases keep JSON in a text column and read it with
functions like `JSON_VALUE`. In Python, the module [`json`](https://docs.python.org/3/library/json.html)
turns it into dictionaries and lists - the types you already know.

### JSON types and Python types

| JSON | Example | Python |
|---|---|---|
| object | `{"lgd": 0.45}` | `dict` |
| array | `[0, 30, 90]` | `list` |
| string | `"EUR"` | `str` |
| number without a point | `400` | `int` |
| number with a point | `0.45` | `float` |
| `true` / `false` | `true` | `True` / `False` |
| `null` | `null` | `None` |

[`json.loads`](https://docs.python.org/3/library/json.html#json.loads) (load **s**tring)
reads JSON from a string. Look at the type of each value:

```python run
import json

text = '{"loan_id": "L000002", "loans": 400, "lgd": 0.45, "checked": true, "rating": null, "dpd_buckets": [0, 30, 90]}'
data = json.loads(text)

for name, value in data.items():
    print(f"{name:<12} {value!r:<14} {type(value).__name__}")
```

**The trap: JSON is not Python.** The text looks like Python code, but the rules are
stricter: only double quotes, `true` and not `True`, `null` and not `None`, no comma
after the last item. A file that breaks a rule raises a `json.JSONDecodeError` (a kind
of `ValueError`), with the line and column:

```python run
import json

for text in ['{"stage": 3}', "{'stage': 3}", '{"checked": True}', '[1, 2, 3,]']:
    try:
        print(text, "->", json.loads(text))
    except json.JSONDecodeError as error:
        print(text, "-> JSONDecodeError:", error)
```

The wording of the messages can be different in another Python version; the line
and the column are always there.

### Read and write JSON files

[`json.load`](https://docs.python.org/3/library/json.html#json.load) (without the
`s`) reads a file into dictionaries and lists; [`json.dump`](https://docs.python.org/3/library/json.html#json.dump) writes one:

```python run
import json

with open("data/report_config.json", encoding="utf-8") as file:
    config = json.load(file)

print(config["report_date"], config["lgd"], config["dpd_buckets"])
print(config["output"]["folder"], type(config["output"]["excel"]))
```

The nested values are read with `[]` twice: `config["output"]` is a dictionary, and
`["folder"]` reads a key in it. Settings in a file, not in the code: next month you
change the file, not the script.

**Write JSON.** [`json.dump`](https://docs.python.org/3/library/json.html#json.dump) writes a dictionary to a file:

```python run
import json
from pathlib import Path

summary = {"report_date": "2026-09-30", "loans": 400, "outstanding": 131370708.6,
           "stages": {"1": 323, "2": 58, "3": 19}, "checked": True}

Path("out").mkdir(exist_ok=True)
with open("out/summary.json", "w", encoding="utf-8") as file:
    json.dump(summary, file, indent=2)

print(Path("out/summary.json").read_text(encoding="utf-8"))
```

::: warning JSON has no dates
A `date` is not one of the JSON types (see the table above) - [`json.dump`](https://docs.python.org/3/library/json.html#json.dump) raises a `TypeError`. Store dates as ISO text
([`d.isoformat()`](https://docs.python.org/3/library/datetime.html#datetime.date.isoformat)), and convert back after reading. Keys of JSON objects are always
strings: `{1: 323}` comes back as `{"1": 323}`.

```python run
import json
from datetime import date

record = {"loan_id": "L000002", "report_date": date(2026, 9, 30)}
try:
    print(json.dumps(record))                   # dumps: JSON as a string, not a file
except TypeError as error:
    print("TypeError:", error)
print(json.dumps(record, default=str))          # default: how to write unknown types
print(json.loads(json.dumps({1: 323})))
```
:::

::: tip Try it
Change the LGD in a copy of the config to 0.40, save it as `out/config_test.json`,
read it back, and print the LGD.
:::

::: details Answer
```python run
import json
from pathlib import Path

with open("data/report_config.json", encoding="utf-8") as file:
    config = json.load(file)

config["lgd"] = 0.40                       # change the copy in memory

Path("out").mkdir(exist_ok=True)
with open("out/config_test.json", "w", encoding="utf-8") as file:
    json.dump(config, file, indent=2)

with open("out/config_test.json", encoding="utf-8") as file:
    test = json.load(file)
print(test["lgd"])
```

The original `data/report_config.json` does not change: only the new file has
`0.4`.
:::

## 9. Summary
| Topic | Remember |
|-------|----------|
| Exceptions | an error while the code runs; it stops the script unless caught; read the traceback from the bottom |
| Common types | `ValueError`, `TypeError`, `KeyError`, `IndexError`, `ZeroDivisionError`, `FileNotFoundError`, `UnicodeDecodeError` |
| `try` / `except` | catch the specific type; `as error` for the message; a tuple for several types; keep `try` small |
| `else` / `finally` | `else` without an error; `finally` always |
| `raise` | `raise ValueError(f"... {value!r}")`: name the value and the rule |
| Stop or go on | bad rows: reject and report; bad inputs or settings: raise; bugs: let them stop |
| `pathlib` | `Path("data") / "x.csv"`; [`exists`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.exists), `name`, `suffix`; [`mkdir(exist_ok=True)`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.mkdir) |
| Files | `with open(path, mode, encoding="utf-8")`; modes `r`, `w`, `a`, `x`; loop over the file for big files |
| CSV | [`csv.reader`](https://docs.python.org/3/library/csv.html#csv.reader) / `DictReader`; `delimiter=";"`; write with `newline=""`; `utf-8-sig` for Excel |
| JSON | [`json.load(f)`](https://docs.python.org/3/library/json.html#json.load), [`json.dump(obj, f, indent=2)`](https://docs.python.org/3/library/json.html#json.dump); dates as ISO text |

## Practice
Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root:

```bash
python 08-errors-and-files/practice/task1-safe-convert.py
```

The tasks that write files write them into the folder `out/` of the repository (it is
in `.gitignore`).

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-safe-convert.py` | `to_float`, `to_int`, `to_date` with `try` / `except` |
| 2 | `task2-predict-exceptions.py` | Predict the exception, and the output with `else` / `finally` |
| 3 | `task3-paths-and-text.py` | `pathlib`: check the input files, build names, write and read a text file |
| 4 | `task4-csv-json.py` | Read the config, write a CSV report with `DictWriter` |

## Homework

1. `08-errors-and-files/homework.py` (in the homework repository): **check the
   payments file** - find the file (with a clear error if it is missing), read the
   amounts with `try` / `except`, write the bad payments into a text file and a short
   summary into a JSON file. Every check must print `OK`.
2. The practice tasks you did not finish in class.

## Self-study

This part is not covered in class. It is for reading at home: a real log for your
scripts, and Excel files without pandas.

### `logging`: the SAS log for Python scripts

[`print`](https://docs.python.org/3/builtins/functions.html#print) is fine while you develop. A script that runs every month needs a **log**:
lines with a time and a level, in a file, that you can read when something went
wrong. The module `logging` comes with Python:

```python run
import logging
from pathlib import Path

Path("out").mkdir(exist_ok=True)
logging.basicConfig(
    filename="out/report.log", encoding="utf-8", level=logging.INFO, force=True,
    format="%(asctime)s %(levelname)-8s %(message)s",
)
log = logging.getLogger("report")

log.info("report started for %s", "2026-09-30")
log.warning("%d payments rejected", 11)
try:
    1 / 0
except ZeroDivisionError:
    log.exception("the average failed")       # the message AND the traceback
log.info("report finished")

print(Path("out/report.log").read_text(encoding="utf-8"))
```

The **levels**, from the least to the most serious: `DEBUG`, `INFO`, `WARNING`, `ERROR`,
`CRITICAL`. `level=logging.INFO` writes INFO and above; switch to `DEBUG` when you look
for a problem, without changing the code. Use `%s` placeholders, not f-strings, in
log messages - the text is built only if the line is written. (`force=True` replaces
an earlier setup; in a script you call `basicConfig` once, at the start.)

| SAS log | `logging` |
|---|---|
| `NOTE:` | [`log.info(...)`](https://docs.python.org/3/library/logging.html#logging.Logger.info) |
| `WARNING:` | [`log.warning(...)`](https://docs.python.org/3/library/logging.html#logging.Logger.warning) |
| `ERROR:` | [`log.error(...)`](https://docs.python.org/3/library/logging.html#logging.Logger.error), [`log.exception(...)`](https://docs.python.org/3/library/logging.html#logging.Logger.exception) |
| `OPTIONS MPRINT;` for more detail | `level=logging.DEBUG` |

**Exercises**

1. Read `loans.csv` and write a log instead of [`print`](https://docs.python.org/3/builtins/functions.html#print): one INFO line per stage with
   the number of loans ([`Counter`](https://docs.python.org/3/library/collections.html#collections.Counter), [lecture 7](./07-text-and-regex.md#counting-with-counter)), and a WARNING if more than 4% of the
   loans are in stage 3.
2. Add a second handler that also prints the WARNING lines on the screen. (Hint:
   [`logging.StreamHandler()`](https://docs.python.org/3/library/logging.handlers.html#logging.StreamHandler), [`setLevel`](https://docs.python.org/3/library/logging.html#logging.Logger.setLevel), [`log.addHandler`](https://docs.python.org/3/library/logging.html#logging.Logger.addHandler).)

::: details Answer
```python run
import csv
import logging
import sys
from collections import Counter
from pathlib import Path

Path("out").mkdir(exist_ok=True)
logging.basicConfig(
    filename="out/stages.log", encoding="utf-8", level=logging.INFO, force=True,
    format="%(asctime)s %(levelname)-8s %(message)s",
)
log = logging.getLogger("stages")

screen = logging.StreamHandler(sys.stdout)      # exercise 2: WARNING also on the screen
screen.setLevel(logging.WARNING)
logging.getLogger().addHandler(screen)

with open("data/loans.csv", encoding="utf-8") as file:
    stages = Counter(row["stage"] for row in csv.DictReader(file))

total = sum(stages.values())
for stage, count in sorted(stages.items()):
    log.info("stage %s: %d loans", stage, count)
share = stages["3"] / total
if share > 0.04:
    log.warning("%.1f%% of the loans are in stage 3", share * 100)

print(Path("out/stages.log").read_text(encoding="utf-8"))
```

The handler of `basicConfig` writes every line into the file; the second handler
prints only the WARNING lines on the screen. Without `sys.stdout`, a `StreamHandler`
writes to the error output (`sys.stderr`) - in the terminal you see it the same way.
:::

### Excel files with `openpyxl`

#### Read a workbook

`openpyxl` (in `requirements.txt`) reads and writes `.xlsx` files. A **workbook** has
**sheets**; a sheet has rows of **cells**:

```python run
from openpyxl import load_workbook

wb = load_workbook("data/fx_rates.xlsx", read_only=True)
print(wb.sheetnames)

ws = wb["2026-09"]
for row in ws.iter_rows(min_row=1, max_row=4, values_only=True):
    print(row)
wb.close()
```

`values_only=True` gives the values as tuples. The cells are **typed**: a date
cell gives a `datetime`, a number a `float` - no conversion from text.

**One cell.** A single cell by its address, and the size of a sheet:

```python run
from openpyxl import load_workbook

wb = load_workbook("data/fx_rates.xlsx")
ws = wb["2026-07"]
print(ws["A1"].value, ws["B2"].value, ws.cell(row=2, column=1).value)
print(ws.max_row - 1, "days,", ws.max_column, "columns")
```

**USD rates from all sheets.** All sheets into one dictionary **date -> USD rate**:

```python run
from openpyxl import load_workbook

wb = load_workbook("data/fx_rates.xlsx", read_only=True)
usd = {}
for ws in wb.worksheets:
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    for row in rows:
        record = dict(zip(header, row))
        usd[record["date"].date()] = record["USD"]
wb.close()

print(len(usd), "working days;", min(usd), "to", max(usd))
print("the last rate:", usd[max(usd)])
```

#### Write a workbook

```python run
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font

Path("out").mkdir(exist_ok=True)
wb = Workbook()
ws = wb.active
ws.title = "by stage"
ws.append(["stage", "loans", "outstanding"])
for row in [(1, 323, 110184825.28), (2, 58, 16884527.04), (3, 19, 4301356.28)]:
    ws.append(row)
for cell in ws[1]:
    cell.font = Font(bold=True)
for cell in ws["C"][1:]:
    cell.number_format = "#,##0.00"
ws.column_dimensions["C"].width = 16

notes = wb.create_sheet("notes")
notes["A1"] = "Report date: 2026-09-30"
wb.save("out/stages.xlsx")

print(wb.sheetnames, "-> out/stages.xlsx saved")
```

**The number format is kept.** Read it back - the number format is stored in the file, the value stays a number:

```python run
from pathlib import Path
from openpyxl import Workbook, load_workbook

Path("out").mkdir(exist_ok=True)
wb = Workbook()
wb.active.append(["stage", "outstanding"])
wb.active.append([3, 4301356.28])
wb.active["B2"].number_format = "#,##0.00"
wb.save("out/check.xlsx")

ws = load_workbook("out/check.xlsx").active
print(ws["B2"].value, type(ws["B2"].value).__name__, ws["B2"].number_format)
```

In SAS: `PROC IMPORT DBMS=XLSX`, `LIBNAME x XLSX`, `ODS EXCEL`. pandas reads and
writes whole sheets in one line (`read_excel`, lectures 13 and 15; `to_excel` with
several sheets, [lecture 15](./15-pandas-reports.md#_6-an-excel-report-with-several-sheets)) - with openpyxl working inside. Use openpyxl
alone when you need single cells, or the formatting of a sheet.

::: info Excel on this site
The site installs `openpyxl` the first time an example uses Excel - the first run of
such an example takes a few seconds longer.
:::

**Exercises**

1. Read the sheet `2026-08` of `data/fx_rates.xlsx` and print the lowest and the
   highest USD rate of August.
2. Add a third sheet `usd` to the workbook of `out/stages.xlsx` (before saving) with
   the USD rates of September: one row per day, `date` and `rate`.

::: details Answer
```python
# 1.
fx = load_workbook("data/fx_rates.xlsx", read_only=True)
rows = fx["2026-08"].iter_rows(values_only=True)
header = next(rows)
rates = [dict(zip(header, row))["USD"] for row in rows]
print(min(rates), max(rates))

# 2. before wb.save(...)
usd = wb.create_sheet("usd")
usd.append(["date", "rate"])
source = load_workbook("data/fx_rates.xlsx", read_only=True)["2026-09"]
rows = source.iter_rows(values_only=True)
header = next(rows)
for row in rows:
    record = dict(zip(header, row))
    usd.append([record["date"].date(), record["USD"]])
```
:::

## Read more

- Python tutorial: [Errors and exceptions](https://docs.python.org/3/tutorial/errors.html),
  [Reading and writing files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
- Reference: [Built-in exceptions](https://docs.python.org/3/library/exceptions.html),
  [`pathlib`](https://docs.python.org/3/library/pathlib.html),
  [`csv`](https://docs.python.org/3/library/csv.html),
  [`json`](https://docs.python.org/3/library/json.html),
  [Logging HOWTO](https://docs.python.org/3/howto/logging.html),
  [Unicode HOWTO](https://docs.python.org/3/howto/unicode.html) (encodings)
- [openpyxl tutorial](https://openpyxl.readthedocs.io/en/stable/tutorial.html)
- Real Python: [Python exceptions: an introduction](https://realpython.com/python-exceptions/),
  [Python's pathlib module](https://realpython.com/python-pathlib/)

**Next session:** modules, packages and Git - turn your functions into a module you
can import, set up a project folder, and keep its history in Git.
