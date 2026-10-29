---
title: "16. pandas: reports and the final project"
---

# 16. pandas: reports and the final project

<div class="lecture-meta">
  <span>Session 16</span><span>practice: <code>16-pandas-reports-project/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- turn a long table into a report table with `pivot_table` and `pd.crosstab` - and
  back with `melt`;
- work with dates: month ends, months between two dates, periods;
- compare each month with the previous one - the `LAG` and `RETAIN` of a DATA step;
- build a rating migration matrix;
- write a report into one Excel file with several sheets, and draw charts;
- organise the final project as a script that runs again every month.

From SAS to pandas - a two-way report table:

```sas
proc tabulate data=portfolio;
  class segment stage;
  var outstanding;
  table segment all, (stage all) * outstanding * sum;
run;
```

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")
portfolio = loans.merge(clients[["client_id", "segment"]], on="client_id")

portfolio.pivot_table(index="segment", columns="stage", values="outstanding",
                      aggfunc="sum", margins=True, margins_name="all").round(2)
```

Sessions 14 and 15 gave you the data and the numbers. Today they become a report.

## 1. Pivot tables

### `pivot_table`: groups in rows and columns

`pivot_table` is a `groupby` with two keys, where the second key goes into the
columns - `PROC TABULATE`, or Excel's pivot table:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.pivot_table(index="product", columns="currency", values="outstanding", aggfunc="sum").round(0)
```

Where a combination has no rows, the cell is `NaN`. `fill_value=0` writes 0 instead,
and `margins=True` adds the totals (the `ALL` of `PROC TABULATE`):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.pivot_table(index="product", columns="stage", values="loan_id", aggfunc="count",
                  fill_value=0, margins=True, margins_name="total")
```

Several values and several functions give a column header with two levels:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
table = loans.pivot_table(index="stage", columns="currency",
                          values=["outstanding", "interest_rate"],
                          aggfunc={"outstanding": "sum", "interest_rate": "mean"})
print(table.round(2))
print(table.columns.tolist()[:3])            # (value, currency) pairs
print(table["outstanding"].round(2))         # one block of columns
```

Large numbers come out as `1.101848e+08`. A display format for the whole session -
only the display changes, not the values:

```python run
import pandas as pd

pd.options.display.float_format = "{:,.2f}".format          # 110,184,825.28
loans = pd.read_csv("data/loans.csv")
print(loans.pivot_table(index="currency", columns="stage", values="outstanding", aggfunc="sum"))
pd.reset_option("display.float_format")                      # back to the default
```

A list of functions - the count and the sum side by side (`N` and `SUM` in
`PROC TABULATE`):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
table = loans.pivot_table(index="product", columns="stage", values="outstanding",
                          aggfunc=["count", "sum"], fill_value=0)
with pd.option_context("display.float_format", "{:,.0f}".format):   # this format only here
    print(table)
```

The rows in the order of the report, not alphabetical: `reindex` with the list of
labels:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")
portfolio = loans.merge(clients[["client_id", "segment"]], on="client_id")
table = portfolio.pivot_table(index="segment", columns="stage", values="loan_id", aggfunc="count")
print(table)
print(table.reindex(["retail", "sme", "corporate"]))                     # the order of the report
```

### `unstack`: a pivot from a `groupby`

A `groupby` with two keys (session 15) gives a long Series; `unstack` moves the last
key into the columns - the same table:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
long = loans.groupby(["product", "stage"])["outstanding"].sum()
print(long.head(4))
wide = long.unstack(fill_value=0).round(2)
wide
```

### `pivot` without aggregation

`pivot` only reshapes: every (row, column) pair must appear **once**. It is the right
tool for a monthly history - one row per client, one column per month (`PROC
TRANSPOSE`):

```python run
import pandas as pd

history = pd.read_csv("data/ratings_history.csv")
wide = history.pivot(index="client_id", columns="month_end", values="rating")
print(wide.shape)
wide.iloc[:5, -4:]                           # 5 clients, the last 4 months
```

If a pair appears twice, `pivot` stops with `ValueError: Index contains duplicate
entries` - a good check. `pivot_table` would aggregate them silently (the mean, by
default).

### `pd.crosstab`: counts and shares

`pd.crosstab` counts the combinations of two columns - `PROC FREQ; TABLES a * b;`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["dpd_bucket"] = pd.cut(loans["days_past_due"], bins=[-1, 0, 30, 90, float("inf")],
                             labels=["current", "1-30", "31-90", "90+"])
print(pd.crosstab(loans["product"], loans["dpd_bucket"], margins=True))
pd.crosstab(loans["product"], loans["dpd_bucket"], normalize="index").round(3)   # row %
```

`normalize="index"` gives the share of each row (each row sums to 1), `"columns"` of
each column, `True` of the whole table. With `values=` and `aggfunc=`, `crosstab`
sums amounts instead of counting rows.

`crosstab` with amounts - the outstanding by product and DPD bucket, in EUR
thousands:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
bucket = pd.cut(loans["days_past_due"], bins=[-1, 0, 30, 90, float("inf")],
                labels=["current", "1-30", "31-90", "90+"]).rename("dpd_bucket")
amounts = pd.crosstab(loans["product"], bucket, values=loans["outstanding"] / 1000,
                      aggfunc="sum").fillna(0).round(0)
amounts
```

### Percentages of the total

Divide a table by its row totals with `div(..., axis=0)`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")
portfolio = loans.merge(clients[["client_id", "segment"]], on="client_id")
table = portfolio.pivot_table(index="segment", columns="stage", values="outstanding", aggfunc="sum")
shares = table.div(table.sum(axis=1), axis=0)          # each row / its total
(shares * 100).round(1)
```

Two-level column names (a `pivot_table` with several values) are awkward in Excel
and in later code. Join them into one level:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
table = loans.pivot_table(index="product", columns="stage", values="outstanding",
                          aggfunc=["count", "sum"], fill_value=0)
table.columns = [f"{func}_stage{stage}" for func, stage in table.columns]
table = table.reset_index()
print(table.columns.tolist())
table.head(3)
```

::: tip Try it
A table with the regions in the rows and the segments in the columns: the **number**
of clients (`clients.csv`), with totals. Then the same as shares of each region.
Which region has the most corporate clients?
:::

## 2. From wide to long: `melt`

`melt` is the opposite of `pivot`: columns become rows - `PROC TRANSPOSE` back, or
SQL `UNPIVOT`. A budget in Excel often comes wide, one column per month:

```python run
import pandas as pd

budget = pd.DataFrame({
    "segment": ["retail", "sme", "corporate"],
    "2026-10": [7.0, 31.5, 93.0],
    "2026-11": [7.1, 31.8, 93.5],
    "2026-12": [7.3, 32.0, 94.0],
})
long = budget.melt(id_vars="segment", var_name="month", value_name="plan_m_eur")
long
```

Long data is what `groupby`, `merge` and charts want: one row per fact. The way back
is `pivot`:

```python run
import pandas as pd

budget = pd.DataFrame({"segment": ["retail", "sme"], "2026-10": [7.0, 31.5], "2026-11": [7.1, 31.8]})
long = budget.melt(id_vars="segment", var_name="month", value_name="plan")
print(long.groupby("month")["plan"].sum())                     # easy in long form
print(long.pivot(index="segment", columns="month", values="plan"))
```

`value_vars` melts only some of the columns. The monthly ratings, wide (section 1),
back to long - the same table as the file:

```python run
import pandas as pd

history = pd.read_csv("data/ratings_history.csv")
wide = history.pivot(index="client_id", columns="month_end", values="rating").reset_index()
q3 = wide.melt(id_vars="client_id", value_vars=["2026-07-31", "2026-08-31", "2026-09-30"],
               var_name="month_end", value_name="rating")
print(q3.shape)
print(q3.sort_values(["client_id", "month_end"]).head(4))
```

::: details Check yourself: a table has 150 clients and 12 month columns. How many rows does `melt(id_vars="client_id")` give?
150 x 12 = 1800 rows - one per client and month, with three columns: `client_id`,
`variable` (the month) and `value`. That is the shape of `ratings_history.csv`.
:::

## 3. Dates and month ends

### Text to dates

Session 7 parsed dates one by one with `datetime.strptime`. `pd.to_datetime` does the
whole column; `format=` says how, `errors="coerce"` turns a bad date into `NaT` (the
`NaN` of dates):

```python run
import pandas as pd

raw = pd.Series(["30.09.2026", "31.08.2026", "31.13.2026", ""])
dates = pd.to_datetime(raw, format="%d.%m.%Y", errors="coerce")
print(dates)
print(dates.isna().sum(), "bad or missing")
```

`read_csv(parse_dates=...)` (session 14) does the same while reading. A date column
has the `.dt` methods:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv", parse_dates=["start_date", "maturity_date"])
parts = pd.DataFrame({
    "start": loans["start_date"],
    "year": loans["start_date"].dt.year,
    "quarter": loans["start_date"].dt.quarter,
    "month_name": loans["start_date"].dt.strftime("%b %Y"),       # like the MONYY7. format
    "weekday": loans["start_date"].dt.day_name(),
})
parts.head()
```

Real files mix formats. `client_register.csv` has the registration date in four
formats (session 7). Try one format after another, and keep the first that works -
a `COALESCE` of the parsing attempts:

```python run
import pandas as pd

register = pd.read_csv("data/client_register.csv")
raw = register["registered"]
parsed = pd.to_datetime(raw, format="%Y-%m-%d", errors="coerce")
for fmt in ["%d.%m.%Y", "%d/%m/%Y", "%Y%m%d"]:
    parsed = parsed.fillna(pd.to_datetime(raw, format=fmt, errors="coerce"))
print(parsed.isna().sum(), "not parsed")
print(pd.DataFrame({"raw": raw, "parsed": parsed}).drop_duplicates("raw").head(6))
```

### Month ends: `INTNX`

`pd.offsets.MonthEnd` moves a date to a month end - `INTNX('month', date, n, 'end')`:

```python run
import pandas as pd

d = pd.Timestamp("2026-09-15")
print(d + pd.offsets.MonthEnd(0))          # this month's end      INTNX('month', d, 0, 'end')
print(d + pd.offsets.MonthEnd(1))          # the next month end (from the 15th: this one!)
print(d - pd.offsets.MonthEnd(1))          # the previous month end
print(pd.Timestamp("2026-09-30") + pd.offsets.MonthEnd(1))   # from a month end: the next one
print(pd.Timestamp("2026-01-31") + pd.DateOffset(months=1))  # one month later: 2026-02-28
```

::: warning `MonthEnd(1)` means "the next month end"
From the 15th, the next month end is the end of **this** month; from the 30th of
September, it is the end of October. To get the end of the month of any date, use
`MonthEnd(0)`.
:::

The usual report dates from one report date - the start of the year, the end of the
previous month, the same day one year ago:

```python run
import pandas as pd

report_date = pd.Timestamp("2026-09-30")
print(report_date - pd.offsets.YearBegin(1))      # 2026-01-01  INTNX('year', d, 0, 'begin')
print(report_date - pd.offsets.MonthEnd(1))       # 2026-08-31  the previous month end
print(report_date - pd.DateOffset(years=1))       # 2025-09-30  one year ago
print(report_date + pd.offsets.QuarterEnd(0))     # 2026-09-30  the end of this quarter
```

All the month ends of a period - the report dates of a year:

```python run
import pandas as pd

ends = pd.date_range("2025-10-31", "2026-09-30", freq="ME")
print(len(ends))
print(ends.strftime("%Y-%m-%d").tolist())
```

(`freq="ME"` is "month end" since pandas 2.2; older code writes `"M"`, which now gives
a warning.)

Filter rows by a date range - `between` works with dates too (both ends included):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv", parse_dates=["start_date", "maturity_date"])
q3 = loans[loans["start_date"].between("2026-07-01", "2026-09-30")]
print(len(q3), "loans started in Q3 2026")
report_date = pd.Timestamp("2026-09-30")
due_soon = loans[loans["maturity_date"].between(report_date, report_date + pd.DateOffset(months=3))]
print(len(due_soon), "loans mature in the next 3 months")
```

### Months between: `INTCK`

The number of month boundaries between two dates - `INTCK('month', a, b)`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv", parse_dates=["start_date", "maturity_date"])
report_date = pd.Timestamp("2026-09-30")

def months_between(a, b):
    """INTCK('month', a, b) for date columns or dates."""
    return (b.year - a.year) * 12 + (b.month - a.month)

loans["age_months"] = months_between(loans["start_date"].dt, report_date)
loans["left_months"] = months_between(report_date, loans["maturity_date"].dt)
loans[["loan_id", "start_date", "maturity_date", "age_months", "left_months"]].head()
```

Bands of the loan age - `pd.cut` (session 15) on the months:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv", parse_dates=["start_date"])
report_date = pd.Timestamp("2026-09-30")
age = (report_date.year - loans["start_date"].dt.year) * 12 + (report_date.month - loans["start_date"].dt.month)
bands = pd.cut(age, bins=[-1, 6, 12, 36, 60, float("inf")],
               labels=["0-6m", "7-12m", "1-3y", "3-5y", "5y+"]).rename("age")
loans.groupby(bands, observed=True)["outstanding"].agg(["count", "sum"]).round(0)
```

The difference of two dates is a `Timedelta` - days, not months:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv", parse_dates=["start_date", "maturity_date"])
term = loans["maturity_date"] - loans["start_date"]
print(term.head(3))
print((term.dt.days / 365.25).round(1).head(3).tolist())       # years
```

### Periods: a month as a value

`to_period("M")` turns a date into its month - good for grouping and for labels
(`2026-09`):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv", parse_dates=["start_date"])
loans["start_month"] = loans["start_date"].dt.to_period("M")
recent = loans[loans["start_date"] >= "2026-01-01"]               # a date filter with a text date
print(recent.groupby("start_month")["amount"].sum().round(0))
print(pd.Period("2026-09", freq="M").end_time.date())              # back to the last day
```

Periods can be added and subtracted - a month plus one, the months between two
periods:

```python run
import pandas as pd

september = pd.Period("2026-09", freq="M")
print(september + 1, september - 12)               # 2026-10 2025-09
print((september - pd.Period("2025-10", freq="M")).n, "months")    # 11
print(september.strftime("%B %Y"))                 # a label for a report title
```

::: tip Try it
For each loan: the month end of its start date, and the number of months until the
report date 30.09.2026. How many loans are younger than 6 months?
:::

## 4. Monthly history: LAG, changes, running totals

`balances_monthly.csv` has the outstanding and the days past due of every loan at 12
month ends - the kind of table a monthly risk report is built from.

### The portfolio over time

```python run
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"])
monthly = balances.groupby("month_end").agg(loans=("loan_id", "count"),
                                            outstanding=("outstanding", "sum"))
monthly["outstanding_m"] = (monthly["outstanding"] / 1e6).round(2)
monthly["change_m"] = monthly["outstanding_m"].diff().round(2)           # DIF
monthly["change_pct"] = (monthly["outstanding"].pct_change() * 100).round(2)
monthly[["loans", "outstanding_m", "change_m", "change_pct"]]
```

`diff()` is the value minus the previous row (`DIF`), `pct_change()` the relative
change. The first month has no previous one: `NaN`.

### LAG by loan

For each loan, the value of the previous month: sort, then `shift` inside the group -
`LAG` with `BY loan_id`, or `LAG() OVER (PARTITION BY loan_id ORDER BY month_end)`:

```python run
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"])
balances = balances.sort_values(["loan_id", "month_end"])
by_loan = balances.groupby("loan_id")
balances["prev_outstanding"] = by_loan["outstanding"].shift(1)
balances["repaid"] = (balances["prev_outstanding"] - balances["outstanding"]).round(2)
balances["prev_dpd"] = by_loan["days_past_due"].shift(1)
balances.loc[balances["loan_id"] == "L000002", ["month_end", "outstanding", "prev_outstanding", "repaid", "prev_dpd"]].tail(4)
```

::: warning Sort first
`shift(1)` takes the previous **row**. If the rows are not in month order inside each
loan, it takes a wrong month - and nothing warns you. Always `sort_values([key,
date])` first (in SAS, `PROC SORT` before `BY`).
:::

A loan that **crossed** 30 days past due this month - the flow into arrears:

```python run
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"]).sort_values(["loan_id", "month_end"])
balances["prev_dpd"] = balances.groupby("loan_id")["days_past_due"].shift(1)
new_late = balances[(balances["prev_dpd"] <= 30) & (balances["days_past_due"] > 30)]
print(len(new_late), "times a loan crossed 30 days past due")
new_late.groupby("month_end").size()
```

The last month of each loan - `LAST.loan_id` - and the month a loan first appears
in the history (new loans per month):

```python run
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"]).sort_values(["loan_id", "month_end"])
last = balances.groupby("loan_id").tail(1)                         # IF LAST.loan_id
print(last["month_end"].value_counts())
first_month = balances.groupby("loan_id")["month_end"].min()       # the first appearance
print(first_month.value_counts().sort_index().tail(4))
```

### Running totals: `RETAIN`

`cumsum`, `cummax`, `cumcount` inside a group - a `RETAIN` variable that restarts
with each `BY` group:

```python run
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"]).sort_values(["loan_id", "month_end"])
balances["late"] = (balances["days_past_due"] > 0).astype(int)
balances["months_late"] = balances.groupby("loan_id")["late"].cumsum()          # RETAIN n; n + late;
balances["worst_dpd"] = balances.groupby("loan_id")["days_past_due"].cummax()   # the worst so far
balances[balances["loan_id"] == "L000002"][["month_end", "days_past_due", "months_late", "worst_dpd"]]
```

The portfolio by month and segment - a pivot with the months in the rows, the shape
for a chart:

```python run
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"])
segments = pd.read_csv("data/loans.csv")[["loan_id", "client_id"]].merge(
    pd.read_csv("data/clients.csv")[["client_id", "segment"]], on="client_id")
monthly = balances.merge(segments, on="loan_id", validate="many_to_one")
by_month = monthly.pivot_table(index="month_end", columns="segment", values="outstanding", aggfunc="sum") / 1e6
by_month.round(2).tail(4)
```

The DPD buckets per month - how the arrears move over the year:

```python run
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"])
bucket = pd.cut(balances["days_past_due"], bins=[-1, 0, 30, 90, float("inf")],
                labels=["current", "1-30", "31-90", "90+"])
pd.crosstab(balances["month_end"].dt.strftime("%Y-%m"), bucket).tail(6)
```

### Moving averages and a date index

`rolling(3)` looks at the last 3 rows - a 3-month average smooths the monthly
noise:

```python run
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"])
total = balances.groupby("month_end")["outstanding"].sum() / 1e6
trend = pd.DataFrame({"total_m": total.round(2), "avg_3m": total.rolling(3).mean().round(2)})
trend.tail(5)
```

With dates in the index, `resample` groups by calendar periods - here, quarters
(`QE` = quarter end):

```python run
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"])
total = balances.groupby("month_end")["outstanding"].sum()
print((total.resample("QE").last() / 1e6).round(2))          # the value at each quarter end
```

::: tip Try it
For each month end: the number of loans more than 30 days past due and their share
of the outstanding. In which month was the share the highest?
:::

## 5. The rating migration matrix

How did the ratings of the clients move over the year? The rating at the start of the
history in the rows, the rating now in the columns - a **migration matrix**, a
standard table of credit risk:

```python run
import pandas as pd

history = pd.read_csv("data/ratings_history.csv")
start = history[history["month_end"] == "2025-10-31"][["client_id", "rating"]]
end = history[history["month_end"] == "2026-09-30"][["client_id", "rating"]]
pairs = start.merge(end, on="client_id", suffixes=("_start", "_end"), validate="one_to_one")

matrix = pd.crosstab(pairs["rating_start"], pairs["rating_end"])
matrix
```

The diagonal is "no change"; above it, the client got a worse rating (a higher
number); below it, a better one. As shares of each row - the probability of moving
from one rating to another:

```python run
import pandas as pd

history = pd.read_csv("data/ratings_history.csv")
start = history[history["month_end"] == "2025-10-31"][["client_id", "rating"]]
end = history[history["month_end"] == "2026-09-30"][["client_id", "rating"]]
pairs = start.merge(end, on="client_id", suffixes=("_start", "_end"))

shares = pd.crosstab(pairs["rating_start"], pairs["rating_end"], normalize="index")
(shares * 100).round(0)
```

The summary - upgrades, downgrades, stable - is a comparison of the two columns, no
matrix needed:

```python run
import numpy as np
import pandas as pd

history = pd.read_csv("data/ratings_history.csv")
start = history[history["month_end"] == "2025-10-31"][["client_id", "rating"]]
end = history[history["month_end"] == "2026-09-30"][["client_id", "rating"]]
pairs = start.merge(end, on="client_id", suffixes=("_start", "_end"))

pairs["move"] = np.select(
    [pairs["rating_end"] > pairs["rating_start"], pairs["rating_end"] < pairs["rating_start"]],
    ["downgrade", "upgrade"], default="stable")
print(pairs["move"].value_counts())
print("default rate:", round((pairs["rating_end"] == 10).mean(), 4))
```

With the grades as labels, and all ratings in the rows and columns even when a
rating has no client (`reindex`, `fill_value=0`) - the matrix keeps its square shape
every month:

```python run
import pandas as pd

history = pd.read_csv("data/ratings_history.csv")
grade = pd.read_csv("data/rating_scale.csv").set_index("rating")["grade"]
start = history[history["month_end"] == "2026-08-31"][["client_id", "rating"]]
end = history[history["month_end"] == "2026-09-30"][["client_id", "rating"]]
pairs = start.merge(end, on="client_id", suffixes=("_start", "_end"))

matrix = pd.crosstab(pairs["rating_start"], pairs["rating_end"])
matrix = matrix.reindex(index=range(1, 11), columns=range(1, 11), fill_value=0)
matrix.index = matrix.index.map(grade)
matrix.columns = matrix.columns.map(grade)
matrix
```

The same matrix weighted by **exposure** - how much money moved, not how many
clients:

```python run
import pandas as pd

history = pd.read_csv("data/ratings_history.csv")
exposure = pd.read_csv("data/loans.csv").groupby("client_id")["outstanding"].sum()
start = history[history["month_end"] == "2025-10-31"][["client_id", "rating"]]
end = history[history["month_end"] == "2026-09-30"][["client_id", "rating"]]
pairs = start.merge(end, on="client_id", suffixes=("_start", "_end"))
pairs["exposure_m"] = pairs["client_id"].map(exposure).fillna(0) / 1e6

pd.crosstab(pairs["rating_start"], pairs["rating_end"], values=pairs["exposure_m"],
            aggfunc="sum").fillna(0).round(1)
```

::: info The same in SQL (session 13)
`SELECT s.rating, e.rating, COUNT(*) FROM history s JOIN history e ON ... GROUP BY 1,
2` gives the long form; `crosstab` gives the matrix directly. In SAS: `PROC FREQ;
TABLES rating_start * rating_end / NOCOL NOPERCENT;`.
:::

::: tip Try it
Make the matrix between 31.08.2026 and 30.09.2026 (one month). Is the diagonal
stronger than for the whole year? Why would it be?
:::

## 6. An Excel report with several sheets

### `ExcelWriter`

One `to_excel` writes one sheet. For several sheets in one file, open a
`pd.ExcelWriter` and write each table with its `sheet_name` - `ODS EXCEL` with
`SHEET_NAME=`:

```python run
from pathlib import Path
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")
portfolio = loans.merge(clients[["client_id", "segment"]], on="client_id")

by_stage = portfolio.pivot_table(index="segment", columns="stage", values="outstanding",
                                 aggfunc="sum", margins=True, margins_name="total").round(2)
by_product = portfolio.groupby("product", as_index=False).agg(
    loans=("loan_id", "count"), outstanding=("outstanding", "sum")).round(2)

Path("out").mkdir(exist_ok=True)
with pd.ExcelWriter("out/portfolio_2026-09.xlsx") as writer:
    by_stage.to_excel(writer, sheet_name="segment x stage")
    by_product.to_excel(writer, sheet_name="products", index=False)
    portfolio.to_excel(writer, sheet_name="data", index=False)

check = pd.read_excel("out/portfolio_2026-09.xlsx", sheet_name=None)     # read back
{name: df.shape for name, df in check.items()}
```

`with` closes the file at the end (session 9) - only then is it a valid Excel file.
`index=False` leaves out the row numbers; keep the index when it holds the labels
(the segments of the pivot).

### A title above the table, widths and number formats

`startrow` leaves room for a title; then `writer.sheets[...]` gives the openpyxl
worksheet (session 9) to write the title, set the widths and the number format:

```python run
from pathlib import Path
import pandas as pd

loans = pd.read_csv("data/loans.csv")
table = loans.groupby("product", as_index=False).agg(
    loans=("loan_id", "count"), outstanding=("outstanding", "sum"), avg_rate=("interest_rate", "mean"))

Path("out").mkdir(exist_ok=True)
with pd.ExcelWriter("out/products.xlsx") as writer:
    table.to_excel(writer, sheet_name="products", index=False, startrow=2)
    sheet = writer.sheets["products"]
    sheet["A1"] = "Outstanding by product, 30.09.2026"
    for column, width in {"A": 18, "B": 8, "C": 18, "D": 10}.items():
        sheet.column_dimensions[column].width = width
    for row in sheet.iter_rows(min_row=4, min_col=3, max_col=3):     # the outstanding column
        for cell in row:
            cell.number_format = "#,##0.00"

print(pd.read_excel("out/products.xlsx", skiprows=2).head(3))
```

The numbers stay numbers in Excel (they can be summed); only their display changes.
(More formatting - bold headers, frozen panes, colours, a chart inside the file - in
Self-study.)

Several tables on **one** sheet - each with its `startrow`, one under another:

```python run
from pathlib import Path
import pandas as pd

loans = pd.read_csv("data/loans.csv")
by_stage = loans.groupby("stage", as_index=False)["outstanding"].sum()
by_currency = loans.groupby("currency", as_index=False)["outstanding"].sum()

Path("out").mkdir(exist_ok=True)
with pd.ExcelWriter("out/one_sheet.xlsx") as writer:
    by_stage.to_excel(writer, sheet_name="summary", index=False, startrow=0)
    by_currency.to_excel(writer, sheet_name="summary", index=False, startrow=len(by_stage) + 3)

print(pd.read_excel("out/one_sheet.xlsx", header=None))
```

Add or replace one sheet of an existing file - `mode="a"` with `if_sheet_exists`:

```python run
from pathlib import Path
import pandas as pd

Path("out").mkdir(exist_ok=True)
pd.DataFrame({"x": [1, 2]}).to_excel("out/book.xlsx", sheet_name="first", index=False)

with pd.ExcelWriter("out/book.xlsx", mode="a", if_sheet_exists="replace") as writer:
    pd.DataFrame({"y": [3]}).to_excel(writer, sheet_name="second", index=False)
    pd.DataFrame({"x": [10, 20, 30]}).to_excel(writer, sheet_name="first", index=False)

{name: df.shape for name, df in pd.read_excel("out/book.xlsx", sheet_name=None).items()}
```

A report is often a dictionary of tables - one loop writes them all, in order:

```python run
from pathlib import Path
import pandas as pd

loans = pd.read_csv("data/loans.csv")
tables = {
    "by stage": loans.groupby("stage", as_index=False)["outstanding"].sum(),
    "by product": loans.groupby("product", as_index=False)["outstanding"].sum(),
    "top 10": loans.nlargest(10, "outstanding")[["loan_id", "client_id", "outstanding"]],
}
Path("out").mkdir(exist_ok=True)
with pd.ExcelWriter("out/report_loop.xlsx") as writer:
    for name, table in tables.items():
        table.to_excel(writer, sheet_name=name, index=False)

list(pd.read_excel("out/report_loop.xlsx", sheet_name=None))
```

For a system that wants CSV - the export side of session 14: `;`, decimal comma, a
BOM so that Excel shows the Cyrillic right:

```python run
from pathlib import Path
import pandas as pd

loans = pd.read_csv("data/loans.csv", parse_dates=["start_date", "maturity_date"])
Path("out").mkdir(exist_ok=True)
loans.head(3).to_csv("out/loans_for_excel.csv", sep=";", decimal=",", index=False,
                     encoding="utf-8-sig", date_format="%d.%m.%Y")
print(Path("out/loans_for_excel.csv").read_text(encoding="utf-8-sig"))
```

::: warning Do not round before you sum
Round only the numbers you **show**. If you round every loan and then sum, the total
in the report is not the total of the data. Keep full precision in the calculations,
and round the final table (or use the number format).
:::

::: tip Try it
Add a third sheet "migration" with the migration matrix of section 5 to
`portfolio_2026-09.xlsx`, and read the file back to check the sheet names.
:::

## 7. Charts

pandas draws with **matplotlib**: `df.plot(...)` makes the chart, `plt.savefig`
writes it to a file. Import `matplotlib.pyplot` yourself (on the site, that also loads
it):

```python run
import matplotlib.pyplot as plt
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")
portfolio = loans.merge(clients[["client_id", "segment"]], on="client_id")
table = portfolio.pivot_table(index="segment", columns="stage", values="outstanding", aggfunc="sum") / 1e6

ax = table.plot(kind="bar", stacked=True, figsize=(6, 4))
ax.set_title("Outstanding by segment and stage")
ax.set_ylabel("EUR million")
ax.set_xlabel("")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()
```

A line over time - the monthly total of section 4:

```python run
import matplotlib.pyplot as plt
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"])
total = balances.groupby("month_end")["outstanding"].sum() / 1e6

ax = total.plot(marker="o", figsize=(7, 3.5))
total.rolling(3).mean().plot(ax=ax, linestyle="--", label="3-month average")
ax.set_title("Portfolio outstanding")
ax.set_ylabel("EUR million")
ax.legend(["month end", "3-month average"])
plt.tight_layout()
plt.show()
```

Save the chart as a file for the report or a presentation:

```python run
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

loans = pd.read_csv("data/loans.csv")
counts = loans["product"].value_counts().sort_values()

ax = counts.plot(kind="barh", figsize=(6, 3.5), title="Loans by product")
plt.tight_layout()
Path("out").mkdir(exist_ok=True)
plt.savefig("out/products.png", dpi=150)
print(Path("out/products.png").stat().st_size > 0)
```

The distribution of one column - a histogram (`PROC UNIVARIATE` with `HISTOGRAM`):

```python run
import matplotlib.pyplot as plt
import pandas as pd

loans = pd.read_csv("data/loans.csv")
ax = loans["interest_rate"].plot(kind="hist", bins=20, figsize=(6, 3.5), edgecolor="white")
ax.set_title("Interest rates of the loans")
ax.set_xlabel("%")
plt.tight_layout()
plt.show()
```

Two columns against each other - a scatter plot:

```python run
import matplotlib.pyplot as plt
import pandas as pd

loans = pd.read_csv("data/loans.csv")
ax = loans.plot(kind="scatter", x="interest_rate", y="days_past_due", alpha=0.5, figsize=(6, 3.5))
ax.set_title("Interest rate and days past due")
plt.tight_layout()
plt.show()
```

Several charts in a loop - `plt.close()` after each saved file:

```python run
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

loans = pd.read_csv("data/loans.csv")
Path("out").mkdir(exist_ok=True)
for column in ["product", "currency", "stage"]:
    ax = loans.groupby(column)["outstanding"].sum().div(1e6).plot(kind="bar", title=f"Outstanding by {column}, EUR m")
    plt.tight_layout()
    plt.savefig(f"out/by_{column}.png")
    plt.close()
print(sorted(p.name for p in Path("out").glob("by_*.png")))
```

In a script (not a notebook), `plt.show()` opens a window and waits; for a report,
only `savefig` - and `plt.close()` after it, so that the next chart starts empty.

::: tip Try it
A bar chart of the migration summary of section 5 (upgrades, stable, downgrades).
:::

## 8. The final project: from script to process

The [final project](../project) brings all sessions together: a monthly report that
runs again for every new month. The brief is on the project page; here is the shape of
the code.

A folder with the modules of the course and one main script:

```text
portfolio-report/
  README.md                  what the report does, how to run it
  requirements.txt
  report.py                  main(): load -> validate -> transform -> aggregate -> write
  portfolio_utils.py         session 10: functions (buckets, EL, parsing)
  homework_nomenclature.py   session 12: Nomenclature, BandedNomenclature, Registry
  data/                      the input (not in Git if real)
  out/                       the reports (not in Git: .gitignore)
```

`report.py` - every step a function that can be tested alone, the report date as a
parameter (session 10):

```python
"""Monthly portfolio report.  Run:  python report.py 2026-09-30"""
import sys
from pathlib import Path

import pandas as pd

DATA = Path("data")
OUT = Path("out")


def load(report_date):
    """Files and the database -> DataFrames (sessions 9, 13, 14)."""
    ...


def validate(tables):
    """Nomenclatures (session 12): unknown codes, values out of range -> a reject table."""
    ...


def transform(tables, report_date):
    """Types, new columns (buckets, PD, EL), joins (session 15)."""
    ...


def aggregate(portfolio):
    """The report tables: pivots, migration, trend (sessions 15, 16)."""
    ...


def write(tables, report_date):
    """One Excel file with several sheets and a chart (session 16)."""
    ...


def main(report_date):
    tables = load(report_date)
    rejects = validate(tables)
    portfolio = transform(tables, report_date)
    report = aggregate(portfolio)
    write(report | {"rejects": rejects}, report_date)


if __name__ == "__main__":
    main(pd.Timestamp(sys.argv[1] if len(sys.argv) > 1 else "2026-09-30"))
```

The same shape, small enough to run here - every step a function, the date a
parameter:

```python run
from pathlib import Path
import pandas as pd

DATA = Path("data")


def load():
    return {name: pd.read_csv(DATA / f"{name}.csv") for name in ["loans", "clients", "rating_scale"]}


def transform(t, lgd=0.45):
    full = (t["loans"].merge(t["clients"][["client_id", "segment", "rating"]], on="client_id", validate="many_to_one")
                      .merge(t["rating_scale"], on="rating", validate="many_to_one"))
    return full.assign(el=lambda d: (d["pd_min"] + d["pd_max"]) / 2 * lgd * d["outstanding"])


def aggregate(full):
    return {"summary": pd.DataFrame({"outstanding": [full["outstanding"].sum()], "el": [full["el"].sum()]}).round(2),
            "segment x stage": full.pivot_table(index="segment", columns="stage", values="outstanding",
                                                aggfunc="sum", margins=True, margins_name="total").round(2)}


def main(report_date):
    report = aggregate(transform(load()))
    Path("out").mkdir(exist_ok=True)
    path = Path("out") / f"report_{report_date:%Y-%m-%d}.xlsx"
    with pd.ExcelWriter(path) as writer:
        for name, table in report.items():
            table.to_excel(writer, sheet_name=name)
    return path, report["summary"]


main(pd.Timestamp("2026-09-30"))
```

Rules that make a report reliable:

- **No hard-coded dates or paths** in the functions: the report date is a parameter.
- **Check the totals**: the total outstanding of the report = the total of the input;
  the EL = 1,140,106.56 for 30.09.2026.
- **Rejects are part of the output**: the rows that failed the validation, with the
  reason, in their own sheet - never silently dropped.
- **Run it twice**: the second run gives the same file. Then run it for 31.08.2026.
- **Commit** after each step that works (session 10).

## 9. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root (with the virtual environment active):

```bash
python 16-pandas-reports-project/practice/task1-pivot.py
```

The tasks that write files write them into `out/` (ignored by Git).

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-pivot.py` | `pivot_table` with totals, `crosstab` with shares, `melt` back |
| 2 | `task2-dates.py` | Parse dates, month ends, months between, periods |
| 3 | `task3-monthly-history.py` | LAG by loan, monthly totals, months in arrears |
| 4 | `task4-migration.py` | The migration matrix, upgrades and downgrades, the default rate |
| 5 | `task5-excel-report.py` | A three-sheet Excel report, read back and checked |
| 6 | `task6-chart.py` (Optional) | A bar chart and a line chart saved as PNG files |

## Summary

| SQL / SAS | pandas |
|-----------|--------|
| `PROC TABULATE`, `PIVOT` | `pivot_table(index, columns, values, aggfunc, margins=True, fill_value=0)` |
| `PROC TRANSPOSE` | `pivot` (no aggregation), `unstack`; back: `melt` |
| `PROC FREQ; TABLES a * b` | `pd.crosstab(a, b, normalize="index", margins=True)` |
| SAS dates, `INPUT(x, ddmmyy10.)` | `pd.to_datetime(format=..., errors="coerce")`, `.dt` |
| `INTNX('month', d, 0, 'end')` | `d + pd.offsets.MonthEnd(0)`; `pd.date_range(freq="ME")` |
| `INTCK('month', a, b)` | `(b.year - a.year) * 12 + (b.month - a.month)` |
| `MONYY7.` | `.dt.to_period("M")`, `.dt.strftime("%b %Y")` |
| `LAG`, `DIF` by group | `sort_values`, then `groupby(key)[col].shift(1)` / `diff()` |
| `RETAIN` | `groupby(key)[col].cumsum()` / `cummax()` |
| migration matrix | merge two month ends, `pd.crosstab(start, end)` |
| `ODS EXCEL`, `PROC EXPORT` | `pd.ExcelWriter` + `to_excel(writer, sheet_name=...)`; openpyxl for formats |
| `PROC SGPLOT` | `df.plot(kind=...)`, `plt.savefig` |

## Homework

1. `16-pandas-reports-project/homework.py` (in the homework repository): **the monthly
   report, part 1 of the project** - `build_report(data, report_date)` returns a
   dictionary of tables (summary, segment x stage, DPD buckets, migration, monthly
   trend, top clients) and `write_report(tables, path)` writes them into one Excel
   file. Every check must print `OK`.
2. The practice tasks you did not finish in class.
3. The [final project](../project): start from the homework, add the loading from the
   database, the validation with your nomenclatures, a chart, and Git.

## Self-study

This part is not covered in class. It is for reading at home: a report that looks
finished, charts with more control, and where to go after the course.

### A formatted Excel report

openpyxl (session 9) can style everything after pandas has written the data: fonts,
fills, number formats, frozen panes, filters, conditional colours - and a native Excel
chart:

```python run
from pathlib import Path
import pandas as pd
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Font, PatternFill

loans = pd.read_csv("data/loans.csv")
table = loans.groupby("product", as_index=False).agg(
    loans=("loan_id", "count"), outstanding=("outstanding", "sum")).sort_values("outstanding", ascending=False)

Path("out").mkdir(exist_ok=True)
with pd.ExcelWriter("out/formatted.xlsx") as writer:
    table.to_excel(writer, sheet_name="products", index=False)
    ws = writer.sheets["products"]
    for cell in ws[1]:                                              # the header row
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E78")
    for (cell,) in ws.iter_rows(min_row=2, min_col=3, max_col=3):
        cell.number_format = "#,##0"
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["C"].width = 16
    ws.freeze_panes = "A2"                                          # the header stays visible
    ws.auto_filter.ref = ws.dimensions                              # filter buttons
    last = ws.max_row
    ws.conditional_formatting.add(f"C2:C{last}", ColorScaleRule(start_type="min", start_color="FFFFFF",
                                                                end_type="max", end_color="F8696B"))
    chart = BarChart()
    chart.title = "Outstanding by product"
    chart.add_data(Reference(ws, min_col=3, min_row=1, max_row=last), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=2, max_row=last))
    ws.add_chart(chart, "E2")

print(pd.read_excel("out/formatted.xlsx").shape)
```

The chart is an Excel chart: it changes when somebody edits the numbers in the
file. (A PNG from matplotlib can be put in with `openpyxl.drawing.image.Image`; it
needs the Pillow package.)

**Exercises**

1. Write the migration matrix (section 5) to a sheet and colour it with a
   `ColorScaleRule` from white (0) to red (the maximum). Freeze the first row and the
   first column (`freeze_panes = "B2"`).
2. Write the segment x stage pivot with `margins=True` and make the "total" row
   bold.

::: details Answer
```python
from pathlib import Path
import pandas as pd
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Font

history = pd.read_csv("data/ratings_history.csv")
start = history[history["month_end"] == "2025-10-31"][["client_id", "rating"]]
end = history[history["month_end"] == "2026-09-30"][["client_id", "rating"]]
pairs = start.merge(end, on="client_id", suffixes=("_start", "_end"))
matrix = pd.crosstab(pairs["rating_start"], pairs["rating_end"])

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")
pivot = (loans.merge(clients[["client_id", "segment"]], on="client_id")
              .pivot_table(index="segment", columns="stage", values="outstanding",
                           aggfunc="sum", margins=True, margins_name="total").round(2))

Path("out").mkdir(exist_ok=True)
with pd.ExcelWriter("out/exercises.xlsx") as writer:
    matrix.to_excel(writer, sheet_name="migration")
    ws = writer.sheets["migration"]
    ws.freeze_panes = "B2"
    ws.conditional_formatting.add(f"B2:K11", ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF",
                                                            end_type="max", end_color="F8696B"))
    pivot.to_excel(writer, sheet_name="segment x stage")
    ws = writer.sheets["segment x stage"]
    for cell in ws[ws.max_row]:                    # the last row is "total"
        cell.font = Font(bold=True)
```
:::

### Charts in more depth

For full control, create the figure and its axes yourself and give each chart its
axes - here two charts side by side:

```python run
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

loans = pd.read_csv("data/loans.csv")
balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"])

fig, (left, right) = plt.subplots(1, 2, figsize=(10, 3.5))
loans.groupby("stage")["outstanding"].sum().plot(kind="bar", ax=left, color="#1F4E78")
left.set_title("By stage")
left.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1e6:,.0f}m"))
left.tick_params(axis="x", rotation=0)

balances.groupby("month_end")["outstanding"].sum().plot(ax=right, marker="o")
right.set_title("Monthly total")
right.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1e6:,.0f}m"))
right.set_xlabel("")

fig.suptitle("Portfolio, 30.09.2026")
fig.tight_layout()
plt.show()
```

`fig.savefig("chart.png", dpi=200)` saves the whole figure - 200 dpi is sharp enough
for a presentation.

**Exercise**

Draw the share of loans more than 30 days past due per month end (section 4, Try it)
as a line, with the y axis in percent (`FuncFormatter(lambda v, _: f"{v:.1%}")`), next
to a bar chart of the number of such loans.

::: details Answer
```python
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv", parse_dates=["month_end"])
balances["late_amount"] = balances["outstanding"].where(balances["days_past_due"] > 30, 0)
monthly = balances.groupby("month_end").agg(total=("outstanding", "sum"),
                                            late=("late_amount", "sum"),
                                            late_loans=("days_past_due", lambda d: (d > 30).sum()))
fig, (left, right) = plt.subplots(1, 2, figsize=(10, 3.5))
(monthly["late"] / monthly["total"]).plot(ax=left, marker="o", title="Share > 30 days")
left.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1%}"))
monthly["late_loans"].plot(kind="bar", ax=right, title="Loans > 30 days")
right.set_xticklabels([d.strftime("%m.%y") for d in monthly.index], rotation=45)
fig.tight_layout()
plt.show()
```
:::

### What next

You now have the tools for most of the daily work. Where to go from here, when you
need it:

- **Jupyter** (installed with `requirements.txt`): for exploring a new dataset step by
  step, with tables and charts under the code. Keep the final, repeatable report as a
  `.py` script.
- **The pandas documentation**: the [user guide](https://pandas.pydata.org/docs/user_guide/index.html)
  and the comparisons with [SAS](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sas.html)
  and [SQL](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html).
- **DuckDB**: SQL directly on DataFrames, CSV and Parquet files - your SQL, inside
  Python, very fast on large files.
- **polars**: a newer DataFrame library, faster than pandas on large data, with a
  different (expression-based) API.
- **statsmodels** and **scikit-learn**: regression, scorecards, model validation -
  the modelling side.
- **Scheduling**: a script with a report-date argument can run every month by itself
  (Windows Task Scheduler, cron on Linux).

## Read more

- pandas: [Reshaping and pivot tables](https://pandas.pydata.org/docs/user_guide/reshaping.html),
  [Time series / date functionality](https://pandas.pydata.org/docs/user_guide/timeseries.html),
  [Windowing operations](https://pandas.pydata.org/docs/user_guide/window.html),
  [Chart visualization](https://pandas.pydata.org/docs/user_guide/visualization.html),
  [`ExcelWriter`](https://pandas.pydata.org/docs/reference/api/pandas.ExcelWriter.html)
- openpyxl: [Styling cells](https://openpyxl.readthedocs.io/en/stable/styles.html),
  [Charts](https://openpyxl.readthedocs.io/en/stable/charts/introduction.html)
- matplotlib: [Quick start guide](https://matplotlib.org/stable/users/explain/quick_start.html)

**This was the last session.** The [final project](../project) is the next step: one
report of your own work, in Python, from the data to the Excel file.
