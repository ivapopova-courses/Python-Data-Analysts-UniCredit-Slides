---
title: 14. NumPy and introduction to pandas
---

# 14. NumPy and introduction to pandas

<div class="lecture-meta">
  <span>Session 14</span><span>practice: <code>14-numpy-pandas-intro/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- calculate on a whole column at once with **NumPy** arrays - no loops;
- choose values with `np.where` and `np.select`, the vector `CASE WHEN`;
- work with the two objects of **pandas**: the `Series` (a column) and the
  `DataFrame` (a table);
- read CSV and Excel files with the options real files need: separators, decimal
  commas, encodings, dates, missing values;
- look at a new dataset the way `PROC CONTENTS`, `PROC MEANS` and `PROC FREQ` do;
- understand and fix the types of the columns.

From SAS to pandas - the first look at a dataset, two ways:

```sas
proc import datafile="loans.csv" out=loans dbms=csv replace; run;
proc contents data=loans; run;
proc means data=loans n mean min max; var outstanding interest_rate; run;
proc freq data=loans; tables product; run;
```

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(loans.shape)
print(loans.dtypes)
print(loans[["outstanding", "interest_rate"]].describe().round(2))
loans["product"].value_counts()
```

Since session 1 you have done this kind of work with loops over rows. pandas does it
on whole **columns** - with the same ideas inside (sessions 5 and 6), in C, and in one
line each.

## 1. Why NumPy and pandas

A loop handles one value at a time, in Python. A NumPy operation handles the whole
column at once, in compiled C code - often 50 to 100 times faster:

```python run
import time
import numpy as np

amounts = list(range(1_000_000))
start = time.perf_counter()
doubled = [a * 1.05 for a in amounts]
t_loop = time.perf_counter() - start

array = np.arange(1_000_000)
start = time.perf_counter()
doubled_np = array * 1.05
t_numpy = time.perf_counter() - start

print(f"loop {t_loop * 1000:.1f} ms, NumPy {t_numpy * 1000:.1f} ms")
```

- **NumPy** - arrays of numbers and fast calculations on them.
- **pandas** - tables with named columns of different types, built on NumPy: read,
  clean, select, group, join, reshape, write.

In SAS terms: a DATA step loops over the observations; `PROC MEANS` works on whole
variables. pandas code looks like the second.

::: info pandas 2 and pandas 3
`pip install -r requirements.txt` installs pandas 3 today (session 1); this site runs
pandas 3 too. Where pandas 2.2 behaves differently, these pages say so - mostly the
type of text columns (`str` in 3, `object` in 2.2) and copies of a DataFrame (session
15). Check your version: `pd.__version__`.
:::

::: tip Try it
Change the timing example to compute `a ** 2` instead of `a * 1.05`. Is the difference
bigger or smaller?
:::

## 2. NumPy arrays

### An array: one type, one shape

```python run
import numpy as np

outstanding = np.array([1044231.30, 651927.30, 644.25, 5875.11, 225.06])
print(outstanding)
print(outstanding.dtype, outstanding.shape, outstanding.ndim, len(outstanding))

stages = np.array([1, 2, 2, 1, 1])
print(stages.dtype)
```

An array holds values of **one** type (`dtype`): `float64`, `int64`, `bool`, ... A
list can mix anything; an array cannot - that is why it is fast.

Arrays without typing the values - ranges, zeros, a 2D table:

```python run
import numpy as np

print(np.arange(1, 13))                          # the months 1 ... 12 (like range)
print(np.linspace(0, 1, 5))                      # 5 evenly spaced values from 0 to 1
print(np.zeros(3), np.ones(3, dtype=int))

monthly = np.arange(36).reshape(12, 3)           # 12 rows (months) x 3 columns (segments)
print(monthly.shape)
print(monthly[:2])                               # the first two months
```

### Operations on the whole array

Arithmetic works **element by element** - no loop:

```python run
import numpy as np

outstanding = np.array([1044231.30, 651927.30, 644.25, 5875.11])
rates = np.array([8.83, 5.44, 4.79, 8.35])

print(outstanding / 1000)                    # every value
print(outstanding * rates / 100)             # pairs: the yearly interest of each loan
print((outstanding * rates / 100).sum())
print(np.round(outstanding / 1000, 1))
```

Compare with session 5: `[o * r / 100 for o, r in zip(outstanding, rates)]`. NumPy
writes it as the formula itself.

### Comparisons and masks: the `WHERE`

A comparison gives an array of `True` / `False` - a **mask**. A mask in square
brackets keeps the values where it is `True`:

```python run
import numpy as np

days = np.array([0, 35, 0, 120, 15, 95])
outstanding = np.array([1000.0, 2500.0, 800.0, 4000.0, 1200.0, 300.0])

late = days > 30
print(late)
print(outstanding[late])                      # WHERE days_past_due > 30
print(outstanding[late].sum(), late.sum(), late.mean())   # True counts as 1
print(outstanding[(days > 0) & (days <= 90)])             # & is AND, | is OR
```

::: warning `&` and `|`, with brackets
In arrays (and in pandas), combine conditions with `&` (and), `|` (or), `~` (not) - not
with `and` / `or`. And put each comparison in **brackets**: `(days > 0) & (days <= 90)`.
Without them, Python reads `days > (0 & days) <= 90` and gives an error or a wrong
result.
:::

### Aggregates

```python run
import numpy as np

outstanding = np.array([1044231.30, 651927.30, 644.25, 5875.11, 225.06])

print(outstanding.sum(), outstanding.mean(), outstanding.min(), outstanding.max())
print(outstanding.std(ddof=1))                # ddof=1: the sample standard deviation (SAS STD)
print(outstanding.argmax())                   # the POSITION of the maximum
print(np.percentile(outstanding, [25, 50, 75]))
print(np.median(outstanding))
```

`ddof=1` matters: NumPy's default `std()` is the **population** standard deviation,
SAS and pandas use the sample one (`n - 1`).

Running totals and differences - `RETAIN` and `LAG` of a DATA step, for a whole array:

```python run
import numpy as np

monthly_outstanding = np.array([128.4, 129.1, 130.2, 129.6, 131.4])
print(np.cumsum([1200, 800, 1500, 900]))          # a running total
print(np.round(np.diff(monthly_outstanding), 1))  # the change from month to month
```

Sort, and the positions of the largest - the top N of session 5:

```python run
import numpy as np

outstanding = np.array([1044231.30, 651927.30, 644.25, 5875.11, 225.06])
ids = np.array(["L1", "L2", "L3", "L4", "L5"])

print(np.sort(outstanding)[::-1])                 # largest first
order = np.argsort(outstanding)[::-1]             # the positions, largest first
print(ids[order[:3]], outstanding[order[:3]])
```

`np.clip` keeps values inside limits - a PD after a stress must stay between 0 and 1:

```python run
import numpy as np

pd_stressed = np.array([0.004, 0.07, 0.35, 0.80]) * 2.5
print(pd_stressed)
print(np.clip(pd_stressed, 0, 1))
```

### `np.where`: `CASE WHEN` with two branches

`np.where(condition, value_if_true, value_if_false)` - for every element:

```python run
import numpy as np

days = np.array([0, 35, 0, 120, 15])
print(np.where(days > 30, "late", "ok"))
print(np.where(days > 90, 1.0, 0.02))          # a PD: 1 for defaulted loans
```

### `np.select`: `CASE WHEN` with many branches

```python run
import numpy as np

days = np.array([0, 35, 0, 120, 15, 60])

conditions = [days == 0, days <= 30, days <= 90]
choices = ["current", "1-30", "31-90"]
print(np.select(conditions, choices, default="90+"))
```

The conditions are checked **in order** - the first true one wins, like `CASE WHEN`.

### Broadcasting: different shapes together

A scalar is "stretched" to the shape of the array - that is why `outstanding / 1000`
works. The same happens with a row and a table: a stress test with three scenarios
for four loans, in one line:

```python run
import numpy as np

outstanding = np.array([1044231.30, 651927.30, 644.25, 5875.11])
pd_base = np.array([0.004, 0.07, 0.02, 0.01])
stress = np.array([[1.0], [1.5], [3.0]])          # 3 scenarios: a column

pd_scenarios = np.minimum(pd_base * stress, 1.0)   # (3, 1) x (4,) -> (3, 4)
el = pd_scenarios * 0.45 * outstanding             # (3, 4) x (4,) -> (3, 4)
print(el.shape)
print(np.round(el.sum(axis=1), 2))                 # the EL of each scenario: sum over the loans
```

`axis=1` sums **across** a row (over the loans); `axis=0` sums **down** a column
(over the scenarios).

### Missing values in NumPy: `NaN`

A missing number is `np.nan` ("not a number", a float). It spreads: any calculation
with `nan` gives `nan` - unless you use the `nan...` functions:

```python run
import numpy as np

values = np.array([100.0, np.nan, 250.0])
print(values.sum(), np.nansum(values), np.nanmean(values))
print(np.nan == np.nan, np.isnan(values))           # nan is not equal to itself!
print(np.array([1, 2, 3]).dtype)                    # int: cannot hold nan
```

(SAS missing values sort first and are skipped by `PROC MEANS`; SQL `NULL`s are skipped
by `SUM`. In NumPy, `nan` is not skipped - in pandas it is, section 7.)

::: tip Try it
With `days` and `outstanding` of the mask example: the share of the outstanding that
is more than 30 days past due. Then the DPD bucket of each loan with `np.select`.
:::

## 3. `Series`

A **Series** is one column: values (a NumPy array) and an **index** - a label for each
row:

```python run
import pandas as pd

outstanding = pd.Series([1044231.30, 651927.30, 644.25], index=["L000001", "L000002", "L000003"],
                        name="outstanding")
print(outstanding)
print(outstanding["L000002"], outstanding.index.tolist(), outstanding.values)
print((outstanding / 1000).round(1))
```

From a dictionary, the keys become the index:

```python run
import pandas as pd

by_segment = pd.Series({"corporate": 93087049.89, "retail": 6837600.42, "sme": 31446058.29})
print(by_segment.sort_values(ascending=False))
print(by_segment.sum(), by_segment.idxmax())
print((by_segment / by_segment.sum()).round(4))
```

A column of a file is a Series too - with the same methods:

```python run
import pandas as pd

outstanding = pd.read_csv("data/loans.csv")["outstanding"]
print(type(outstanding), len(outstanding))
print(outstanding.head(3))
print(outstanding.describe().round(2))
print(outstanding[outstanding > 5_000_000].round(0))       # a mask, as in NumPy
```

### A trap: operations match the labels

Two Series are combined by their **index**, not by their position. A label that is in
only one of them gives `NaN`:

```python run
import pandas as pd

august = pd.Series({"retail": 6.9, "sme": 31.2, "corporate": 92.5})
september = pd.Series({"sme": 31.4, "corporate": 93.1, "project": 5.0})

print(september - august)                       # matched by name; NaN where one is missing
print(september.sub(august, fill_value=0))      # treat a missing one as 0
```

This **alignment** is a feature - you never subtract the wrong rows - but a surprise if
you expect positions.

### Counting: `value_counts`

```python run
import pandas as pd

stages = pd.Series([1, 2, 2, 1, 3, 1, 1])
print(stages.value_counts())                       # PROC FREQ
print(stages.value_counts(normalize=True).round(3))
print(stages.value_counts().sort_index())
```

::: tip Try it
Make a Series of the three stage totals of the portfolio with the index `1, 2, 3`, and
compute the share of each stage. Then add a Series that has only the index `3` - what
happens to stages 1 and 2?
:::

## 4. `DataFrame`

### A table of Series

A **DataFrame** is a table: several Series with **one** index, each column with its own
type. Create one from a dictionary of columns:

```python run
import pandas as pd

loans = pd.DataFrame({
    "loan_id": ["L000001", "L000002", "L000003", "L000004"],
    "product": ["investment", "investment", "credit_card", "overdraft"],
    "outstanding": [1044231.30, 651927.30, 644.25, 5875.11],
    "stage": [1, 2, 2, 1],
})
print(loans)
print(loans.shape, list(loans.columns))
```

From a list of dictionaries (the rows of session 6):

```python run
import pandas as pd

rows = [{"client_id": "C0001", "segment": "retail", "rating": 3},
        {"client_id": "C0002", "segment": "sme", "rating": 5}]
pd.DataFrame(rows)
```

### Columns

`df["name"]` gives one column as a **Series**; `df[["a", "b"]]` (a list inside) gives a
**DataFrame** with those columns - `SELECT a, b`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(type(loans["outstanding"]), type(loans[["loan_id", "outstanding"]]))
print(loans["outstanding"].sum().round(2))
loans[["loan_id", "product", "outstanding"]].head(3)
```

A new column from other columns - a derived variable of a DATA step, for all rows at
once:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["repaid_share"] = (1 - loans["outstanding"] / loans["amount"]).round(4)
loans["yearly_interest"] = (loans["outstanding"] * loans["interest_rate"] / 100).round(2)
loans[["loan_id", "amount", "outstanding", "repaid_share", "yearly_interest"]].head()
```

Remove and rename columns - `DROP=` and `RENAME=` of a DATA step:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
small = loans.drop(columns=["start_date", "maturity_date", "amount"])
small = small.rename(columns={"days_past_due": "dpd", "interest_rate": "rate"})
print(small.columns.tolist())
print(loans.shape, small.shape)                       # loans itself is unchanged
```

### Rows: `head`, `tail`, `sample`, a first sort

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(loans.tail(2))                                  # the last rows
print(loans.sample(3, random_state=1)[["loan_id", "product"]])   # random rows, repeatable
loans.sort_values("outstanding", ascending=False).head(3)[["loan_id", "product", "outstanding"]]
```

`sort_values` is `PROC SORT` / `ORDER BY`; selection with conditions (`WHERE`) and
`loc` are session 15.

### The index

Every DataFrame has an index - by default the numbers `0, 1, 2, ...`. A column can
become the index - then rows are found by it, like a dictionary:

```python run
import pandas as pd

clients = pd.read_csv("data/clients.csv").set_index("client_id")
print(clients.loc["C0002"])                            # a row by its label (more in session 15)
print(clients.index[:3].tolist())
```

::: tip Try it
Read `clients.csv` and add a column `years_client`: 2026 minus the year of
`client_since` (hint: `loans["start_date"].str[:4].astype(int)` takes the year from the
text). Show the 3 oldest clients with `sort_values`.
:::

## 5. Reading CSV files

### The defaults

`pd.read_csv(path)` guesses a lot: the header in the first line, the separator `,`,
the decimal point `.`, numbers as numbers, everything else as text. For `loans.csv`
that is right. For files from other systems, the options tell pandas how to read:

| Option | Means | SAS / informat |
|---|---|---|
| `sep=";"` | the separator | `DLM=';'` |
| `decimal=","` | the decimal comma | `COMMAX.` |
| `thousands=" "` | the thousands separator | `COMMA.` |
| `encoding="utf-8-sig"` / `"cp1251"` | the encoding (session 7) | `ENCODING=` |
| `dtype={"client_id": str}` | the type of a column | `$` / an informat |
| `parse_dates=[...]`, `dayfirst=True` | dates | `DDMMYY10.` |
| `na_values=["."]` | texts that mean "missing" | `.` is missing in SAS |
| `usecols=[...]`, `nrows=100` | some columns, the first rows | `KEEP=`, `OBS=` |
| `skiprows`, `header` | lines to skip; where the header is | `FIRSTOBS=` |

### A real file: `loans_export.csv`

The same loans as an export of a local system (sample data page): `;`, decimal comma,
`dd.mm.yyyy` dates, a BOM, column names with spaces, a SAS-style `.` for missing
values. Read it with the defaults, and see what goes wrong:

```python run
import pandas as pd

raw = pd.read_csv("data/loans_export.csv")
print(raw.shape)
print(raw.columns[:3].tolist())
raw.head(2)
```

One column with everything in it - the separator was not a comma. With the right
options:

```python run
import pandas as pd

loans = pd.read_csv(
    "data/loans_export.csv",
    sep=";", decimal=",", encoding="utf-8-sig",
    na_values=["."],
    parse_dates=["Start date", "Maturity date"], dayfirst=True,
)
print(loans.shape)
print(loans.dtypes)
loans.head(3)
```

Now `Outstanding` is a number (the `.` became `NaN`), the dates are dates, and the BOM
is gone from the first column name.

### Clean column names

Names with spaces and capitals are awkward in code. Rename them to `snake_case` once,
right after reading:

```python run
import pandas as pd

loans = pd.read_csv("data/loans_export.csv", sep=";", decimal=",", encoding="utf-8-sig", na_values=["."])
loans.columns = (loans.columns.str.strip().str.lower()
                 .str.replace("%", "pct").str.replace(" ", "_"))
print(loans.columns.tolist())

loans = loans.rename(columns={"interest_rate_pct": "interest_rate"})   # one name by hand
print(loans.columns.tolist()[-3:])
```

`loans.columns.str` gives the string methods of session 7 for all names at once.

A thousands separator and a title above the table - `thousands=` and `skiprows=`:

```python run
import io
import pandas as pd

text = """Portfolio report 30.09.2026
generated by the core system
loan_id;outstanding
L000001;1 044 231,30
L000002;651 927,30
"""
df = pd.read_csv(io.StringIO(text), sep=";", decimal=",", thousands=" ", skiprows=2)
print(df)
print(df["outstanding"].dtype, df["outstanding"].sum())
```

Several texts can mean "missing" - list them all:

```python run
import io
import pandas as pd

text = "loan_id,rating\nL1,5\nL2,.\nL3,n/a\nL4,\nL5,NR\n"
df = pd.read_csv(io.StringIO(text), na_values=[".", "n/a", "NR"])
print(df)
print(df["rating"].isna().sum(), "missing")
```

### Ids are text

An id that looks like a number - an EIK, an account, a branch code `0042` - must stay
**text**: as a number, its leading zeros are lost and nobody should calculate with it.
`dtype` fixes the type when reading:

```python run
import io
import pandas as pd

text = "branch,eik,limit\n0042,131234567,1000\n0107,000123456,2500\n"
print(pd.read_csv(io.StringIO(text)))                                  # 42, 123456: zeros lost
print(pd.read_csv(io.StringIO(text), dtype={"branch": str, "eik": str}))
```

(`io.StringIO` makes a string behave like a file - session 9.)

### Some columns, some rows; another encoding

```python run
import pandas as pd

first = pd.read_csv("data/loans.csv", usecols=["loan_id", "product", "outstanding"], nrows=5)
print(first)

regions = pd.read_csv("data/regions_bg.csv", encoding="cp1251")     # session 7: cp1251
print(regions)
```

### Check the result against a trusted source

The export and `loans.csv` should hold the same loans. A quick check of the totals -
the habit of session 7:

```python run
import pandas as pd

clean = pd.read_csv("data/loans.csv")
export = pd.read_csv("data/loans_export.csv", sep=";", decimal=",", encoding="utf-8-sig", na_values=["."])

print(len(clean), len(export), "rows")
print(round(clean["outstanding"].sum(), 2), round(export["Outstanding"].sum(), 2))
print(export["Loan ID"].duplicated().sum(), "duplicated ids;", export["Outstanding"].isna().sum(), "missing amounts")
```

The export has 6 rows more (duplicates) and 8 missing amounts - session 15 cleans them.

::: tip Try it
Read only the columns `Loan ID`, `Product` and `Outstanding` of the export (`usecols`),
with the right options. How many rows have no product?
:::

## 6. Reading Excel (and SAS) files

### `read_excel`

`pd.read_excel` reads a sheet of an `.xlsx` file (with openpyxl underneath, session 9):

```python run
import pandas as pd

september = pd.read_excel("data/fx_rates.xlsx", sheet_name="2026-09")
print(september.shape, september.dtypes.to_dict())
september.head(3)
```

`sheet_name=None` reads **all** sheets into a dictionary `name -> DataFrame`:

```python run
import pandas as pd

sheets = pd.read_excel("data/fx_rates.xlsx", sheet_name=None)
print(list(sheets))
for name, df in sheets.items():
    print(name, len(df), "days, USD from", df["USD"].min(), "to", df["USD"].max())
```

To put the sheets under each other in one table, `pd.concat` (session 15 explains it):

```python run
import pandas as pd

sheets = pd.read_excel("data/fx_rates.xlsx", sheet_name=None)
rates = pd.concat(sheets.values(), ignore_index=True)
print(rates.shape)
rates.tail(3)
```

Other useful options: `skiprows` (a title above the table), `usecols="A:C"`,
`dtype`, `na_values` - the same as for CSV.

### SAS datasets

pandas reads `.sas7bdat` and `.xpt` files directly - useful while SAS and Python live
side by side:

```python
import pandas as pd

loans = pd.read_sas("loans.sas7bdat", encoding="latin-1")        # or "utf-8", "cp1251"
loans = pd.read_sas("big.sas7bdat", chunksize=100_000)            # an iterator of pieces
```

SAS dates arrive as dates (pandas converts them), SAS missing values as `NaN`. To get
the **labels** and **formats** of the variables as well, the package `pyreadstat`
(`pip install pyreadstat`) reads them: `df, meta = pyreadstat.read_sas7bdat(path)`,
then `meta.column_labels`.

::: tip Try it
Read all sheets of `fx_rates.xlsx`, and print the mean `GBP` rate of each month.
:::

## 7. A first look at the data

A new dataset: before any analysis, the same questions every time. In SAS, a few
procedures; in pandas, a few methods.

| Question | SAS | pandas |
|---|---|---|
| how big? | `PROC CONTENTS` | `df.shape`, `len(df)` |
| which columns, which types? | `PROC CONTENTS` | `df.dtypes`, `df.info()` |
| what do rows look like? | `PROC PRINT (OBS=10)` | `df.head(10)`, `df.sample(5)` |
| numbers: n, mean, min, max? | `PROC MEANS` | `df.describe()` |
| categories: how many of each? | `PROC FREQ` | `df["col"].value_counts()` |
| missing values? | `PROC MEANS NMISS` | `df.isna().sum()` |
| duplicates? | `PROC SORT NODUPKEY` + the log | `df.duplicated().sum()` |

### `info()`: `PROC CONTENTS`

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.info()
```

The columns, their non-missing counts, their types, and the memory. A column whose
non-null count is lower than the number of rows has missing values.

### `describe()`: `PROC MEANS`

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.describe().round(2)
```

For the text columns: `describe(include="object")` in pandas 2.2, `include="str"` in
pandas 3 - or simply `include="all"` (works in both):

```python run
import pandas as pd

clients = pd.read_csv("data/clients.csv")
clients.describe(include="all")
```

`count`, `unique`, `top` (the most frequent value) and `freq` for text; the numeric
statistics for numbers. Other percentiles - the tails matter in risk:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["outstanding"].describe(percentiles=[0.01, 0.5, 0.99]).round(2)
```

### `value_counts()`: `PROC FREQ`

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(loans["product"].value_counts())
print(loans["stage"].value_counts(normalize=True).sort_index().round(3))
print(loans["currency"].value_counts(dropna=False))      # also count the missing ones
```

A number in ranges - `value_counts(bins=...)` - a first histogram as a table:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["interest_rate"].value_counts(bins=[0, 4, 8, 12, 16]).sort_index()
```

Two variables - `TABLES stage * currency` - is `pd.crosstab` (session 16):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
pd.crosstab(loans["stage"], loans["currency"], margins=True)
```

### Distinct values, missing values, duplicates

```python run
import pandas as pd

export = pd.read_csv("data/loans_export.csv", sep=";", decimal=",", encoding="utf-8-sig", na_values=["."])

print(export.nunique())                                 # distinct values per column
print(export.isna().sum())                              # missing values per column
print(export.duplicated().sum(), "rows are exact copies of an earlier row")
print(export["Loan ID"].duplicated().sum(), "loan ids appear more than once")
```

`isna()` gives a DataFrame of `True` / `False`; `.sum()` counts the `True` per column -
the masks of section 2, for a whole table.

To remove the exact copies, `drop_duplicates()` - like `PROC SORT NODUPRECS`, but it
keeps the order of the rows (the first copy stays):

```python run
import pandas as pd

export = pd.read_csv("data/loans_export.csv", sep=";", decimal=",", encoding="utf-8-sig", na_values=["."])
unique_rows = export.drop_duplicates()
print(len(export), "->", len(unique_rows), "rows")
print(unique_rows["Loan ID"].duplicated().sum(), "loan ids appear more than once now")
```

`drop_duplicates(subset=["Loan ID"])` compares only that column (`NODUPKEY`). A new
DataFrame comes back; the old one does not change.

### Dates: the range

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv", parse_dates=["start_date", "maturity_date"])
print(loans["start_date"].min(), loans["start_date"].max())
print(loans["maturity_date"].dt.year.value_counts().sort_index().head())
```

`.dt` gives the date parts of a whole column (session 16 uses it a lot).

### A profile function

The same questions for every new file - write them once, as a function (session 4):

```python run
import pandas as pd

def profile(df):
    """One row per column: type, missing, distinct, an example."""
    return pd.DataFrame({
        "type": df.dtypes.astype(str),
        "missing": df.isna().sum(),
        "distinct": df.nunique(),
        "example": df.iloc[0],
    })

loans = pd.read_csv("data/loans.csv")
profile(loans)
```

::: tip Try it
Profile `client_register.csv` with the function. Which columns have missing values,
and how many distinct cities does it see (compare with session 7)?
:::

## 8. The types of the columns

### The types you will meet

| pandas type | Holds | SAS |
|---|---|---|
| `int64` | whole numbers, no missing values | numeric |
| `float64` | numbers with decimals; `NaN` for missing | numeric |
| `str` (pandas 3) / `object` (pandas 2.2) | text | character |
| `bool` | `True` / `False` | numeric 0 / 1 |
| `datetime64` | dates and times | numeric with a date format |
| `category` | a few repeated values (codes) | a character variable with a format |
| `Int64` (capital I) | whole numbers **with** missing values | - |

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(loans.dtypes.value_counts())
print(loans["loan_id"].dtype)          # str in pandas 3, object in pandas 2.2
```

A comparison gives a `bool` column - and `True` counts as 1, so `sum` counts and
`mean` gives the share:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
late = loans["days_past_due"] > 30
print(late.dtype, late.sum(), round(late.mean(), 4))
```

### Change a type: `astype`

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["stage"] = loans["stage"].astype(str)              # a code, not a number to add
loans["product"] = loans["product"].astype("category")   # few distinct values
print(loans[["stage", "product"]].dtypes)
print(loans["product"].cat.categories.tolist())
```

A category can have an **order** - then comparisons and sorting follow it, not the
alphabet:

```python run
import pandas as pd

buckets = pd.Series(["31-90", "current", "90+", "1-30", "current"])
order = pd.CategoricalDtype(["current", "1-30", "31-90", "90+"], ordered=True)
buckets = buckets.astype(order)
print(buckets.sort_values().tolist())
print((buckets > "1-30").tolist())
```

### Text to numbers and dates: `to_numeric`, `to_datetime`

`astype(float)` stops at the first bad value. `pd.to_numeric(..., errors="coerce")`
turns bad values into `NaN` - the `??` informat of SAS (session 9) - so you can count
them:

```python run
import pandas as pd

raw = pd.Series(["125.50", "12O.50", "", "n/a", "7"])
numbers = pd.to_numeric(raw, errors="coerce")
print(numbers)
print(numbers.isna().sum(), "could not be read:", raw[numbers.isna()].tolist())
```

`pd.to_datetime` with a `format` reads dates - for a whole column, much faster than
`strptime` in a loop (session 7):

```python run
import pandas as pd

raw = pd.Series(["30.09.2026", "15.01.2026", "31.09.2026"])
dates = pd.to_datetime(raw, format="%d.%m.%Y", errors="coerce")
print(dates)
print((pd.Timestamp("2026-09-30") - dates).dt.days)
```

### Whole numbers with missing values: `Int64`

A `float` can be `NaN`, an `int64` cannot - so a column of whole numbers with one
missing value becomes `float64`. The **nullable** type `Int64` keeps it whole:

```python run
import pandas as pd

stage = pd.Series([1, 2, None, 3])
print(stage.dtype, stage.tolist())                 # float64: 1.0, 2.0, nan, 3.0
print(stage.astype("Int64"))                       # 1, 2, <NA>, 3
```

### Memory

`category` and the right types save memory - it matters with millions of rows:

```python run
import pandas as pd

history = pd.read_csv("data/ratings_history.csv")
before = history.memory_usage(deep=True).sum()
history["client_id"] = history["client_id"].astype("category")
history["month_end"] = pd.to_datetime(history["month_end"])
after = history.memory_usage(deep=True).sum()
print(f"{before / 1024:.0f} KB -> {after / 1024:.0f} KB")
```

::: tip Try it
Read `payments_2026-09.csv` and convert `amount` with `pd.to_numeric(...,
errors="coerce")` and `pay_date` with `pd.to_datetime(..., format="%Y-%m-%d",
errors="coerce")`. How many values of each could not be read? (Compare with the
loader of session 9.)
:::

## 9. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: `git pull upstream main`) and run the tasks from the
terminal, in the repository root (with the virtual environment active - the tasks
need NumPy and pandas):

```bash
python 14-numpy-pandas-intro/practice/task1-numpy-arrays.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-numpy-arrays.py` | Arrays, masks and aggregates on the outstanding amounts |
| 2 | `task2-predict-numpy.py` | Predict shapes, types, broadcasting, `NaN`, alignment |
| 3 | `task3-where-select.py` | `np.where` and `np.select` for buckets, flags and PDs |
| 4 | `task4-read-export.py` | Read `loans_export.csv` with all the right options |
| 5 | `task5-profile.py` | The profile of a dataset: shape, types, describe, counts, missing values |
| 6 | `task6-excel-sheets.py` (Optional) | All sheets of `fx_rates.xlsx`; the monthly averages |

## Summary

| Topic | Remember |
|-------|----------|
| NumPy | `np.array`; one `dtype`; operations on whole arrays; masks `a[a > 90]`; `&`, `\|`, `~` with brackets |
| Aggregates | `sum`, `mean`, `min`, `max`, `argmax`, `np.percentile`; `std(ddof=1)` for the sample |
| `CASE WHEN` | `np.where(cond, a, b)`; `np.select([conds], [choices], default=...)` - the first true wins |
| Broadcasting | a scalar or a smaller array is stretched; `axis=0` down, `axis=1` across |
| `NaN` | spreads in NumPy (`np.nansum`); not equal to itself; ints cannot hold it |
| Series | values + index; operations match labels (alignment); `value_counts` |
| DataFrame | columns of Series with one index; `df["a"]` a Series, `df[["a", "b"]]` a DataFrame; new columns from others |
| `read_csv` | `sep`, `decimal`, `thousands`, `encoding`, `dtype`, `parse_dates` + `dayfirst`, `na_values`, `usecols`, `nrows` |
| `read_excel` | `sheet_name=...`; `None` for all sheets (a dict); `read_sas` for SAS datasets |
| First look | `shape`, `info()`, `head()`, `describe()`, `value_counts()`, `nunique()`, `isna().sum()`, `duplicated().sum()` |
| Types | int64, float64, str / object, bool, datetime64, category, Int64; `astype`; `to_numeric` / `to_datetime` with `errors="coerce"` |

## Homework

1. `14-numpy-pandas-intro/homework.py` (in the homework repository): **load and
   profile the export** - a function that reads `loans_export.csv` into a clean
   DataFrame (snake_case names, the right types, missing values as `NaN`, no
   duplicate rows), a profile of it, and a comparison of its totals with `loans.csv`.
   Every check must print `OK`.
2. The practice tasks you did not finish in class.
3. Optional: open a Jupyter notebook in your Homework folder and do section 7 on
   `clients.csv` and `client_register.csv` - the notebook is the natural place for a
   first look.

## Self-study

This part is not covered in class. It is for reading at home: a simulation of the
portfolio loss with NumPy - the "modelling" side of the team's work - and a short note
on SAS files.

### Monte Carlo: the distribution of the portfolio loss

The expected loss (`PD x LGD x EAD`, summed) is one number. A risk manager also wants
the **distribution** of the loss: how bad can a year be? A simple simulation:

1. For each loan, draw a random number; the loan defaults if it is below its PD.
2. The loss of the year is the sum of `LGD x EAD` of the defaulted loans.
3. Repeat 10,000 times; look at the distribution of the 10,000 losses.

NumPy does all scenarios at once - a 10,000 x 400 array of random numbers:

```python run
import numpy as np
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")
scale = pd.read_csv("data/rating_scale.csv")

pd_of_rating = dict(zip(scale["rating"], (scale["pd_min"] + scale["pd_max"]) / 2))
rating = loans["client_id"].map(dict(zip(clients["client_id"], clients["rating"])))
pd_loan = rating.map(pd_of_rating).to_numpy()            # one PD per loan
ead = loans["outstanding"].to_numpy()
lgd = 0.45

rng = np.random.default_rng(2026)                         # a seed: the same result every run
defaults = rng.random((10_000, len(ead))) < pd_loan       # (10000, 400) True / False
losses = (defaults * (lgd * ead)).sum(axis=1)             # the loss of each scenario

print(f"expected loss (formula):    {np.sum(pd_loan * lgd * ead):>14,.2f}")
print(f"mean of the simulation:     {losses.mean():>14,.2f}")
print(f"99.9% quantile (VaR):       {np.quantile(losses, 0.999):>14,.2f}")
print(f"share of years without loss: {np.mean(losses == 0):.2%}")
```

The mean of the simulation is close to the expected loss of homework 4 (1,140,106.56) -
the formula is the mean of this distribution. The 99.9% quantile is far higher: one or
two large project finance loans that default together make a bad year. (This simple
model treats the defaults as independent; real credit portfolio models add a common
factor for the economy.)

A histogram (charts: session 16):

```python run
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")
scale = pd.read_csv("data/rating_scale.csv")
pd_of_rating = dict(zip(scale["rating"], (scale["pd_min"] + scale["pd_max"]) / 2))
pd_loan = loans["client_id"].map(dict(zip(clients["client_id"], clients["rating"]))).map(pd_of_rating).to_numpy()
ead = loans["outstanding"].to_numpy()

losses = ((np.random.default_rng(2026).random((10_000, len(ead))) < pd_loan) * 0.45 * ead).sum(axis=1)
plt.hist(losses / 1e6, bins=60)
plt.xlabel("loss of the year, EUR million")
plt.ylabel("scenarios")
plt.title("Simulated portfolio loss")
plt.show()
```

**Exercises**

1. Run the simulation with LGD 0.25 and 0.60. How do the mean and the 99.9% quantile
   change? Are they proportional to the LGD?
2. Remove the 7 loans over EUR 5 million (`ead > 5e6`) and run it again. What happens
   to the 99.9% quantile - and why is that the concentration risk of homework 5?

::: details Answer
1. Both are proportional: the losses are `defaults x LGD x EAD`, so all of them scale
   with the LGD (with the same seed, exactly).
2. `keep = ead <= 5e6`, then use `pd_loan[keep]` and `ead[keep]`. The mean drops a
   little, the 99.9% quantile drops a lot: the tail of the distribution comes from the
   few very large loans - the concentration of the top 10 (47% of the portfolio,
   homework 5).
:::

### Reading SAS datasets

`pd.read_sas` reads `.sas7bdat` (and `.xpt`) files without SAS. Points to know:

- **Encoding:** give `encoding=` (the SAS session encoding, often `latin-1` or
  `utf-8`); without it, text columns come as bytes (`b'...'`).
- **Dates:** SAS date variables with a date format arrive as `datetime64`; without a
  format, as numbers of days since 1960-01-01 - convert with
  `pd.to_datetime(x, unit="D", origin="1960-01-01")`.
- **Missing values:** `.` and the special missing values `.A` - `.Z` become `NaN`.
- **Big files:** `chunksize=` gives pieces (session 13, Self-study).
- **Labels and formats:** `pyreadstat.read_sas7bdat(path)` returns `(df, meta)`;
  `meta.column_names_to_labels` maps the variable names to their labels.

```python
import pandas as pd

days = pd.Series([24379, 24745])                      # days since 1960-01-01 (a SAS date)
print(pd.to_datetime(days, unit="D", origin="1960-01-01"))
```

**Exercise**

1. Convert the SAS date numbers `0`, `366` and `24379` into dates. What is the SAS date
   of 30.09.2026?

::: details Answer
```python
import pandas as pd
print(pd.to_datetime(pd.Series([0, 366, 24379]), unit="D", origin="1960-01-01"))
print((pd.Timestamp("2026-09-30") - pd.Timestamp("1960-01-01")).days)     # 24379
```
`0` is 1960-01-01, `366` is 1961-01-01 (1960 was a leap year), `24379` is 2026-09-30.
:::

## Read more

- NumPy: [the absolute basics for beginners](https://numpy.org/doc/stable/user/absolute_beginners.html),
  [broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html)
- pandas: [10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html),
  [Comparison with SAS](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sas.html),
  [Comparison with SQL](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html),
  [`read_csv`](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- pandas 3: [What's new in 3.0](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)
  (the string type and copy-on-write)
- Book: [Python for Data Analysis, 3rd edition](https://wesmckinney.com/book/) by Wes
  McKinney, the author of pandas - free online

**Next session:** pandas - selection with `loc` and masks, new columns with
`np.select` and `pd.cut`, `groupby` (the `GROUP BY` and `PROC MEANS` of pandas),
`merge` (the `JOIN`), and missing values.
