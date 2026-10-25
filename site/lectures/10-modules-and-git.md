---
title: 10. Modules, packages, Git and GitHub
---

# 10. Modules, packages, Git and GitHub

<div class="lecture-meta">
  <span>Session 10</span><span>practice: <code>10-modules-and-git/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- import modules in all their forms, and know where Python finds them;
- put your own functions into a **module**, and import it from a script or a
  notebook - the Python version of a SAS autocall macro library;
- organise a project folder so that it can be run again, by you or by a colleague;
- use the most useful parts of the standard library: dates and month ends,
  statistics, counters, settings from the environment;
- keep the history of your code in **Git**: commit, look back, branch and merge;
- work with a remote repository on GitHub: clone, push, pull, and a pull request.

From SAS to Python - the same reusable library, two ways:

```sas
/* the macros live in C:\project\macros, one file per macro */
options sasautos=("C:\project\macros" sasautos);
%include "C:\project\macros\formats.sas";

%dpd_bucket(days=45);
```

```python
# portfolio_utils.py lives next to the script (or in a package folder)
from portfolio_utils import dpd_bucket, expected_loss

print(dpd_bucket(45))
```

A **module** is just a `.py` file. Everything you defined in it - functions,
constants - can be imported by another file. That is how the code of sessions 4 - 9
becomes a library you use every month.

## 1. `import`

### The forms of `import`

You have used `import` since session 1. The four forms:

```python run
import math                              # the module; use it with its name
print(math.sqrt(16))

from math import sqrt, floor             # names from the module
print(sqrt(16), floor(2.7))

import statistics as st                  # a short name
print(st.mean([1, 2, 3, 4]))

from statistics import median as med     # a name, renamed
print(med([1, 5, 2]))
```

| Form | Use it when |
|---|---|
| `import math` | you use a few things, and want the reader to see where they come from (`math.sqrt`) |
| `from math import sqrt` | you use a name often, and it is clear |
| `import pandas as pd` | the module has a common short name: `pd`, `np`, `plt` |
| `from x import *` | **never** in your code: it hides where the names come from, and can overwrite your own |

### What `import` does

The first `import` of a module **runs** its file from top to bottom, and keeps the
result in `sys.modules`. A second `import` of the same module does not run it again -
it takes the module from there:

```python run
import sys
import math

print("math" in sys.modules)
print(type(math), math.__name__)
print([name for name in dir(math) if not name.startswith("_")][:12])
```

See it with a module of your own that prints when it runs - imported twice, it prints
once:

```python run
import sys
from pathlib import Path

Path("hello_module.py").write_text('print("hello_module runs now")\nRATE = 0.45\n', encoding="utf-8")
sys.modules.pop("hello_module", None)      # only on this page: forget an earlier import

import hello_module                        # runs the file: prints
import hello_module                        # taken from sys.modules: no print
print(hello_module.RATE)
```

`dir(module)` lists its names; `help(module.function)` shows the docstring (session
4). The docstring is also in `__doc__`:

```python run
import statistics

print(statistics.median.__doc__.splitlines()[0])
print(statistics.__doc__.splitlines()[0])
```

An imported name is a normal variable of **your** file. Giving it a new value changes
it only in your file, not in the module:

```python run
from math import pi
import math

pi = 3                       # your name pi now means 3
print(pi, math.pi)           # the module is not changed
```

A module can also be imported by a name that is only known when the script runs -
for example from a setting:

```python run
import importlib

for name in ["statistics", "json", "no_such_module"]:
    try:
        module = importlib.import_module(name)
        print(name, "->", module.__name__)
    except ModuleNotFoundError as error:
        print(name, "->", error)
```

### Where Python looks: `sys.path`

`import name` looks for `name.py` (or a folder `name/`) in the folders of `sys.path`,
in order:

1. the folder of the script you run (or the current folder in a notebook);
2. the folders of the standard library;
3. `site-packages` of the active environment - where `pip` installs.

```python run
import sys

for folder in sys.path[:4]:
    print(repr(folder))
```

Which file was imported, and which version? `__file__` and `__version__` answer "is
this the pandas of my virtual environment?" - the first question when a script works
on one computer and not on another:

```python run
import csv
import pandas

print(csv.__file__)
print(pandas.__file__)
print(pandas.__version__)
```

In your terminal, the path of `pandas` must be inside the `.venv` folder of your
project.

::: warning Do not name your file like a module
A file `statistics.py`, `csv.py` or `pandas.py` in your project folder **hides** the
real module: `import csv` imports **your** file, and nothing works. Name your files
for what they do: `load_payments.py`, `portfolio_utils.py`.

```python run
import sys
from pathlib import Path

folder = Path("shadow_demo")
folder.mkdir(exist_ok=True)
(folder / "statistics.py").write_text("print('this is MY statistics.py!')\n", encoding="utf-8")

sys.path.insert(0, str(folder))          # as if it were the folder of your script
sys.modules.pop("statistics", None)      # only on this page
import statistics
print(hasattr(statistics, "mean"))       # False - the real module is hidden

sys.path.remove(str(folder))             # clean up for the next examples
del sys.modules["statistics"]
```
:::

::: tip Try it
Import `date` from `datetime` in two ways - `import datetime` and `from datetime
import date` - and create the date 2026-09-30 with each. Why is `datetime.datetime`
not a typo?
:::

## 2. Your own module

### Write the module

A module is a `.py` file with functions and constants - and **no** code that does
work when it is imported. This one collects functions of sessions 4 - 8:

```python
"""portfolio_utils.py - functions for the loan portfolio."""
import re

LGD = 0.45


def dpd_bucket(days_past_due):
    """The bucket of days past due: current, 1-30, 31-90, 90+."""
    if days_past_due == 0:
        return "current"
    if days_past_due <= 30:
        return "1-30"
    if days_past_due <= 90:
        return "31-90"
    return "90+"


def expected_loss(pd_value, ead, lgd=LGD):
    """EL = PD * LGD * EAD."""
    return pd_value * lgd * ead


def is_loan_id(text):
    """True for an L and six digits."""
    return re.fullmatch(r"L\d{6}", text) is not None
```

Save it as `portfolio_utils.py` next to your script, and import it:

```python
from portfolio_utils import dpd_bucket, expected_loss

print(dpd_bucket(45), expected_loss(0.02, 100000))
```

On this page, an example can write the file and import it - every example has the
same folder:

```python run
from pathlib import Path

Path("portfolio_utils.py").write_text('''"""portfolio_utils.py - functions for the loan portfolio."""
import re

LGD = 0.45


def dpd_bucket(days_past_due):
    """The bucket of days past due: current, 1-30, 31-90, 90+."""
    if days_past_due == 0:
        return "current"
    if days_past_due <= 30:
        return "1-30"
    if days_past_due <= 90:
        return "31-90"
    return "90+"


def expected_loss(pd_value, ead, lgd=LGD):
    """EL = PD * LGD * EAD."""
    return pd_value * lgd * ead


def is_loan_id(text):
    """True for an L and six digits."""
    return re.fullmatch(r"L\\d{6}", text) is not None
''', encoding="utf-8")

import portfolio_utils

print(portfolio_utils.dpd_bucket(45))
print(portfolio_utils.expected_loss(0.02, 100000))
print(portfolio_utils.LGD, portfolio_utils.is_loan_id("L000001"))
print(portfolio_utils.__file__)
```

Now any example can import it - like a script in the same folder:

```python run
from portfolio_utils import dpd_bucket, is_loan_id
import csv

with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))

print(all(is_loan_id(l["loan_id"]) for l in loans))
print(sorted({dpd_bucket(int(l["days_past_due"])) for l in loans}))
```

(Run the example above first - it writes the file.)

What is in the module, and the expected loss of the portfolio by stage with its
functions:

```python run
import csv
import portfolio_utils as pu

print([name for name in dir(pu) if not name.startswith("_")])

el_by_stage = {}
with open("data/loans.csv", encoding="utf-8") as file:
    for loan in csv.DictReader(file):
        stage = int(loan["stage"])
        pd_value = {1: 0.01, 2: 0.10, 3: 1.0}[stage]          # a simple PD per stage
        el_by_stage[stage] = el_by_stage.get(stage, 0) + pu.expected_loss(pd_value, float(loan["outstanding"]))
print({s: round(v, 2) for s, v in sorted(el_by_stage.items())})
```

The buckets of the whole portfolio, counted with the function of the module and a
`Counter` (session 6):

```python run
import csv
from collections import Counter
from portfolio_utils import dpd_bucket

with open("data/loans.csv", encoding="utf-8") as file:
    buckets = Counter(dpd_bucket(int(row["days_past_due"])) for row in csv.DictReader(file))

for bucket in ["current", "1-30", "31-90", "90+"]:
    print(f"{bucket:<8}{buckets[bucket]:>5}")
```

::: warning `from module import CONSTANT` makes a copy of the name
`from portfolio_utils import LGD` creates **your** variable `LGD`, with the value the
module had at the import. A later change of `portfolio_utils.LGD` does not reach it.
Read settings through the module (`pu.LGD`) - or better, pass them as arguments:

```python run
import portfolio_utils as pu
from portfolio_utils import LGD

pu.LGD = 0.40              # a change in the module
print(LGD, pu.LGD)         # your copy is still the old value
pu.LGD = 0.45              # back, for the next examples
```
:::

### The `__main__` guard

Every module has a name in `__name__`. When a file is **run** (`python
portfolio_utils.py`), its `__name__` is `"__main__"`; when it is **imported**, its
`__name__` is the module name. The guard runs code only when the file is run:

```python
"""portfolio_utils.py"""

def dpd_bucket(days_past_due):
    ...

if __name__ == "__main__":
    # only when run as a script: a quick self-test
    assert dpd_bucket(0) == "current"
    assert dpd_bucket(45) == "31-90"
    print("portfolio_utils: all checks passed")
```

```python run
import sys
from pathlib import Path

Path("guard_demo.py").write_text('''print("guard_demo: __name__ is", __name__)

def double(x):
    return 2 * x

if __name__ == "__main__":
    print("guard_demo was RUN, not imported")
''', encoding="utf-8")

sys.modules.pop("guard_demo", None)       # only on this page: forget an earlier import
import guard_demo                          # the guard code does not run
print(guard_demo.double(21))
```

And **run** as a script - `runpy` does from Python what `python guard_demo.py` does in
the terminal:

```python run
import runpy

result = runpy.run_path("guard_demo.py", run_name="__main__")
```

So a module can be both: a library to import, and a script with a self-test.

::: info Only on this page: `sys.modules.pop(...)`
All examples of a page run in the same Python, so a module imported by an earlier
example stays in `sys.modules`. `sys.modules.pop("name", None)` makes the next `import`
read the file again. In your own scripts you do not need it.
:::

### Change the module, use it again

A script reads the module **when it starts**, so after a change, run the script again.
In a **Jupyter notebook** the kernel keeps the old version - restart the kernel, or
switch on automatic reloading once, at the top of the notebook:

```python
%load_ext autoreload
%autoreload 2
from portfolio_utils import dpd_bucket      # now picks up every saved change
```

In a script or a running Python, `importlib.reload` reads a module again:

```python run
import importlib
from pathlib import Path

import portfolio_utils                      # written by an example above

text = Path("portfolio_utils.py").read_text(encoding="utf-8")
Path("portfolio_utils.py").write_text(text.replace("LGD = 0.45", "LGD = 0.40"), encoding="utf-8")

print(portfolio_utils.LGD)                  # still the old value
importlib.reload(portfolio_utils)
print(portfolio_utils.LGD)                  # the new value
```

::: tip Try it
Add a function `stage(days_past_due, rating)` (session 4) to `portfolio_utils.py`
with `write_text`, reload the module, and call it for `(45, 5)` and `(0, 10)`.
:::

## 3. Packages and the layout of a project

### A package: a folder of modules

When one module grows too big, split it into several, in a **folder** with a file
`__init__.py` (it can be empty). The folder is a **package**; import its modules with
a point:

```text
portfolio/
    __init__.py
    cleaning.py         clean_client_id, parse_amount, parse_date
    rules.py            dpd_bucket, stage, expected_loss
    loading.py          load_payments, DataError
```

```python
from portfolio.rules import dpd_bucket
from portfolio import cleaning

print(dpd_bucket(45), cleaning.parse_amount("1 234,56"))
```

```python run
from pathlib import Path
import sys

package = Path("portfolio")
package.mkdir(exist_ok=True)
(package / "__init__.py").write_text('"""The portfolio package."""\n', encoding="utf-8")
(package / "rules.py").write_text('''def dpd_bucket(days):
    return "current" if days == 0 else "1-30" if days <= 30 else "31-90" if days <= 90 else "90+"
''', encoding="utf-8")

for name in [n for n in sys.modules if n.startswith("portfolio.") or n == "portfolio"]:
    sys.modules.pop(name)                  # only on this page
from portfolio.rules import dpd_bucket
print([dpd_bucket(d) for d in (0, 15, 45, 120)])
```

What is in a package - its modules, found by `pkgutil` (after the example above):

```python run
import pkgutil
import portfolio

print(portfolio.__path__)
print([module.name for module in pkgutil.iter_modules(portfolio.__path__)])
```

`__init__.py` can **re-export** the most used names, so that users write
`from portfolio import dpd_bucket` without knowing the module inside:

```python run
from pathlib import Path
import sys

Path("portfolio/__init__.py").write_text('"""The portfolio package."""\nfrom .rules import dpd_bucket\n', encoding="utf-8")
for name in [n for n in sys.modules if n.startswith("portfolio.") or n == "portfolio"]:
    sys.modules.pop(name)                  # only on this page

import portfolio
print(portfolio.dpd_bucket(45))
print(sorted(p.name for p in Path("portfolio").glob("*.py")))
```

The point in `from .rules import ...` means "the module `rules` of **this** package" - a
*relative* import, possible only inside a package.

### The layout of a data project

A layout that colleagues recognise - and that works with Git (section 6):

```text
monthly-portfolio-report/
    README.md               what it is, how to run it
    requirements.txt        the packages, with versions
    .gitignore              what Git must NOT keep: .venv, data, output
    portfolio/              the package: the reusable code
        __init__.py
        cleaning.py
        rules.py
    report.py               the script that is run every month
    notebooks/              exploration, ad-hoc analysis
    data/                   the input files - NOT in Git
    out/                    the results - NOT in Git
    tests/                  checks of the functions (optional)
```

Run the script from the project folder: `python report.py`. A module **inside** the
package that should be run is started with `-m` and its dotted name:

::: code-group
```powershell [Windows]
cd C:\Users\maria\monthly-portfolio-report
.venv\Scripts\activate
python report.py
python -m portfolio.rules
```
```bash [Linux / macOS]
cd ~/monthly-portfolio-report
source .venv/bin/activate
python report.py
python -m portfolio.rules
```
:::

A small script can make the skeleton of a new project - the same folders every time:

```python run
from pathlib import Path

project = Path("monthly-portfolio-report")
for folder in ["portfolio", "notebooks", "data", "out"]:
    (project / folder).mkdir(parents=True, exist_ok=True)
(project / "portfolio" / "__init__.py").touch()
(project / "README.md").write_text("# Monthly portfolio report\n\nRun: python report.py\n", encoding="utf-8")
(project / ".gitignore").write_text(".venv/\n__pycache__/\ndata/\nout/\n", encoding="utf-8")

for path in sorted(project.rglob("*")):
    print("    " * (len(path.parts) - 2) + path.name + ("/" if path.is_dir() else ""))
```

::: warning A path like `"data/loans.csv"` depends on where you start the script
A relative path is read from the **current folder** of the terminal, not from the
folder of the script. `python report.py` works in the project folder, and fails with
`FileNotFoundError` when started from another one:

```python run
import os

os.chdir("data")                         # as if the terminal were in another folder
try:
    open("data/loans.csv", encoding="utf-8")
except FileNotFoundError as error:
    print("FileNotFoundError:", error)
finally:
    os.chdir("..")                       # back, for the next examples
```

In a script, build the paths from the folder of the script itself:
`DATA = Path(__file__).parent / "data"` - then it works from any folder. (In a
notebook there is no `__file__`; start Jupyter in the project folder.)
:::

| SAS | Python |
|---|---|
| `/programs/report.sas` | `report.py` |
| `/macros/*.sas` + `SASAUTOS` | the package `portfolio/` |
| `%INCLUDE "common.sas"` | `import portfolio.common` |
| `LIBNAME in "/data"` | `DATA = Path("data")` at the top of `report.py` |

::: tip Try it
Add a module `cleaning.py` with `squeeze(s)` (session 7) to the `portfolio` package
of the example above, and import it with `from portfolio.cleaning import squeeze`.
:::

## 4. A tour of the standard library

"Batteries included" (session 1): Python comes with modules for most daily needs.
The ones an analyst uses most:

### `datetime` and `calendar`: report dates

Session 7 introduced `date`, `datetime` and `timedelta`. Month ends - the report dates -
need the number of days of a month: `calendar.monthrange(year, month)` gives the
weekday of the 1st and the number of days:

```python run
import calendar
from datetime import date

def month_end(d):
    """The last day of the month of d - INTNX('month', d, 0, 'e')."""
    return d.replace(day=calendar.monthrange(d.year, d.month)[1])

print(month_end(date(2026, 2, 10)), month_end(date(2028, 2, 10)), month_end(date(2026, 9, 1)))
print(calendar.isleap(2028))
```

**Adding months** is not in `datetime` - a month has no fixed length. A small function
does it the way SAS `INTNX('month', d, n, 'e')` does, at month ends:

```python run
import calendar
from datetime import date

def add_months(d, n):
    """The month end n months after (or before) the month of d."""
    month_index = d.year * 12 + (d.month - 1) + n
    year, month = divmod(month_index, 12)
    return date(year, month + 1, calendar.monthrange(year, month + 1)[1])

report_date = date(2026, 9, 30)
print(add_months(report_date, 1), add_months(report_date, -1), add_months(report_date, -12))
print([add_months(report_date, -k) for k in range(3)])           # the last three month ends
```

The months between two dates - `INTCK('month', a, b)`:

```python run
from datetime import date

def months_between(a, b):
    return (b.year - a.year) * 12 + (b.month - a.month)

print(months_between(date(2019, 4, 16), date(2026, 9, 30)))
```

Quarter ends, and the working days between two dates:

```python run
import calendar
from datetime import date, timedelta

def quarter_end(d):
    month = (d.month - 1) // 3 * 3 + 3
    return date(d.year, month, calendar.monthrange(d.year, month)[1])

def working_days(start, end):
    """Monday to Friday from start to end, both included (no holidays)."""
    days = (end - start).days + 1
    return sum(1 for k in range(days) if (start + timedelta(days=k)).weekday() < 5)

print(quarter_end(date(2026, 8, 15)), quarter_end(date(2026, 11, 2)))
print(working_days(date(2026, 9, 1), date(2026, 9, 30)))
print(date(2026, 9, 30).isocalendar())          # ISO year, week, weekday
```

`calendar` also prints a month - handy to check a date in a hurry:

```python run
import calendar

print(calendar.month(2026, 9))
```

(pandas has all of this built in - `pd.offsets.MonthEnd`, `Period` - session 16.)

### `statistics`: `PROC MEANS` and `PROC UNIVARIATE` for a list

```python run
import csv
import statistics as st

with open("data/loans.csv", encoding="utf-8") as file:
    rates = [float(r["interest_rate"]) for r in csv.DictReader(file)]

print("n      ", len(rates))
print("mean   ", round(st.mean(rates), 3))
print("median ", round(st.median(rates), 2))
print("stdev  ", round(st.stdev(rates), 3))          # the sample standard deviation
print("deciles", [round(q, 2) for q in st.quantiles(rates, n=10)])
```

By group - `PROC MEANS ... CLASS stage` - with a dictionary of lists (session 6) and
`statistics` per group:

```python run
import csv
import statistics as st
from collections import defaultdict

rates_of = defaultdict(list)
with open("data/loans.csv", encoding="utf-8") as file:
    for loan in csv.DictReader(file):
        rates_of[int(loan["stage"])].append(float(loan["interest_rate"]))

for stage, rates in sorted(rates_of.items()):
    print(f"stage {stage}: n={len(rates):>3}  mean={st.mean(rates):5.2f}  median={st.median(rates):5.2f}")
```

Since Python 3.10, `statistics` also has `correlation` and `linear_regression`:

```python run
import csv
import statistics as st

with open("data/loans.csv", encoding="utf-8") as file:
    loans = list(csv.DictReader(file))
rates = [float(l["interest_rate"]) for l in loans]
dpd = [int(l["days_past_due"]) for l in loans]
print(round(st.correlation(rates, dpd), 3))
```

`stdev` is the sample standard deviation (like SAS `STD`), `pstdev` the population
one. `quantiles(..., n=4)` gives the quartiles; note that the methods of computing
quantiles differ a little between SAS, SQL and Python.

### `collections`: more containers

You know `Counter` and `defaultdict` (session 6). Two more:

```python run
from collections import namedtuple, deque

Loan = namedtuple("Loan", ["loan_id", "product", "outstanding"])
loan = Loan("L000002", "investment", 651927.30)
print(loan.product, loan.outstanding, loan[0])         # by name and by position

last_three = deque(maxlen=3)                            # keeps only the last 3
for month_total in [128.4, 129.1, 130.2, 129.6, 131.4]:
    last_three.append(month_total)
print(list(last_three), round(sum(last_three) / 3, 2))  # a 3-month moving average
```

A `namedtuple` is a tuple with names for its positions - a light record (session 3,
Advanced). Classes (session 11) do the same with more power. Rows of a CSV file as
named tuples:

```python run
import csv
from collections import namedtuple

with open("data/rating_scale.csv", encoding="utf-8") as file:
    reader = csv.reader(file)
    Grade = namedtuple("Grade", next(reader))         # the header gives the field names
    scale = [Grade._make(row) for row in reader]

print(scale[3])
print(scale[3].grade, scale[3].pd_max)
```

`ChainMap` looks up a key in several dictionaries, in order - the layers of the
settings of a report: the command line wins over the environment, which wins over the
config file:

```python run
import json
from collections import ChainMap

with open("data/report_config.json", encoding="utf-8") as file:
    from_file = json.load(file)
from_environment = {"lgd": 0.40}
from_command_line = {"report_date": "2026-10-31"}

settings = ChainMap(from_command_line, from_environment, from_file)
print(settings["report_date"], settings["lgd"], settings["currency"])
```

### `math`: careful sums

```python run
import math

amounts = [0.1] * 10
total = 0.0
for a in amounts:                                       # a loop adds the rounding errors
    total += a
print(total, math.fsum(amounts))                        # fsum adds floats exactly
print(total == 1.0, math.isclose(total, 1.0))           # compare floats with a tolerance
print(round(math.log(1.05), 6), math.exp(0.05))         # continuous rates
```

`math.prod` multiplies - compound growth over several periods:

```python run
import math

monthly_growth = [0.012, -0.004, 0.008, 0.010]
print(round(math.prod(1 + g for g in monthly_growth) - 1, 5))      # the growth of the 4 months
```

### Small helpers for reports

`pprint` prints nested dictionaries and lists so that you can read them:

```python run
import json
from pprint import pprint

with open("data/report_config.json", encoding="utf-8") as file:
    pprint(json.load(file), width=60)
```

Dates in file names - ISO order, so that the files sort by date:

```python run
from datetime import date

report_date = date(2026, 9, 30)
print(f"portfolio_report_{report_date:%Y-%m}.xlsx")
print(f"rejected_{report_date:%Y%m%d}.csv")
```

`string.Template` fills `$names` in a text - a mail or a report header that a
colleague can edit without knowing Python:

```python run
from string import Template

text = Template("Report $report_date: $loans loans, outstanding EUR $outstanding.")
print(text.substitute(report_date="30.09.2026", loans=400, outstanding="131,370,708.60"))
```

`namedtuple` records turn into dictionaries (for `csv.DictWriter`) and can be copied
with one field changed:

```python run
from collections import namedtuple

Loan = namedtuple("Loan", ["loan_id", "stage", "outstanding"])
loan = Loan("L000002", 2, 651927.30)
print(loan._asdict())
print(loan._replace(stage=3), loan)            # a new record; the old one is unchanged
```

`itertools.batched` (Python 3.12+) cuts a list into pieces - for example ids for SQL
`IN (...)` lists, which many databases limit to 1000 values:

```python run
from itertools import batched

loan_ids = [f"L{n:06d}" for n in range(1, 2501)]
for chunk in batched(loan_ids, 1000):
    print(len(chunk), chunk[0], "...", chunk[-1])
```

`difflib.get_close_matches` finds the most similar known value - a typo in a city or a
product name:

```python run
from difflib import get_close_matches

regions = ["Sofia", "Plovdiv", "Varna", "Burgas", "Ruse", "Stara Zagora", "Pleven"]
for typed in ["Sofiq", "Plovdif", "Stara Zag.", "Vidin"]:
    print(typed, "->", get_close_matches(typed, regions, n=1, cutoff=0.6))
```

### `random`: a sample for a manual check

An auditor wants 10 loans chosen at random to check by hand. `random.seed` makes the
choice **repeatable** - the same seed gives the same sample next week:

```python run
import csv
import random

with open("data/loans.csv", encoding="utf-8") as file:
    loan_ids = [row["loan_id"] for row in csv.DictReader(file)]

random.seed(2026)
first = sorted(random.sample(loan_ids, 10))
random.seed(2026)
again = sorted(random.sample(loan_ids, 10))       # the same seed: the same sample
other = sorted(random.sample(loan_ids, 10))       # no new seed: the generator went on

print(first)
print(first == again, first == other)
```

Like `PROC SURVEYSELECT ... SEED=` in SAS.

### `hashlib`: did the input change?

A checksum of a file is a short text that changes when **any** byte of the file
changes. Keep it with the report: next month you can prove which input was used:

```python run
import hashlib
from pathlib import Path

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

print(sha256("data/loans.csv")[:16], "...")
print(sha256("data/clients.csv")[:16], "...")
```

### `time`: how long it takes

```python run
import csv
import time

start = time.perf_counter()
with open("data/balances_monthly.csv", encoding="utf-8") as file:
    rows = sum(1 for _ in csv.DictReader(file))
print(rows, "rows in", round(time.perf_counter() - start, 3), "s")
```

### `os` and `sys`: the environment

Settings that differ between computers or users - a folder, a server name, a
**password** - do not belong in the code. Read them from the **environment
variables**:

```python run
import os
import sys

print(os.getenv("REPORT_FOLDER", "out"))               # a default if it is not set
print(int(os.getenv("MAX_REJECTED", "50")))             # a number: convert the text
os.environ["REPORT_FOLDER"] = "reports"                 # set it (only for this run)
print(os.getenv("REPORT_FOLDER"))
print(sys.version.split()[0], sys.platform)
```

Session 13 reads the password of a database this way - never write a password into a
script or a notebook that goes into Git.

::: code-group
```powershell [Windows]
$env:REPORT_FOLDER = "C:\reports"     # PowerShell, for this terminal
python report.py
```
```bash [Linux / macOS]
export REPORT_FOLDER=~/reports
python report.py
```
:::

Old code often uses `os.path` instead of `pathlib` - the same jobs, as functions on
strings:

```python run
import os.path
from pathlib import Path

print(os.path.join("data", "loans.csv"), Path("data") / "loans.csv")
print(os.path.exists("data/loans.csv"), os.path.splitext("loans.csv"))
print(os.path.basename("data/loans.csv"), Path("data/loans.csv").name)
```

### `shutil`: copy and archive

```python run
import shutil
from pathlib import Path

Path("out").mkdir(exist_ok=True)
shutil.copy("data/rating_scale.csv", "out/rating_scale_backup.csv")
archive = shutil.make_archive("out/inputs_2026-09", "zip", root_dir="data")
print(Path("out/rating_scale_backup.csv").exists(), Path(archive).name, Path(archive).stat().st_size, "bytes")
```

And look into the archive with `zipfile`:

```python run
import zipfile

with zipfile.ZipFile("out/inputs_2026-09.zip") as archive:
    names = archive.namelist()
    print(len(names), "files, e.g.", sorted(names)[:3])
    print(archive.read("rating_scale.csv").decode("utf-8").splitlines()[0])
```

::: tip Try it
Compute the quartiles of the outstanding amounts of the stage 1 loans with
`statistics.quantiles(..., n=4)`. Then the median of the days past due of the loans
that are late at all.
:::

## 5. `pip` and virtual environments, again

Session 1 set up the environment of the Homework repository. The rules, once more,
now that you will make projects of your own:

- **one virtual environment per project**, in the project folder (`.venv`), never
  installed into the Python of the computer;
- the packages of the project in `requirements.txt`, with the versions you tested
  (`pip freeze`);
- `.venv` is **not** in Git - `requirements.txt` is, and it rebuilds `.venv` on any
  computer.

::: code-group
```powershell [Windows]
py -m venv .venv
.venv\Scripts\activate
python -m pip install pandas openpyxl
python -m pip freeze > requirements.txt
```
```bash [Linux / macOS]
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pandas openpyxl
python -m pip freeze > requirements.txt
```
:::

The name you install is not always the name you import:

| `pip install` | `import` |
|---|---|
| `pandas` | `pandas` |
| `openpyxl` | `openpyxl` |
| `python-dateutil` | `dateutil` |
| `scikit-learn` | `sklearn` |
| `pyyaml` | `yaml` |

```python run
import importlib.metadata as md
import pandas, numpy                     # on this page: load them first

for package in ["pandas", "numpy", "python-dateutil"]:
    try:
        print(f"{package:<16}{md.version(package)}")
    except md.PackageNotFoundError:
        print(f"{package:<16}not installed")
```

Which packages does a package need? The same as `pip show` lists under `Requires`:

```python run
import importlib.metadata as md
import pandas                            # on this page: load it first

for requirement in md.requires("pandas"):
    if "extra ==" not in requirement:     # skip the optional extras
        print(requirement)
```

The part after `;` is a condition: `tzdata` is needed only on Windows (and on this
site).

Does the environment match `requirements.txt`? A check at the start of a monthly
script saves an hour of searching later:

```python run
import importlib.metadata as md
import numpy, pandas                     # on this page: load them first

requirements = """numpy>=2.0
pandas>=2.2
"""
for line in requirements.splitlines():
    name, minimum = line.split(">=")
    installed = md.version(name)
    as_numbers = lambda v: tuple(int(x) for x in v.split(".")[:2])
    ok = as_numbers(installed) >= as_numbers(minimum)
    print(f"{name:<8} needs >= {minimum:<6} has {installed:<8} {'ok' if ok else 'TOO OLD'}")
```

Are you in a virtual environment at all? In a `.venv`, `sys.prefix` (the environment)
differs from `sys.base_prefix` (the Python it was made from):

```python run
import sys

print(sys.prefix)
print(sys.base_prefix)
print("in a virtual environment:", sys.prefix != sys.base_prefix)
```

On this page the answer is `False` - the site has no `.venv`. Run the same three lines
in the terminal of your Homework folder: `True`.

::: details Advanced: uv
[uv](https://docs.astral.sh/uv/) is a newer, much faster tool that does the work of
`venv` and `pip` (and installs Python versions too): `uv venv`, `uv pip install -r
requirements.txt`. It is free and popular, but `venv` + `pip` come with Python and are
enough for this course.
:::

::: tip Try it
In your Homework folder, run `python -m pip list` and find the versions of pandas and
numpy. Then `python -m pip show openpyxl`: which packages does it need?
:::

## 6. Git: versions of your code

### Why

Without version control, versions of a program look like this: `report.sas`,
`report_v2.sas`, `report_v2_final.sas`, `report_v2_final_MARIA.sas`. Which one made
last month's numbers? What changed between them?

**Git** keeps the full history of a project folder:

- every saved version (**commit**) with its date, author and a message;
- what changed in each one, line by line;
- the way back to any earlier version;
- parallel lines of work (**branches**) that can be merged.

Git runs on your computer (you installed it for session 1). **GitHub**, GitLab and
Azure DevOps are websites that keep a copy of a repository, for sharing and backup
(section 8).

### Three places

```text
  working folder          staging area             repository (.git)
  (your files)            (the next commit)        (the history)
       |    git add file       |    git commit -m "..."   |
       | --------------------> | -----------------------> |
       |                       |                          |
       | <---------------------------- git restore file   |
```

- the **working folder** - the files you edit;
- the **staging area** - the changes you have chosen for the next commit (`git add`);
- the **repository** - the commits, in the hidden folder `.git`.

### The first repository

In a terminal, in the project folder (the commands are the same on Windows and
Linux):

```bash
git init                                  # make this folder a repository (once)
git status                                # what changed since the last commit
git add portfolio_utils.py report.py      # choose the changes for the commit
git commit -m "Add the DPD bucket and the EL functions"
git log --oneline                         # the history, one line per commit
```

Who you are - once per computer (the [how-to page](/how-to#practice-and-homework)
did this):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### See the changes: `diff`

What `git diff` shows is a **unified diff**: `-` for a removed line, `+` for an added
one. The module `difflib` makes the same for two versions of a text:

```python run
import difflib

before = """LGD = 0.45
BUCKETS = (0, 30, 90)
REPORT = "monthly"
""".splitlines(keepends=True)
after = """LGD = 0.40
BUCKETS = (0, 30, 90)
REPORT = "monthly"
CURRENCY = "EUR"
""".splitlines(keepends=True)

print("".join(difflib.unified_diff(before, after, "a/rules.py", "b/rules.py")))
```

The same for a data file: what changed between two versions of the rating scale?
`n=0` shows only the changed lines, without context:

```python run
import difflib
from pathlib import Path

old = Path("data/rating_scale.csv").read_text(encoding="utf-8").splitlines(keepends=True)
new = old.copy()
new[3] = "3,A,0.001,0.003,low risk\n"                       # a new upper PD for rating 3

print("".join(difflib.unified_diff(old, new, "rating_scale.csv (Aug)", "rating_scale.csv (Sep)", n=0)))
```

The Git commands:

```bash
git diff                     # what changed in the working folder, not added yet
git diff --staged            # what is added, will go into the next commit
git log -p -1                # the last commit with its changes
git show HEAD~1:report.py    # the file as it was one commit ago
```

### `.gitignore`: what Git must not keep

A text file `.gitignore` in the project folder lists the files and folders Git
ignores. For a data project, this is not optional:

```text
# the environment - rebuilt from requirements.txt
.venv/
__pycache__/

# data and results - never in Git
data/
out/
*.xlsx
*.csv

# secrets and local settings
.env
*.log

# editors and notebooks
.vscode/
.ipynb_checkpoints/
```

::: danger Data and passwords never go into Git
Git keeps **everything** forever: a file that was committed once stays in the history,
even after you delete it. Real data of the bank, exports with client names, files with
passwords must never be committed - not even "just for a moment". Put them in
`.gitignore` **before** the first `git add`.
:::

```python run
from pathlib import Path

rules = """.venv/
__pycache__/
data/
out/
*.xlsx
.env
"""
Path("out").mkdir(exist_ok=True)
Path("out/.gitignore").write_text(rules, encoding="utf-8")
print(Path("out/.gitignore").read_text(encoding="utf-8").splitlines())
```

The patterns of `.gitignore` are the same kind as `glob` (session 9). The module
`fnmatch` tests a name against them - which files of a project would Git ignore?

```python run
from fnmatch import fnmatch

ignore = ["*.xlsx", "*.csv", ".env", "*.log"]
files = ["report.py", "portfolio_utils.py", "loans_2026-09.csv", "report_2026-09.xlsx",
         ".env", "README.md", "run.log"]

for name in files:
    ignored = any(fnmatch(name, pattern) for pattern in ignore)
    print(f"{name:<22}{'ignored' if ignored else 'kept in Git'}")
```

### Good commits

- **Small**: one change, one commit - "Add the reject file to the loader", not "work
  of Tuesday".
- **A message that says what and why**: in the imperative, like a title: "Fix the
  date format of the payments file".
- **Working code**: commit when the script runs.

### Git in VS Code

The **Source Control** view (`Ctrl+Shift+G`) does the same with buttons: the changed
files, **+** to stage, a message box and **Commit**, the history, and the changes of
a file side by side. Use whatever you prefer - the commands are the same underneath.

::: tip Try it
In your Homework repository: `git status`, then `git log --oneline -5`. Change one
line in a task file, and look at `git diff`. Then `git restore <file>` to undo it.
:::

## 7. Branches and merge

A **branch** is a separate line of commits. The main line is usually called `main`.
Work on a change in its own branch; when it is ready, **merge** it into `main`:

```bash
git switch -c add-reject-file          # create a branch and switch to it
# ... edit, run, commit ...
git commit -am "Write rejected payments to a CSV file"
git switch main                        # back to main - the files change back!
git merge add-reject-file              # bring the work of the branch into main
git branch -d add-reject-file          # the branch is not needed any more
```

```text
main:              A ---- B ------------- M
                           \             /
add-reject-file:            C ---- D ---
```

Why branches, for a report script: `main` always holds the version that produced the
last official numbers; the changes for next month are made on a branch, and merged
after they are checked.

### A conflict

When two branches change the **same lines** of a file, Git cannot decide alone. `git
merge` stops and marks the place in the file:

```text
<<<<<<< HEAD
LGD = 0.45
=======
LGD = 0.40
>>>>>>> new-lgd
```

Edit the file to the version you want (delete the markers), then:

```bash
git add portfolio_utils.py
git commit                              # completes the merge
```

VS Code shows conflicts with buttons: **Accept Current**, **Accept Incoming**,
**Accept Both**.

::: tip Try it
In a test folder: `git init`, commit a file `rules.py` with `LGD = 0.45`; create a
branch, change it to `0.40`, commit; back on `main`, change it to `0.50`, commit; merge
the branch. Resolve the conflict.
:::

## 8. GitHub: remotes and pull requests

### A remote repository

A **remote** is a copy of the repository on a server. The Homework repository of this
course has two (how-to page): `upstream` (the course) and `origin` (yours).

```bash
git clone https://github.com/<user>/<repo>.git     # copy a remote repository (once)
git remote -v                                      # the remotes of this repository
git push                                           # send your commits to the remote
git pull                                           # get the commits of others
```

The usual day: `git pull` before you start, commit as you work, `git push` at the end.

### A pull request: a review before the merge

On GitHub (and GitLab, Azure DevOps, Bitbucket), a **pull request** (a *merge
request* in GitLab) asks: "please merge my branch into `main`". A colleague reads the
changes line by line, comments, and approves - the four-eyes principle, for code:

```bash
git switch -c fix-date-format
# ... commit the fix ...
git push -u origin fix-date-format       # the branch goes to GitHub
# on GitHub: "Compare & pull request" -> describe the change -> a reviewer approves -> Merge
git switch main
git pull                                 # main now has the merged fix
```

### Without GitHub

If your company does not allow github.com, everything of sections 6 and 7 works on
your computer alone, and a company server (GitLab, Azure DevOps, Bitbucket) works
like section 8 - only the address in `git clone` is different.

::: tip Try it
On GitHub, open your own Homework repository: find the list of commits, open one, and
look at its changes. Compare with `git log -p -1` in the terminal.
:::

## 9. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: `git pull upstream main`) and run the tasks from the
terminal, in the repository root:

```bash
python 10-modules-and-git/practice/task1-standard-library.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-standard-library.py` | `statistics`, `math` and `collections` on the portfolio |
| 2 | `task2-predict-imports.py` | Predict: module names, `__name__`, `dir`, what `import` returns |
| 3 | `task3-my-module.py` | Write `portfolio_utils.py` in the same folder; the task imports and checks it |
| 4 | `task4-report-dates.py` | Month ends, add months, quarter ends, months between two dates |
| 5 | `task5-predict-git.py` | Which Git command does what |
| 6 | `task6-project-layout.py` (Optional) | Create a project skeleton with `pathlib`, with a `.gitignore` |

## Summary

| Topic | Remember |
|-------|----------|
| `import` | `import m`, `from m import f`, `import m as x`; never `import *`; runs the file once, keeps it in `sys.modules` |
| Search path | the folder of the script first; never name a file like a module (`csv.py`) |
| Own module | a `.py` file with functions and constants; no work at import time |
| `__main__` | `if __name__ == "__main__":` - code that runs only when the file is run |
| Notebooks | `%load_ext autoreload` + `%autoreload 2`, or restart the kernel |
| Package | a folder with `__init__.py`; `from package.module import name`; `python -m package.module` |
| Project | `README.md`, `requirements.txt`, `.gitignore`, a package, `report.py`, `data/` and `out/` not in Git |
| Standard library | `calendar.monthrange` for month ends; `statistics`; `namedtuple`, `deque`; `math.fsum`, `isclose`; `os.getenv` |
| Environments | one `.venv` per project; `pip freeze > requirements.txt`; install name is not always import name |
| Git | `init`, `status`, `add`, `commit -m`, `log --oneline`, `diff`, `restore` |
| `.gitignore` | `.venv/`, `data/`, `out/`, secrets - before the first commit; data and passwords never in Git |
| Branches | `switch -c`, `merge`, conflicts: edit, `add`, `commit` |
| Remotes | `clone`, `pull`, `push`; a pull request = a review before the merge |

## Homework

1. `10-modules-and-git/homework.py` and `10-modules-and-git/homework_utils.py` (in the
   homework repository): **the portfolio library as a module** - move the functions of
   sessions 4 - 9 into `homework_utils.py`, with docstrings, constants at the top and a
   `__main__` self-test; `homework.py` imports and checks them. Every check must print
   `OK`.
2. The Git part (not checked by the file): make a new folder outside the Homework
   repository, copy `homework_utils.py` into it, and make it a repository with a
   `.gitignore`, three commits, and one branch that you merge.
3. The practice tasks you did not finish in class.

## Self-study

This part is not covered in class. It is for reading at home: a report script that
takes the report date from the command line, and the Git commands that undo things.

### Command-line arguments

A monthly script should not need an edit every month. Give it the report date when
you start it: `python report.py --date 2026-09-30`.

The arguments are in `sys.argv` - a list of strings; the first is the script name:

```python run
import sys

sys.argv = ["report.py", "--date", "2026-09-30", "--lgd", "0.4"]    # as if started like this
print(sys.argv)
```

The module `argparse` reads them properly: names, types, defaults, and a `--help`
text for free:

```python run
import argparse
from datetime import date

parser = argparse.ArgumentParser(description="The monthly portfolio report.")
parser.add_argument("--date", type=date.fromisoformat, required=True, help="the report date, yyyy-mm-dd")
parser.add_argument("--lgd", type=float, default=0.45, help="the LGD (default 0.45)")
parser.add_argument("--excel", action="store_true", help="also write an Excel file")

args = parser.parse_args(["--date", "2026-09-30", "--excel"])     # in a script: parse_args()
print(args.date, args.lgd, args.excel)
parser.print_help()
```

In a script, `parser.parse_args()` without a list reads `sys.argv`. A wrong date
stops the script with a clear message - before any work is done.

::: code-group
```powershell [Windows]
python report.py --date 2026-09-30 --excel
python report.py --help
```
```bash [Linux / macOS]
python report.py --date 2026-09-30 --excel
python report.py --help
```
:::

**Exercises**

1. Add an argument `--input` with the default `data/loans.csv` (type `Path`), and
   print whether the file exists.
2. What happens with `parser.parse_args(["--date", "30.09.2026"])`? Why is that good?

::: details Answer
1. `parser.add_argument("--input", type=Path, default=Path("data/loans.csv"))`, then
   `print(args.input.exists())` (with `from pathlib import Path`).
2. `argparse` calls `date.fromisoformat("30.09.2026")`, which raises a `ValueError`;
   `argparse` turns it into the message *argument --date: invalid fromisoformat
   value* and stops with an error code - the report never runs with a wrong date.
:::

### Git: undo and history

| You want to | Command |
|---|---|
| throw away the changes of a file since the last commit | `git restore report.py` |
| take a file out of the staging area | `git restore --staged report.py` |
| change the message (or add a file) of the **last** commit, not pushed yet | `git commit --amend` |
| undo a commit that is already pushed - with a new commit that does the opposite | `git revert <commit>` |
| see who changed each line, and when | `git blame report.py` |
| the history of one file, with the changes | `git log -p -- report.py` |
| find a word in all versions | `git log -S "LGD" --oneline` |

`revert` is the safe undo for shared history: it adds a commit, it never removes one.

**Notebooks in Git.** A `.ipynb` file keeps the **outputs** of the cells - tables,
charts, sometimes data. Before a commit, clear the outputs (in VS Code: **Clear All
Outputs**), or keep the reusable code in `.py` modules and only the exploration in
notebooks. Outputs of real data in a notebook are data in Git (see the warning of
section 6).

**Exercise**

1. In a test repository, commit a file three times with different `LGD` values. Use
   `git log -S "LGD = 0.40" --oneline` to find the commit that introduced `0.40`, and
   `git revert` it.

::: details Answer
`git log -S "LGD = 0.40" --oneline` lists the commits that added or removed that
text; take the hash of the one that added it, and `git revert <hash>`. Git opens an
editor for the message of the new commit (save and close it); the file is back to
the value before that commit - unless a later commit changed the same line, which
gives a conflict to resolve.
:::

## Read more

- Python tutorial: [Modules](https://docs.python.org/3/tutorial/modules.html),
  [Brief tour of the standard library](https://docs.python.org/3/tutorial/stdlib.html)
- Reference: [`statistics`](https://docs.python.org/3/library/statistics.html),
  [`collections`](https://docs.python.org/3/library/collections.html),
  [`calendar`](https://docs.python.org/3/library/calendar.html),
  [`argparse` tutorial](https://docs.python.org/3/howto/argparse.html)
- Git: [Pro Git](https://git-scm.com/book/en/v2) (the free book: chapters 1 - 3),
  [Version control in VS Code](https://code.visualstudio.com/docs/sourcecontrol/overview)
- GitHub: [About pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)
- Real Python: [Python modules and packages](https://realpython.com/python-modules-packages/)

**Next session:** object-oriented programming - your own classes and objects: a loan
that knows its own rules, with attributes, methods and validation.
