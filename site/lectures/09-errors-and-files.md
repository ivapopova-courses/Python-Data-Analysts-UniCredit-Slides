---
title: 9. Error handling and file handling
---

# 9. Error handling and file handling

<div class="lecture-meta">
  <span>Session 9</span><span>practice: <code>09-errors-and-files/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- read a traceback, and know the common exceptions of data work;
- catch an error with `try` / `except` and go on - instead of stopping the whole
  script;
- raise your own errors with a clear message when the data is wrong;
- work with files and folders through `pathlib`;
- read and write text, CSV, JSON and Excel files;
- load a file with bad rows: keep the good rows, write the bad ones to a reject file
  with the reason, and report a summary - the job of the SAS log, done properly.

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

Python stops at the first bad value - unless you tell it what to do:

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

By the end of today you will turn this into a loader that checks every field, and
writes the bad rows into their own file.

## 1. Errors and exceptions

### Two kinds of errors

- A **syntax error**: the code is not valid Python. Nothing runs - Python checks the
  whole file first (session 1).
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

### The exceptions you will meet

| Exception | When | A data example |
|---|---|---|
| `ValueError` | the type is right, the value is wrong | `float("n/a")`, `int("12.5")`, `strptime("31.09.2026", ...)` |
| `TypeError` | the type is wrong | `"5" + 1`, `float(None)`, `None * 2` |
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

(This loop already uses `try` / `except` - the next section.)

Two more that come from the data, not from your code - a value that is `None`, and a
file in another encoding:

```python run
city = None                       # a missing value from a lookup
print(city.strip())               # AttributeError: 'NoneType' object has no attribute 'strip'
```

```python run
with open("data/regions_bg.csv", encoding="utf-8") as file:     # the file is cp1251
    print(file.read())            # UnicodeDecodeError
```

| SAS | Python |
|---|---|
| `NOTE: Invalid data`, the value becomes missing, the step goes on | the script **stops**, unless you catch the exception |
| `_ERROR_ = 1` for the row | the `except` block runs for the row |
| `ERROR:` in the log stops the step | an exception that nobody catches |

::: tip Try it
Run each line alone, and name the exception before you run it: `int(" 42 ")`,
`int("4 2")`, `float("1e3")`, `["a"].index("b")`, `"abc"[10]`.
:::

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

`except ValueError as error` gives the exception object a name. `str(error)` is the
message - write it into your report:

```python run
from datetime import datetime

try:
    datetime.strptime("31.09.2026", "%d.%m.%Y")
except ValueError as error:
    print("bad date:", error)
```

### Several kinds

Several `except` blocks for different types, or one block for a **tuple** of types:

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

```python run
def to_float(value):
    """A number from text; None for empty, None or bad values."""
    try:
        return float(value)
    except (TypeError, ValueError):      # float(None) is a TypeError
        return None

print([to_float(v) for v in ["12.5", "", None, "n/a", " 7 "]])
```

`to_float` is a small helper you will use in every loader: "a number, or `None`" -
like an informat with the `??` modifier in SAS, which reads a bad value as missing
without a note.

On a real column - the `Outstanding` of `loans_export.csv`, with its decimal commas
and a SAS-style `.` for missing values. Convert, count what failed:

```python run
import csv

def to_float_bg(value):
    try:
        return float(value.replace(",", "."))
    except (AttributeError, ValueError):
        return None

with open("data/loans_export.csv", encoding="utf-8-sig") as file:
    raw = [row["Outstanding"] for row in csv.DictReader(file, delimiter=";")]

values = [to_float_bg(v) for v in raw]
print(len(values), "values,", values.count(None), "missing:", [r for r, v in zip(raw, values) if v is None])
print(f"total of the known values: {sum(v for v in values if v is not None):,.2f}")
```

### Try the formats one by one

Session 7 detected the date format by the shape of the text. With `try`, there is a
shorter way: try each format, and take the first that works:

```python run
from datetime import datetime

FORMATS = ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y%m%d", "%d %b %Y"]

def parse_date(text):
    for fmt in FORMATS:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            pass                  # not this format - try the next one
    return None                   # no format fits

for text in ["2014-06-08", "08.06.2014", "8 Jun 2014", "31.09.2026", "soon"]:
    print(f"{text:>12} -> {parse_date(text)}")
```

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

Rules:

- Catch the **specific** exception you expect (`ValueError`, `KeyError`), not all.
- Keep the `try` block **small**: only the line that can fail.
- Never `pass` silently in a loader: count the error, or write it somewhere.

::: tip Try it
Change `to_float` so that it also accepts the Bulgarian format `"12,50"`: try
`float(value)` first, and if that fails, try again with the comma replaced. Test it
with `"12,50"`, `"12.50"`, `"1 234,5"` and `"abc"`.
:::

## 3. `else` and `finally`

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

```python run
for text in ["12.50", "abc"]:
    try:
        amount = float(text)
    except ValueError:
        print(text, "-> error")
    else:
        print(text, "-> ok, in EUR thousands:", amount / 1000)
    finally:
        print("   (checked", repr(text) + ")")
```

`else` keeps the `try` block small: only the risky line is inside, the code that
**uses** the result is in `else`. `finally` is for clean-up that must happen
whatever comes - closing a connection (session 13), writing the last log line.

A monthly file that may not be there yet - the error is expected, the work on the
file is in `else`:

```python run
for name in ["data/loans.csv", "data/loans_2026-10.csv"]:
    try:
        file = open(name, encoding="utf-8")
    except FileNotFoundError:
        print(name, "-> not delivered yet")
    else:
        with file:
            print(name, "->", sum(1 for line in file) - 1, "rows")
```

`finally` runs even when the error is **not** caught - the clean-up happens, then the
error goes on:

```python run
def load(values):
    print("start")
    try:
        return [float(v) for v in values]
    finally:
        print("clean-up done")

print(load(["1", "2"]))
print(load(["1", "x"]))          # "clean-up done" is printed, then the ValueError
```

### Ask first, or try and catch?

Two styles for the same check:

```python run
rating_of = {"C0001": 3, "C0002": 5}

# LBYL - "look before you leap": check first
client_id = "C9999"
if client_id in rating_of:
    print(rating_of[client_id])
else:
    print("unknown client")

# EAFP - "easier to ask forgiveness than permission": try, and catch
try:
    print(rating_of[client_id])
except KeyError:
    print("unknown client")
```

Both are fine. Python code often uses EAFP when the check would repeat the work
(converting a number to see if it can be converted), and `if` / `get` when the check
is cheap and clear (a key in a dictionary).

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

## 4. `raise` and your own exceptions

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

A wrong **setting** must stop the report before it starts - a report for the wrong
month is worse than no report:

```python run
from datetime import date

def check_report_date(text):
    d = date.fromisoformat(text)                    # a ValueError if not ISO
    next_day = date.fromordinal(d.toordinal() + 1)
    if next_day.day != 1:
        raise ValueError(f"report_date must be the last day of a month, got {text}")
    return d

print(check_report_date("2026-09-30"))
print(check_report_date("2026-09-29"))
```

### Your own exception type

A one-line class (classes: session 11) makes a new kind of exception. Then the
loader can catch **your** data errors, and let real bugs (a `NameError`, a
`TypeError` in your code) stop the script:

```python run
class DataError(ValueError):
    """A value in the input data breaks a rule."""

def check_amount(text):
    try:
        amount = float(text)
    except ValueError:
        raise DataError(f"amount is not a number: {text!r}") from None
    if amount <= 0:
        raise DataError(f"amount must be positive: {amount}")
    return amount

for text in ["125.00", "-75", "12O.50"]:
    try:
        print("ok", check_amount(text))
    except DataError as error:
        print("rejected:", error)
```

`raise ... from None` replaces the original `ValueError` by the clearer `DataError`
(without it, Python shows both). Because `DataError` is a kind of `ValueError`, code
that catches `ValueError` catches it too.

### Re-raise: add context and go on up

Sometimes a function cannot handle an error, but it can add information - the file
and the line - and raise again:

```python run
class DataError(ValueError):
    pass

def load_amounts(lines):
    result = []
    for line_no, text in enumerate(lines, start=2):
        try:
            result.append(float(text))
        except ValueError as error:
            raise DataError(f"payments.csv, line {line_no}: {error}") from error
    return result

print(load_amounts(["10", "20"]))
print(load_amounts(["10", "x", "20"]))
```

### All problems of a row, not only the first

The loader of section 10 stops at the **first** broken rule of a row. For a data
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
| a missing input file, a wrong report date | stop: `raise` - a report on wrong input is worse than no report |
| too many bad rows (say more than 1%) | stop after loading: the input is broken |
| a bug in your code | let it stop - do not catch it |

::: warning `assert` is not for data checks
`assert x > 0, "message"` raises an `AssertionError` when the condition is false - but
Python **removes** all `assert` statements when run with `python -O`. Use `assert` in
tests and for "this can never happen" checks of your own code; check data with `if`
and `raise`.
:::

::: tip Try it
Write `check_currency(code)` that returns the code in capitals if it is one of `EUR`,
`USD`, `GBP` (any case, spaces at the ends allowed), and raises a `DataError` with the
value in the message otherwise.
:::

## 5. Paths with `pathlib`

### A path is an object

The module `pathlib` gives `Path` objects. The operator `/` joins the parts - the same
code works on Windows (`\`) and on Linux / macOS (`/`):

```python run
from pathlib import Path

data = Path("data")
loans_file = data / "loans.csv"

print(loans_file)
print(loans_file.exists(), loans_file.is_file(), data.is_dir())
print(loans_file.name, "|", loans_file.stem, "|", loans_file.suffix, "|", loans_file.parent)
```

| SAS | Python |
|---|---|
| `LIBNAME src "C:\data";` | `src = Path(r"C:\data")` |
| `FILENAME f "C:\data\loans.csv";` | `f = src / "loans.csv"` |
| `%SYSFUNC(FEXIST(f))` | `f.exists()` |

::: warning Windows paths in Python code
A Windows path in a normal string has backslashes - and `"\n"`, `"\t"` are special
characters (session 8). Use a raw string, or forward slashes, which Windows also
accepts:

```python
Path(r"C:\Users\maria\reports\new_loans.csv")     # a raw string
Path("C:/Users/maria/reports/new_loans.csv")      # forward slashes
```
:::

### What is in a folder: `iterdir`

```python run
from pathlib import Path

for path in sorted(Path("data").iterdir()):
    kind = "folder" if path.is_dir() else path.suffix
    print(f"{path.name:<24}{kind}")
```

### Find files: `glob`

`glob(pattern)` lists the files of a folder whose names fit a pattern - `*` is any
text (the shell kind of pattern, not a regex):

```python run
from pathlib import Path

for path in sorted(Path("data").glob("*.csv")):
    print(f"{path.name:<24}{path.stat().st_size:>8} bytes")

print([p.name for p in Path("data").glob("loan*")])
```

### Create folders, read and write whole files

```python run
from pathlib import Path

out = Path("out")
out.mkdir(parents=True, exist_ok=True)          # no error if it exists

note = out / "readme.txt"
note.write_text("Created by the monthly report.\n", encoding="utf-8")
print(note.read_text(encoding="utf-8"))
print(Path.cwd())                                # the current folder
```

`exist_ok=True` makes `mkdir` safe to run every month. `parents=True` creates the
missing folders above it too.

Build the names of output files from parts - the month in the name, another suffix
for the same name:

```python run
from pathlib import Path

out = Path("out")
report = out / "report_2026-09.xlsx"
print(report.with_suffix(".csv"))                       # the same name, another type
print(report.with_name("rejected_2026-09.csv"))
print([out / f"loans_2026-{m:02d}.csv" for m in (7, 8, 9)])
print(report.parts)
```

A missing input file is a `FileNotFoundError` - catch it and say **which** file is
missing:

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
List the files in `data/` that are **not** CSV files, with their size in KB, sorted
by size.
:::

## 6. Text files

### Open, read, close: `with`

Since session 2 you open files with `with open(...) as file:`. `with` **closes** the
file at the end of the block - also when an exception happens inside. Without
`with`, an error can leave the file open (and on Windows, locked).

The **mode** says what you want to do:

| Mode | Means |
|---|---|
| `"r"` | read (the default) |
| `"w"` | write - a new file, or **empty** an existing one |
| `"a"` | append at the end |
| `"x"` | write a new file - an error if it exists |

Always give the `encoding` (session 7):

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

### Read: all at once, or line by line

```python run
with open("data/rating_scale.csv", encoding="utf-8") as file:
    text = file.read()                 # the whole file as one string
print(len(text), "characters")

with open("data/rating_scale.csv", encoding="utf-8") as file:
    lines = file.read().splitlines()   # a list of lines, without "\n"
print(lines[:3])

with open("data/loans.csv", encoding="utf-8") as file:
    count = sum(1 for line in file)    # line by line: little memory, any file size
print(count, "lines")
```

For big files, loop over the file object: only one line is in memory at a time.

The mode `"x"` protects a file that must not be overwritten - the second run fails
instead of destroying the first result:

```python run
from pathlib import Path

Path("out").mkdir(exist_ok=True)
Path("out/final_2026-09.txt").unlink(missing_ok=True)     # start clean for this example

with open("out/final_2026-09.txt", "x", encoding="utf-8") as file:
    file.write("approved figures\n")
try:
    with open("out/final_2026-09.txt", "x", encoding="utf-8") as file:
        file.write("overwritten?\n")
except FileExistsError as error:
    print("not written:", error)
```

Write and read Cyrillic text - the same `encoding` on both sides:

```python run
from pathlib import Path

Path("out").mkdir(exist_ok=True)
Path("out/regions.txt").write_text("София\nПловдив\nВарна\n", encoding="utf-8")
print(Path("out/regions.txt").read_text(encoding="utf-8").splitlines())
print(len(Path("out/regions.txt").read_bytes()), "bytes")     # 2 bytes per Cyrillic letter
```

::: tip Try it
Write the 10 loan ids with the largest outstanding into `out/top10.txt`, one per line,
then read the file back and print the number of lines.
:::

## 7. CSV files

### Read: `csv.reader` and `csv.DictReader`

You know `csv.DictReader` (session 6). `csv.reader` gives each row as a **list**.
Both understand quotes, and both take a `delimiter` for files that are not
comma-separated - like `;` in a Bulgarian Excel export:

```python run
import csv

with open("data/loans_export.csv", encoding="utf-8-sig") as file:
    reader = csv.reader(file, delimiter=";")
    header = next(reader)
    first = next(reader)

print(header)
print(first)
```

(`utf-8-sig` removes the BOM that Excel writes at the start - session 7, Self-study.)

A file **without** a header line: give the column names with `fieldnames`:

```python run
import csv
import io

text = "L000001,800.00,EUR\nL000002,\"1,250.00\",USD\n"      # a file without a header
reader = csv.DictReader(io.StringIO(text), fieldnames=["loan_id", "amount", "currency"])
for row in reader:
    print(row)
```

(`io.StringIO` makes a string behave like an open file - handy for examples and
tests. Note the quoted `"1,250.00"`: one field, not two.)

The values are text. With `DictReader` and a dictionary of converters, a file becomes
typed records:

```python run
import csv

CONVERT = {"amount": float, "outstanding": float, "interest_rate": float,
           "days_past_due": int, "stage": int}

with open("data/loans.csv", encoding="utf-8") as file:
    loans = [{k: CONVERT.get(k, str)(v) for k, v in row.items()} for row in csv.DictReader(file)]

print(loans[0])
```

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

`DictWriter` writes dictionaries; `fieldnames` gives the columns and their order:

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
correctly. Some systems want **every** field in quotes - `quoting=csv.QUOTE_ALL`:

```python run
import csv
import io

buffer = io.StringIO()
writer = csv.writer(buffer, quoting=csv.QUOTE_ALL)
writer.writerow(["L000002", "late, 35 days", 651927.3])
print(buffer.getvalue())
```

### A file for Excel users

A Bulgarian Excel opens CSV files with `;` and a decimal comma best - and it needs
the BOM to see UTF-8 Cyrillic:

```python run
import csv
from pathlib import Path

Path("out").mkdir(exist_ok=True)
rows = [("Sofia", "София", 16, 1234567.89), ("Ruse", "Русе", 28, 98765.4)]

with open("out/regions_for_excel.csv", "w", encoding="utf-8-sig", newline="") as file:
    writer = csv.writer(file, delimiter=";")
    writer.writerow(["region", "name_bg", "clients", "outstanding"])
    for region, name_bg, n, amount in rows:
        writer.writerow([region, name_bg, n, f"{amount:.2f}".replace(".", ",")])

print(Path("out/regions_for_excel.csv").read_text(encoding="utf-8-sig"))
```

| SAS | Python |
|---|---|
| `PROC IMPORT DATAFILE=... DBMS=CSV` | `csv.DictReader(open(...))` |
| `DLM=';'` | `delimiter=";"` |
| `PROC EXPORT ... DBMS=CSV` | `csv.writer(...)`, `writerows` |

::: tip Try it
Read `regions_bg.csv` (cp1251) and write it again as `out/regions_utf8.csv` in UTF-8
with `;` as the separator. Open the result with `read_text` to check it.
:::

## 8. JSON files

JSON (session 6) is the format of configuration files and of web APIs. `json.load`
reads a file into dictionaries and lists; `json.dump` writes one:

```python run
import json

with open("data/report_config.json", encoding="utf-8") as file:
    config = json.load(file)

print(config["report_date"], config["lgd"], config["dpd_buckets"])
print(config["output"]["folder"], type(config["output"]["excel"]))
```

Settings in a file, not in the code: next month you change the file, not the script.

`json.loads` reads JSON from a **string** - for example the answer of a web service:

```python run
import json

answer = '{"base": "EUR", "date": "2026-09-30", "rates": {"USD": 1.1551, "GBP": 0.8702}}'
data = json.loads(answer)
print(data["rates"]["USD"], type(data["rates"]))
print(round(1000 * data["rates"]["GBP"], 2), "GBP for 1000 EUR")
```

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

A summary made from the portfolio - counted with a dictionary (session 6), written
with `sort_keys=True` so that the file looks the same in every run (easy to compare in
Git, session 10):

```python run
import csv
import json
from collections import Counter

with open("data/loans.csv", encoding="utf-8") as file:
    products = Counter(row["product"] for row in csv.DictReader(file))

text = json.dumps({"report_date": "2026-09-30", "loans_by_product": products},
                  indent=2, sort_keys=True)
print(text)
print(json.loads(text)["loans_by_product"]["mortgage"])
```

::: warning JSON knows only a few types
Strings, numbers, `true` / `false`, `null` (`None`), lists and objects (dicts). A
`date` is not one of them - `json.dump` raises a `TypeError`. Store dates as ISO text
(`d.isoformat()`), and convert back after reading. Keys of JSON objects are always
strings: `{1: 323}` comes back as `{"1": 323}`.

```python run
import json
from datetime import date

record = {"loan_id": "L000002", "report_date": date(2026, 9, 30)}
try:
    print(json.dumps(record))
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

## 9. Excel files with `openpyxl`

### Read a workbook

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

A single cell by its address, and the size of a sheet:

```python run
from openpyxl import load_workbook

wb = load_workbook("data/fx_rates.xlsx")
ws = wb["2026-07"]
print(ws["A1"].value, ws["B2"].value, ws.cell(row=2, column=1).value)
print(ws.max_row - 1, "days,", ws.max_column, "columns")
```

All sheets into one dictionary **date -> USD rate**:

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

### Write a workbook

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

Read it back - the number format is stored in the file, the value stays a number:

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
writes whole sheets in one line (`read_excel`, sessions 14 and 16; `to_excel` with
several sheets, session 16) - with openpyxl working inside.

::: info Excel on this site
The site installs `openpyxl` the first time an example uses Excel - the first run of
such an example takes a few seconds longer.
:::

::: tip Try it
Add a third sheet `usd` to `out/stages.xlsx`'s workbook (before saving) with the USD
rates of September: one row per day, `date` and `rate`.
:::

## 10. Loading data with bad records

### The task

`payments_2026-09.csv` has 280 lines; most are fine, some are not:

```python run
with open("data/payments_2026-09.csv", encoding="utf-8") as file:
    lines = file.read().splitlines()

for line_no, line in enumerate(lines, start=1):
    fields = line.split(",")
    if len(fields) != 5 or not fields[3].replace(".", "").isdigit():
        print(line_no, repr(line))
```

The rules of a valid payment:

1. exactly 5 fields;
2. the loan id exists in `loans.csv`;
3. the date is a real date in September 2026 (`yyyy-mm-dd`);
4. the amount is a number greater than 0;
5. the currency is EUR or USD.

A quick profile of the good rows first - how many payments per currency, and the
range of the dates, for the rows that convert without problems:

```python run
import csv
from collections import Counter

with open("data/payments_2026-09.csv", encoding="utf-8") as file:
    rows = [r for r in csv.DictReader(file) if r["pay_date"] and r["currency"]]

print(Counter(r["currency"] for r in rows))
dates = sorted(r["pay_date"] for r in rows)
print("dates from", dates[0], "to", dates[-1])
```

The text dates sort correctly because they are ISO - and `30.09.2026` sorts **after**
every ISO date: one more sign of a bad row.

### One check function per rule, one `try` per row

Each check raises a `DataError` with a clear message. The loader has **one** `try`
per row: the first broken rule rejects the row, with its reason:

```python run
import csv
from datetime import date, datetime

class DataError(ValueError):
    pass

with open("data/loans.csv", encoding="utf-8") as file:
    KNOWN_LOANS = {row["loan_id"] for row in csv.DictReader(file)}

def check_payment(fields):
    """A list of 5 text fields -> a clean record, or a DataError."""
    if len(fields) != 5:
        raise DataError(f"expected 5 fields, got {len(fields)}")
    payment_id, loan_id, pay_date, amount, currency = fields
    if loan_id not in KNOWN_LOANS:
        raise DataError(f"unknown loan {loan_id}")
    try:
        day = datetime.strptime(pay_date, "%Y-%m-%d").date()
    except ValueError:
        raise DataError(f"bad date {pay_date!r}") from None
    if not date(2026, 9, 1) <= day <= date(2026, 9, 30):
        raise DataError(f"date {day} is not in September 2026")
    try:
        value = float(amount)
    except ValueError:
        raise DataError(f"amount is not a number: {amount!r}") from None
    if value <= 0:
        raise DataError(f"amount must be positive: {value}")
    if currency not in ("EUR", "USD"):
        raise DataError(f"unknown currency {currency!r}")
    return {"payment_id": payment_id, "loan_id": loan_id, "pay_date": day,
            "amount": value, "currency": currency}

good, rejected = [], []
with open("data/payments_2026-09.csv", encoding="utf-8", newline="") as file:
    reader = csv.reader(file)
    next(reader)                                       # the header
    for row in reader:
        line_no = reader.line_num
        if not row:                                    # an empty line
            rejected.append((line_no, "", "empty line"))
            continue
        try:
            good.append(check_payment(row))
        except DataError as error:
            rejected.append((line_no, ",".join(row), str(error)))

print(len(good), "payments loaded,", len(rejected), "rejected")
for line_no, text, reason in rejected:
    print(f"line {line_no:>3}: {reason:<40} {text}")
```

`reader.line_num` is the line number in the file - the `_N_` of the log, but for the
file line (the header is line 1).

### The reject file and the summary

The rejected rows go into their own file, with the reason - so that the source system
can fix them. And a short summary, like the end of a SAS log:

```python run
import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

class DataError(ValueError):
    pass

with open("data/loans.csv", encoding="utf-8") as file:
    KNOWN_LOANS = {row["loan_id"] for row in csv.DictReader(file)}

def check_payment(fields):
    if len(fields) != 5:
        raise DataError(f"expected 5 fields, got {len(fields)}")
    payment_id, loan_id, pay_date, amount, currency = fields
    if loan_id not in KNOWN_LOANS:
        raise DataError("unknown loan")
    try:
        day = datetime.strptime(pay_date, "%Y-%m-%d").date()
        value = float(amount)
    except ValueError:
        raise DataError("bad date or amount") from None
    if value <= 0:
        raise DataError("amount not positive")
    if currency not in ("EUR", "USD"):
        raise DataError("unknown currency")
    return loan_id, day, value, currency

good, rejected = [], []
with open("data/payments_2026-09.csv", encoding="utf-8", newline="") as file:
    reader = csv.reader(file)
    header = next(reader)
    for row in reader:
        try:
            good.append(check_payment(row))
        except DataError as error:
            rejected.append({"line": reader.line_num, "reason": str(error), "row": ",".join(row)})

Path("out").mkdir(exist_ok=True)
with open("out/payments_rejected.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["line", "reason", "row"])
    writer.writeheader()
    writer.writerows(rejected)

totals = defaultdict(float)
for loan_id, day, value, currency in good:
    totals[currency] += value

print(f"NOTE: {len(good)} rows read, {len(rejected)} rejected -> out/payments_rejected.csv")
print("NOTE: reasons:", dict(Counter(r["reason"] for r in rejected)))
for currency, total in sorted(totals.items()):
    print(f"NOTE: {currency} total {total:,.2f}")
share = len(rejected) / (len(good) + len(rejected))
if share > 0.01:
    print(f"WARNING: {share:.1%} of the rows were rejected")
```

This is the pattern for every input of a monthly process: **never stop on a bad row,
never lose a bad row, always report**.

The reject file is a normal CSV - the next person reads it with the same tools:

```python run
import csv
from pathlib import Path

path = Path("out/payments_rejected.csv")
if path.exists():
    with open(path, encoding="utf-8") as file:
        for row in csv.DictReader(file):
            print(row["line"], row["reason"])
else:
    print("run the example above first")
```

::: info The same in pandas
pandas has options for bad lines (`pd.read_csv(..., on_bad_lines="skip")`) and turns
bad numbers into `NaN` with `pd.to_numeric(..., errors="coerce")` (session 15). They
are faster - but they do not tell you **why** a row is bad. For an input you must
explain to someone, the loader of this section is the better tool.
:::

::: tip Try it
Add a rule: a payment may not be larger than the outstanding amount of its loan.
You need a dictionary `loan_id -> outstanding` from `loans.csv`. How many rows does
the new rule reject?
:::

## 11. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root:

```bash
python 09-errors-and-files/practice/task1-safe-convert.py
```

The tasks that write files write them into the folder `out/` of the repository (it is
in `.gitignore`).

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-safe-convert.py` | `to_float`, `to_int`, `to_date` with `try` / `except` |
| 2 | `task2-predict-exceptions.py` | Predict the exception, and the output with `else` / `finally` |
| 3 | `task3-raise-checks.py` | Check functions that raise a `DataError` with a clear message |
| 4 | `task4-paths-and-text.py` | `pathlib`: list files, build names, write and read a text file |
| 5 | `task5-csv-json.py` | Read the config, write a CSV report with `DictWriter` |
| 6 | `task6-excel.py` (Optional) | Read the three FX sheets; write a workbook with two sheets |

## Summary

| Topic | Remember |
|-------|----------|
| Exceptions | an error while the code runs; it stops the script unless caught; read the traceback from the bottom |
| Common types | `ValueError`, `TypeError`, `KeyError`, `IndexError`, `ZeroDivisionError`, `FileNotFoundError`, `UnicodeDecodeError` |
| `try` / `except` | catch the specific type; `as error` for the message; a tuple for several types; keep `try` small |
| `else` / `finally` | `else` without an error; `finally` always |
| `raise` | `raise DataError(f"... {value!r}")`; `class DataError(ValueError): pass`; `from None` / `from error` |
| Stop or go on | bad rows: reject and report; bad inputs or settings: raise; bugs: let them stop |
| `pathlib` | `Path("data") / "x.csv"`; `exists`, `name`, `stem`, `suffix`; `glob("*.csv")`; `mkdir(parents=True, exist_ok=True)` |
| Files | `with open(path, mode, encoding="utf-8")`; modes `r`, `w`, `a`, `x`; loop over the file for big files |
| CSV | `csv.reader` / `DictReader`; `delimiter=";"`; write with `newline=""`; `utf-8-sig` for Excel |
| JSON | `json.load(f)`, `json.dump(obj, f, indent=2)`; dates as ISO text |
| Excel | `load_workbook(...)`, `ws.iter_rows(values_only=True)`; `Workbook()`, `ws.append`, `wb.save` |
| Loader | one check per rule, one `try` per row, a reject file with the reason, a summary |

## Homework

1. `09-errors-and-files/homework.py` (in the homework repository): **load the
   September payments** - check every row against the rules, write the valid
   payments and a reject file with the line number and the reason, compute the totals
   per currency and per day, and return a summary. Every check must print `OK`.
2. The practice tasks you did not finish in class.
3. Optional: read `report_config.json` in your loader, and take the report month and
   the allowed currencies from it instead of writing them in the code.

## Self-study

This part is not covered in class. It is for reading at home: a real log for your
scripts, and a loader for a whole folder of monthly files.

### `logging`: the SAS log for Python scripts

`print` is fine while you develop. A script that runs every month needs a **log**:
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
| `NOTE:` | `log.info(...)` |
| `WARNING:` | `log.warning(...)` |
| `ERROR:` | `log.error(...)`, `log.exception(...)` |
| `OPTIONS MPRINT;` for more detail | `level=logging.DEBUG` |

**Exercises**

1. Rewrite the summary of the payments loader (section 10) with `logging` instead of
   `print`: one INFO line per currency, a WARNING if more than 1% of the rows were
   rejected.
2. Add a second handler that also prints the WARNING lines on the screen. (Hint:
   `logging.StreamHandler()`, `setLevel`, `log.addHandler`.)

::: details Answer
```python
log.info("%d rows read, %d rejected", len(good), len(rejected))
for currency, total in sorted(totals.items()):
    log.info("%s total %.2f", currency, total)
if share > 0.01:
    log.warning("%.1f%% of the rows were rejected", share * 100)

screen = logging.StreamHandler()
screen.setLevel(logging.WARNING)
logging.getLogger().addHandler(screen)
```
:::

### A folder of monthly files

A monthly process often reads **all** files of a folder: one per month, one per
branch. `glob` finds them, a regex (session 8) takes the month from the name, and
the loader reads each - one bad file must not stop the others:

```python run
import csv
import re
from pathlib import Path

# make a folder with three monthly files (one of them broken)
folder = Path("out/monthly")
folder.mkdir(parents=True, exist_ok=True)
(folder / "payments_2026-07.csv").write_text("loan_id,amount\nL000001,100.50\nL000002,200\n", encoding="utf-8")
(folder / "payments_2026-08.csv").write_text("loan_id,amount\nL000001,150\n", encoding="utf-8")
(folder / "payments_2026-09.csv").write_bytes("loan_id,amount\nL000003,99\nL000004,сто\n".encode("cp1251"))

totals, failed = {}, []
for path in sorted(folder.glob("payments_*.csv")):
    month = re.search(r"(\d{4}-\d{2})", path.name).group(1)
    try:
        with open(path, encoding="utf-8") as file:
            totals[month] = sum(float(row["amount"]) for row in csv.DictReader(file))
    except (UnicodeDecodeError, ValueError) as error:
        failed.append((path.name, type(error).__name__))

print(totals)
print("failed:", failed)
```

The loop catches the errors **per file**: the good months are loaded, the broken one is
reported with the kind of error.

**Exercises**

1. Change the loop so that a file with a bad amount is still loaded, without the bad
   rows (use the `to_float` of section 2), and the number of skipped rows per file is
   reported.
2. Sort the files by the month in their name, not by the name itself. When is that
   different? (Hint: `payments_2026-10.csv` and `payments_2026-9.csv`.)

::: details Answer
1. Inside the `with`: `values = [to_float(row["amount"]) for row in csv.DictReader(file)]`,
   then `totals[month] = sum(v for v in values if v is not None)` and
   `skipped[path.name] = values.count(None)`. The `UnicodeDecodeError` still needs the
   `try`.
2. `sorted(folder.glob(...), key=lambda p: tuple(int(x) for x in re.search(r"(\d{4})-(\d{1,2})", p.name).groups()))`.
   Sorting by name puts `2026-10` before `2026-9`, because text is compared letter by
   letter - another reason for two-digit months in file names.
:::

## Read more

- Python tutorial: [Errors and exceptions](https://docs.python.org/3/tutorial/errors.html),
  [Reading and writing files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
- Reference: [Built-in exceptions](https://docs.python.org/3/library/exceptions.html),
  [`pathlib`](https://docs.python.org/3/library/pathlib.html),
  [`csv`](https://docs.python.org/3/library/csv.html),
  [`json`](https://docs.python.org/3/library/json.html),
  [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [openpyxl tutorial](https://openpyxl.readthedocs.io/en/stable/tutorial.html)
- Real Python: [Python exceptions: an introduction](https://realpython.com/python-exceptions/),
  [Python's pathlib module](https://realpython.com/python-pathlib/)

**Next session:** modules, packages and Git - turn your functions into a module you
can import, set up a project folder, and keep its history in Git.
