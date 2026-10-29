---
title: "15. pandas: selection, aggregation, joins"
---

# 15. pandas: selection, aggregation, joins

<div class="lecture-meta">
  <span>Session 15</span><span>practice: <code>15-pandas-select-aggregate-join/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- select rows and columns with masks, `loc`, `iloc` and `query` - the `WHERE` of
  pandas;
- add new columns: formulas, `CASE WHEN` with `np.select`, bands with `pd.cut`, codes
  with `map`;
- sort and take the top N;
- group and aggregate with `groupby` and `agg` - `GROUP BY` and `PROC MEANS`;
- join tables with `merge` and stack them with `concat` - `JOIN`, `MERGE` and `SET`;
- handle missing values in all of these.

From SQL to pandas - one query, two ways:

```sql
SELECT c.segment, l.stage,
       COUNT(*)           AS loans,
       SUM(l.outstanding) AS outstanding
FROM loans l
JOIN clients c ON c.client_id = l.client_id
WHERE l.currency = 'EUR'
GROUP BY c.segment, l.stage
HAVING SUM(l.outstanding) > 1000000
ORDER BY outstanding DESC;
```

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")

result = (
    loans[loans["currency"] == "EUR"]                         # WHERE
    .merge(clients, on="client_id")                           # JOIN
    .groupby(["segment", "stage"], as_index=False)            # GROUP BY
    .agg(loans=("loan_id", "count"), outstanding=("outstanding", "sum"))
)
result = result[result["outstanding"] > 1_000_000]            # HAVING
result.sort_values("outstanding", ascending=False)            # ORDER BY
```

Every clause has its own tool, and the tools can be chained. Today we take them one by
one.

## 1. Selecting rows and columns

### Columns: `KEEP` and `DROP`

You know `df["col"]` (a Series) and `df[["a", "b"]]` (a DataFrame) from session 14.
`drop` removes columns - SAS `DROP=`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(loans[["loan_id", "product", "outstanding"]].head(3))      # KEEP=
print(loans.drop(columns=["amount", "maturity_date"]).columns.tolist())   # DROP=
```

Columns by their type, and new names - `RENAME=`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(loans.select_dtypes("number").columns.tolist())            # all number columns
short = loans.rename(columns={"outstanding": "balance", "days_past_due": "dpd"})
print(short.columns.tolist())
```

### Rows: a mask is the `WHERE`

A comparison on a column gives a Series of `True` / `False` (a mask, as in NumPy). The
mask in square brackets keeps the rows where it is `True`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
late = loans["days_past_due"] > 90                  # a mask: one True / False per row
print(late.sum(), "loans more than 90 days past due")
loans[late][["loan_id", "product", "outstanding", "days_past_due"]].head()
```

Several conditions: `&` (and), `|` (or), `~` (not), each comparison in brackets -
the rule of session 14:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
mask = (loans["currency"] == "EUR") & (loans["stage"] >= 2) & ~(loans["product"] == "overdraft")
print(mask.sum(), "rows")
print(loans.loc[mask, "outstanding"].sum().round(2))
```

`IN (...)`, `BETWEEN` and `LIKE 'abc%'` have their own methods:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(loans["product"].isin(["mortgage", "investment"]).sum())          # IN (...)
print(loans["interest_rate"].between(5, 6).sum())                      # BETWEEN 5 AND 6 (both ends included)
print(loans["client_id"].str.startswith("C00").sum())                  # LIKE 'C00%'
print((~loans["currency"].isin(["EUR"])).sum())                        # NOT IN
```

::: info Compare with session 5
`[row for row in loans if row["days_past_due"] > 90]` was the `WHERE` with a list.
The mask does the same for a whole column at once, and keeps the table a table.
:::

### `loc`: rows and columns by label

`loc[rows, columns]` selects both at once. The rows can be a mask, the columns a list:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.loc[loans["stage"] == 3, ["loan_id", "client_id", "outstanding"]].head()
```

With an index of ids (session 14), `loc` takes the labels - like a lookup in a
dictionary:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv").set_index("loan_id")
print(loans.loc["L000002"])                                   # one row: a Series
print(loans.loc["L000002", "outstanding"])                    # one value
print(loans.loc[["L000001", "L000003"], ["product", "outstanding"]])
print(loans.loc["L000001":"L000004", "stage"])                # a range of labels: BOTH ends included
```

### `iloc`: by position

`iloc` counts positions from 0, like a list - the end is **not** included:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(loans.iloc[0])                    # the first row
print(loans.iloc[:3, :4])               # rows 0 - 2, columns 0 - 3 (FIRSTOBS / OBS)
print(loans.iloc[-1]["loan_id"])        # the last row
```

::: warning `loc` includes the end, `iloc` does not
`loc["L000001":"L000004"]` has 4 rows (labels, both ends); `iloc[0:4]` has 4 rows too
(positions 0, 1, 2, 3). Use `loc` with names and masks, `iloc` only when the position
itself matters (the first row, the last 5).
:::

### `query`: the `WHERE` as text

`query` takes the condition as a string - shorter, and close to SQL. `@name` uses a
Python variable (like `&macro_var` in SAS):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(len(loans.query("stage == 3 and currency == 'EUR'")))
limit = 1_000_000
loans.query("outstanding > @limit and product in ['investment', 'project_finance']")[["loan_id", "product", "outstanding"]].head()
```

`and`, `or`, `not` and `in` are allowed inside `query`. Column names with spaces go
in backticks: `` query("`Days past due` > 90") ``.

### Change a filtered table: make a copy

A filtered DataFrame is a new table. If you want to change it, say so with `.copy()`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
late = loans[loans["days_past_due"] > 30].copy()     # a separate table
late["flag"] = "late"
print(late[["loan_id", "flag"]].head(3))
print("flag" in loans.columns)                       # the original did not change
```

Without `.copy()`, pandas 2.2 shows a `SettingWithCopyWarning` (it cannot know if you
wanted to change `loans` too). pandas 3 has **copy-on-write**: a filtered table always
behaves as a copy, and the warning is gone - `.copy()` is still clear, and works in
both.

To change rows **of the original**, use one `loc` with the mask and the column:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["watch"] = "no"
loans.loc[loans["days_past_due"] > 30, "watch"] = "yes"     # UPDATE loans SET watch = 'yes' WHERE ...
print(loans["watch"].value_counts())
```

::: danger Two brackets in a row do not change the table
`loans[loans["days_past_due"] > 90]["stage"] = 3` changes a temporary copy and is
lost (pandas 3 warns with `ChainedAssignmentError`). Always one `loc[mask, column]`.
:::

::: tip Try it
Select the USD and GBP loans of stage 2 or 3 with a mask, then with `query`. Do you
get the same number of rows? What is their total outstanding?
:::

## 2. New columns

### From other columns

A formula on columns works on all rows - the derived column of a DATA step:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["repaid"] = loans["amount"] - loans["outstanding"]
loans["repaid_pct"] = (loans["repaid"] / loans["amount"] * 100).round(1)
loans["yearly_interest"] = loans["outstanding"] * loans["interest_rate"] / 100
loans[["loan_id", "amount", "outstanding", "repaid_pct", "yearly_interest"]].head(3)
```

`assign` does the same, but returns a new DataFrame - handy in a chain (and the
original stays as it was):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
small = loans[["loan_id", "amount", "outstanding"]].assign(
    repaid=lambda d: d["amount"] - d["outstanding"],
    in_thousands=lambda d: (d["outstanding"] / 1000).round(1),
)
print(small.head(3))
print(loans.columns.size, small.columns.size)
```

`lambda d:` gets the DataFrame at that step of the chain (session 4: a small
function without a name).

### `CASE WHEN`: `np.where` and `np.select`

The tools of session 14 work on columns too:

```python run
import numpy as np
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["is_default"] = np.where(loans["days_past_due"] > 90, 1, 0)
loans["size"] = np.select(
    [loans["outstanding"] >= 1_000_000, loans["outstanding"] >= 100_000],
    ["large", "medium"],
    default="small",
)
print(loans["is_default"].sum())
loans["size"].value_counts()
```

### Bands: `pd.cut`

`pd.cut` puts numbers into intervals - the DPD buckets of homework 2, or a format
with ranges (`PROC FORMAT; VALUE dpd 0='current' 1-30='1-30' ...`):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["dpd_bucket"] = pd.cut(
    loans["days_past_due"],
    bins=[-1, 0, 30, 60, 90, float("inf")],
    labels=["current", "1-30", "31-60", "61-90", "90+"],
)
print(loans[["days_past_due", "dpd_bucket"]].head())
loans["dpd_bucket"].value_counts(sort=False)
```

The empty band `61-90` is still listed (with 0): the labels are fixed in advance, like
the values of a format.

The bins are `(a, b]`: open on the left, closed on the right - `(0, 30]` is 1 - 30.
That is why the first edge is `-1`: `(-1, 0]` holds the 0. `right=False` turns them
into `[a, b)`:

```python run
import pandas as pd

amounts = pd.Series([0, 50_000, 99_999.99, 100_000, 2_500_000])
print(pd.cut(amounts, bins=[0, 100_000, 1_000_000, float("inf")], right=False,
             labels=["< 100k", "100k - 1m", "1m +"]))
```

The result is a **category** column (session 14): the labels keep their order (not
alphabetical), which is right for a report.

### Codes and descriptions: `map`

`map` with a dictionary replaces each value by its description - `PUT(code, $fmt.)`
with a format, or the dictionary lookup of session 6:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
product_group = {"mortgage": "secured", "investment": "secured", "project_finance": "secured",
                 "consumer": "unsecured", "credit_card": "unsecured", "overdraft": "unsecured"}
loans["group"] = loans["product"].map(product_group)
print(loans["group"].value_counts(dropna=False))     # working_capital is not in the dict: NaN
```

A value that is not a key gives `NaN` - check for it, like the "unknown code" of a
nomenclature (session 12). The lookup can come from a table: a Series with the codes
as its index:

```python run
import pandas as pd

clients = pd.read_csv("data/clients.csv")
scale = pd.read_csv("data/rating_scale.csv")
grade_of = scale.set_index("rating")["grade"]          # rating -> grade
clients["grade"] = clients["rating"].map(grade_of)
clients[["client_id", "rating", "grade"]].head()
```

### Text and dates in a column

The `.str` methods of session 7 and the `.dt` date parts work on a whole column:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv", parse_dates=["start_date", "maturity_date"])
loans["product_name"] = loans["product"].str.replace("_", " ").str.title()
loans["start_year"] = loans["start_date"].dt.year
loans["years"] = ((loans["maturity_date"] - loans["start_date"]).dt.days / 365.25).round(1)
loans[["product_name", "start_year", "years"]].head()
```

### `apply`: the last resort

`apply(func, axis=1)` calls a Python function for every row - easy to write, but it
is a hidden loop:

```python run
import time
import numpy as np
import pandas as pd

loans = pd.read_csv("data/loans.csv")
big = pd.concat([loans] * 100, ignore_index=True)        # 40,000 rows

start = time.perf_counter()
slow = big.apply(lambda row: "late" if row["days_past_due"] > 30 else "ok", axis=1)
middle = time.perf_counter()
fast = np.where(big["days_past_due"] > 30, "late", "ok")
end = time.perf_counter()

print(f"apply: {middle - start:.3f} s, np.where: {end - middle:.4f} s")
print((slow == fast).all())
```

Look for a column operation first (`np.where`, `np.select`, `pd.cut`, `map`, `.str`,
`.dt`); `apply` only when the rule really needs Python code per row.

::: tip Try it
Add a column `pd_band` to `clients.csv` with `pd.cut` on the rating: 1 - 3 "low",
4 - 6 "medium", 7 - 9 "high", 10 "default". How many clients are in each band?
:::

## 3. Sorting and the top N

`sort_values` with several columns and directions - `ORDER BY a, b DESC`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
ordered = loans.sort_values(["stage", "outstanding"], ascending=[False, False])
ordered[["loan_id", "stage", "outstanding"]].head()
```

The top N without sorting everything: `nlargest` / `nsmallest`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.nlargest(5, "outstanding")[["loan_id", "client_id", "product", "outstanding"]]
```

`rank` gives the place of every row - `PROC RANK`, or `RANK() OVER (ORDER BY ...)`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["size_rank"] = loans["outstanding"].rank(ascending=False, method="min").astype(int)
loans.sort_values("size_rank")[["loan_id", "outstanding", "size_rank"]].head(3)
```

After a sort, the index keeps the old row numbers. `reset_index(drop=True)` numbers
the rows again from 0 - do it when the old numbers mean nothing.

Missing values go **last** in pandas (SAS sorts its `.` first) - `na_position` changes
it:

```python run
import pandas as pd

export = pd.read_csv("data/loans_export.csv", sep=";", decimal=",", encoding="utf-8-sig", na_values=["."])
print(export.sort_values("Outstanding")[["Loan ID", "Outstanding"]].tail(3))
print(export.sort_values("Outstanding", na_position="first")[["Loan ID", "Outstanding"]].head(3))
```

::: details Check yourself: what is the difference between `sort_values("outstanding").head(5)` and `nlargest(5, "outstanding")`?
`sort_values` sorts ascending by default, so `.head(5)` gives the 5 **smallest**.
`nlargest(5, ...)` gives the 5 largest, largest first - the same as
`sort_values("outstanding", ascending=False).head(5)`.
:::

## 4. `groupby`: GROUP BY and PROC MEANS

### One key, one value

`groupby` splits the table into groups, applies a function to each, and combines the
results - split, apply, combine:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.groupby("stage")["outstanding"].sum()
```

The stage totals of session 6 (`110184825.28`, `16884527.04`, `4301356.28`) - in one
line. The result is a Series with the groups as its index. Compare with session 6:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")

totals = {}                                   # session 6: GROUP BY by hand
for stage, amount in zip(loans["stage"], loans["outstanding"]):
    totals[stage] = totals.get(stage, 0) + amount

by_pandas = loans.groupby("stage")["outstanding"].sum()
print({k: round(v, 2) for k, v in sorted(totals.items())})
print(by_pandas.round(2).to_dict())
```

### Several statistics: `agg`

A list of functions - `PROC MEANS N SUM MEAN MAX`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.groupby("product")["outstanding"].agg(["count", "sum", "mean", "max"]).round(2)
```

**Named aggregation** gives every result column its name - `COUNT(*) AS loans`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.groupby("product").agg(
    loans=("loan_id", "count"),
    outstanding=("outstanding", "sum"),
    avg_rate=("interest_rate", "mean"),
    max_dpd=("days_past_due", "max"),
).round(2).sort_values("outstanding", ascending=False)
```

Each item is `new_name=(column, function)`. This is the form to use in reports.

The full `PROC MEANS` output for every group - `describe` after `groupby`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans.groupby("stage")["interest_rate"].describe().round(2)
```

### Several keys

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
by_two = loans.groupby(["currency", "stage"])["outstanding"].sum().round(2)
print(by_two)
print(by_two.loc[("EUR", 3)])                 # a value by its two keys
```

The index has two levels now (a `MultiIndex`). For a flat table - columns as in SQL -
use `as_index=False` or `reset_index()`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
flat = loans.groupby(["currency", "stage"], as_index=False)["outstanding"].sum()
print(flat.head())
print(loans.groupby(["currency", "stage"])["outstanding"].sum().reset_index().equals(flat))
```

The share of each stage **in its segment** - a group total of a group result
(`transform`, below, explains the second line):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")
table = (loans.merge(clients[["client_id", "segment"]], on="client_id")
              .groupby(["segment", "stage"], as_index=False)["outstanding"].sum())
table["share_in_segment"] = (table["outstanding"] / table.groupby("segment")["outstanding"].transform("sum")).round(4)
table
```

(The same table with the stages as columns is a **pivot** - session 16.)

### `size` and `count`

`size()` counts the rows of each group (`COUNT(*)`); `count()` counts the values that
are not missing (`COUNT(col)`):

```python run
import pandas as pd

clients = pd.read_csv("data/clients.csv")
print(clients.groupby("segment").size())
print(clients.groupby("segment")["industry"].count())     # retail clients have no industry
```

### `HAVING`: filter after the grouping

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
per_client = loans.groupby("client_id").agg(loans=("loan_id", "count"),
                                             outstanding=("outstanding", "sum"))
print(per_client[per_client["loans"] >= 6])                         # HAVING COUNT(*) >= 6
print(per_client.query("outstanding > 5_000_000").round(2))         # HAVING SUM(...) > 5m
```

### `PROC FREQ` with two variables

`value_counts` on several columns counts the combinations:

```python run
import pandas as pd

clients = pd.read_csv("data/clients.csv")
print(clients.value_counts(["segment", "region"]).head(6))
print(clients.groupby("segment")["region"].value_counts(normalize=True).round(3).head(7))
```

(`pd.crosstab` - the two-way table with rows and columns - is session 16.)

### The share inside a group: `transform`

The share of each loan in its client's total needs the group total **on every row**.
In SQL that is a window function: `SUM(outstanding) OVER (PARTITION BY client_id)`.
In pandas, `transform`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["client_total"] = loans.groupby("client_id")["outstanding"].transform("sum")
loans["share_of_client"] = (loans["outstanding"] / loans["client_total"]).round(4)
loans.loc[loans["client_id"] == "C0080", ["loan_id", "outstanding", "client_total", "share_of_client"]]
```

`agg` gives one row per group; `transform` gives one value per **row** (the group
result repeated) - so it fits as a new column. Other window functions in the same
way:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["loans_of_client"] = loans.groupby("client_id")["loan_id"].transform("count")
loans["rank_in_client"] = loans.groupby("client_id")["outstanding"].rank(ascending=False).astype(int)
loans.sort_values(["client_id", "rank_in_client"])[["client_id", "loan_id", "outstanding",
                                                    "loans_of_client", "rank_in_client"]].head(6)
```

### Groups from bands

Group by a column made with `pd.cut`. For category columns, `observed=True` shows
only the bands that have rows (the default in pandas 3; pandas 2.2 warns if you do not
say it):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["dpd_bucket"] = pd.cut(loans["days_past_due"], bins=[-1, 0, 30, 90, float("inf")],
                             labels=["current", "1-30", "31-90", "90+"])
loans.groupby("dpd_bucket", observed=True).agg(loans=("loan_id", "count"),
                                               outstanding=("outstanding", "sum")).round(2)
```

::: info `groupby` and SAS
`PROC MEANS DATA=loans; CLASS segment stage; VAR outstanding; OUTPUT OUT=...` is
`groupby(["segment", "stage"]).agg(...)`. There is no need to sort first (`BY`
needs `PROC SORT`; `groupby` does not), and the groups come out sorted by the keys.
:::

::: tip Try it
By `currency`: the number of loans, the total and the mean outstanding, the
maximum days past due - with named aggregation. Then keep only the currencies with
more than 20 loans.
:::

## 5. `merge` and `concat`: JOIN and SET

### The kinds of join

A small example first - two tables, one key:

```python run
import pandas as pd

left = pd.DataFrame({"client_id": ["C1", "C2", "C3"], "segment": ["retail", "sme", "retail"]})
right = pd.DataFrame({"client_id": ["C2", "C3", "C4"], "rating": [5, 3, 7]})

print(left.merge(right, on="client_id"))                  # INNER JOIN (the default)
print(left.merge(right, on="client_id", how="left"))      # LEFT JOIN: all of left, NaN where no match
print(left.merge(right, on="client_id", how="outer"))     # FULL OUTER JOIN
```

`how="right"` exists too. The rows without a partner get `NaN` - and an int column
with `NaN` becomes float (session 14: `5.0`, `3.0`).

### `IN=` of SAS: `indicator=True`

The DATA step `MERGE a(in=a) b(in=b); BY id;` tells where each row came from.
`indicator=True` adds the column `_merge` with `both`, `left_only`, `right_only`:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")

check = clients.merge(loans[["client_id", "loan_id"]], on="client_id", how="left", indicator=True)
print(check["_merge"].value_counts())
no_loans = check.loc[check["_merge"] == "left_only", "client_id"]
print(no_loans.tolist())                                  # IF a AND NOT b
```

The 7 clients without loans - the anti-join (`WHERE l.client_id IS NULL`). Simpler,
when you need only the ids: `~clients["client_id"].isin(loans["client_id"])`.

### The portfolio join and the EL

Loans + clients + the rating scale - the join of homework 4 (session 4, with loops;
session 6, with dicts; session 13, in SQL). Now in pandas:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")
scale = pd.read_csv("data/rating_scale.csv")

full = (loans
        .merge(clients[["client_id", "segment", "region", "rating"]], on="client_id", how="left")
        .merge(scale[["rating", "grade", "pd_min", "pd_max"]], on="rating", how="left"))
full["pd"] = (full["pd_min"] + full["pd_max"]) / 2
full["el"] = full["pd"] * 0.45 * full["outstanding"]

print(full.shape)
print(round(full["el"].sum(), 2))                          # 1140106.56 - the fifth time
full.groupby("segment")["el"].sum().round(2)
```

The same number as with loops, dicts and SQL: the tools agree.

### Different key names, the same column names

`left_on` / `right_on` when the key has another name; `suffixes` when both tables have
a column with the same name. The rating of each client in August and September from
`ratings_history.csv` (a self join, as in session 13):

```python run
import pandas as pd

history = pd.read_csv("data/ratings_history.csv")
aug = history[history["month_end"] == "2026-08-31"]
sep = history[history["month_end"] == "2026-09-30"]

both = aug.merge(sep, on="client_id", suffixes=("_aug", "_sep"))
print(both.columns.tolist())
worse = both[both["rating_sep"] > both["rating_aug"]]
print(len(worse), "clients got a worse rating")
worse.head()
```

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
codes = pd.DataFrame({"code": ["EUR", "USD", "GBP"], "currency_name": ["euro", "US dollar", "pound sterling"]})
loans.merge(codes, left_on="currency", right_on="code", how="left")[["loan_id", "currency", "currency_name"]].head(3)
```

A key of **two** columns - `on=[...]`, like `BY loan_id month_end` or `ON a.x = b.x AND
a.y = b.y`. The monthly balance of each loan with the rating of its client in the same
month:

```python run
import pandas as pd

balances = pd.read_csv("data/balances_monthly.csv")
history = pd.read_csv("data/ratings_history.csv")
owner = pd.read_csv("data/loans.csv")[["loan_id", "client_id"]]

monthly = (balances.merge(owner, on="loan_id", validate="many_to_one")
                   .merge(history, on=["client_id", "month_end"], how="left", validate="many_to_one"))
print(monthly.shape, monthly["rating"].isna().sum(), "without a rating")
monthly[monthly["loan_id"] == "L000002"].tail(3)
```

### The trap: a duplicated key

If the key is not unique on the "one" side, every match is a row: the table grows and
the totals double - the many-to-many join. `validate` stops it with an error:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")
clients_twice = pd.concat([clients, clients.head(3)])          # 3 clients appear twice

joined = loans.merge(clients_twice, on="client_id")
print(len(loans), "->", len(joined), "rows")
print(round(loans["outstanding"].sum(), 2), "->", round(joined["outstanding"].sum(), 2))

try:
    loans.merge(clients_twice, on="client_id", validate="many_to_one")
except Exception as error:
    print(type(error).__name__, ":", error)
```

Rule: on a lookup join, write `validate="many_to_one"` (or check
`key.is_unique` first), and compare the row count before and after.

### `concat`: one table under another

`pd.concat` puts tables under each other - SAS `SET a b;`, SQL `UNION ALL`. The
columns are matched by name:

```python run
import pandas as pd

history = pd.read_csv("data/ratings_history.csv")
q3 = [history[history["month_end"] == m] for m in ["2026-07-31", "2026-08-31", "2026-09-30"]]
together = pd.concat(q3, ignore_index=True)
print(together.shape)
print(together["month_end"].value_counts().sort_index())
```

`keys=` labels where each part came from (like `INDSNAME=` in SAS), and a missing
column is filled with `NaN`:

```python run
import pandas as pd

old = pd.DataFrame({"loan_id": ["L1", "L2"], "outstanding": [100.0, 200.0]})
new = pd.DataFrame({"loan_id": ["L3"], "outstanding": [50.0], "stage": [2]})
print(pd.concat([old, new], keys=["old_system", "new_system"]))
```

(`UNION` without `ALL` = `concat` + `drop_duplicates()`.)

::: tip Try it
Join `loans.csv` with `client_register.csv` on `client_id` with `how="left"` and
`indicator=True`. Do all loans find their client? (Look at the ids in the register -
session 7.) How would you fix the key before the join?
:::

## 6. Missing values

### `NaN`, `None`, `pd.NA`

pandas marks a missing value with `NaN` in number columns, and with `NaN` or `None`
in text columns (pandas 3: `NaN` in the `str` type). Nullable types (`Int64`,
session 14) use `pd.NA`. Do not compare with them - use `isna()` / `notna()`:

```python run
import pandas as pd
import numpy as np

s = pd.Series([1.5, np.nan, None, 4.0])
print(s)
print(s.isna().tolist(), s.notna().sum())
print(s == np.nan)                         # all False: NaN is not equal to anything
```

### Aggregates skip them

Unlike NumPy (session 14), pandas skips `NaN` in `sum`, `mean`, `min`, `max` - like
SQL and `PROC MEANS`:

```python run
import pandas as pd

export = pd.read_csv("data/loans_export.csv", sep=";", decimal=",", encoding="utf-8-sig", na_values=["."])
amounts = export["Outstanding"]
print(len(amounts), amounts.count(), amounts.isna().sum())     # N, N without missing, NMISS
print(round(amounts.sum(), 2), round(amounts.mean(), 2))
print(round(amounts.sum(skipna=False), 2))                     # NaN: what NumPy would give
```

::: warning A mean that skips is a different mean
`mean()` divides by the values that are there (398 here), not by all rows. If a
missing amount means 0, fill it first - that changes the mean. Decide what a missing
value means before you aggregate.
:::

### Fill: `fillna`

With one value, with a value per column, or from another column - SQL `COALESCE`:

```python run
import pandas as pd

export = pd.read_csv("data/loans_export.csv", sep=";", decimal=",", encoding="utf-8-sig", na_values=["."])
print(export["Product"].fillna("unknown").value_counts().tail(3))

filled = export.fillna({"Product": "unknown", "Interest rate %": 0.0})
print(filled[["Product", "Interest rate %"]].isna().sum().to_dict())
```

```python run
import pandas as pd

df = pd.DataFrame({"loan_id": ["L1", "L2", "L3"],
                   "rate_new": [5.1, None, None],
                   "rate_old": [4.9, 6.2, None]})
df["rate"] = df["rate_new"].fillna(df["rate_old"]).fillna(0.0)    # COALESCE(rate_new, rate_old, 0)
df
```

### Drop: `dropna`

```python run
import pandas as pd

export = pd.read_csv("data/loans_export.csv", sep=";", decimal=",", encoding="utf-8-sig", na_values=["."])
print(len(export), len(export.dropna()), len(export.dropna(subset=["Outstanding"])))
```

`dropna()` without `subset` drops a row with **any** missing value - often too much.
Name the columns that matter.

How complete is each column? `isna().mean()` is the share of missing values - the
first table of a data quality report:

```python run
import pandas as pd

register = pd.read_csv("data/client_register.csv", dtype={"eik": str})
quality = pd.DataFrame({"missing": register.isna().sum(), "share": register.isna().mean().round(3)})
quality.sort_values("missing", ascending=False)
```

### NaN in comparisons, groups and joins

```python run
import pandas as pd

export = pd.read_csv("data/loans_export.csv", sep=";", decimal=",", encoding="utf-8-sig", na_values=["."])
not_card = export["Product"] != "credit_card"
print(not_card.sum(), "rows are not credit_card - including the 3 without a product")
print(export.groupby("Product")["Outstanding"].size().sum(), "rows in the groups (NaN dropped)")
print(export.groupby("Product", dropna=False)["Outstanding"].size().tail(2))
```

`!=` is `True` for `NaN` (SQL would give `NULL`, and drop the row); `groupby` drops
the `NaN` key unless `dropna=False`. In `merge`, `NaN` keys **match each other** -
unlike SQL, where `NULL = NULL` is not true:

```python run
import pandas as pd

a = pd.DataFrame({"key": ["K1", None], "x": [1, 2]})
b = pd.DataFrame({"key": ["K1", None], "y": [10, 20]})
print(a.merge(b, on="key"))            # the None rows are joined - drop them first if not wanted
```

### Repair the export from a trusted source

The 8 missing amounts of the export are in `loans.csv`. A left join brings the
reference value next to each row, `fillna` takes it where the export has none:

```python run
import pandas as pd

export = pd.read_csv("data/loans_export.csv", sep=";", decimal=",", encoding="utf-8-sig", na_values=["."])
export = export.drop_duplicates()
reference = pd.read_csv("data/loans.csv")[["loan_id", "outstanding"]]

repaired = export.merge(reference, left_on="Loan ID", right_on="loan_id", how="left", validate="one_to_one")
repaired["Outstanding"] = repaired["Outstanding"].fillna(repaired["outstanding"])
print(repaired["Outstanding"].isna().sum(), "missing now")
print(round(repaired["Outstanding"].sum(), 2), round(reference["outstanding"].sum(), 2))
```

The totals agree: 131,370,708.60.

::: tip Try it
How many rows of the export have **some** missing value? Fill the missing interest
rates with the mean rate of the same product (hint:
`groupby("Product")["Interest rate %"].transform("mean")`).
:::

## 7. The final project

The [final project](../project) is a monthly portfolio report from end to end: load
(files and the database), validate (the nomenclatures of session 12), clean,
aggregate, report (Excel and a chart - session 16), and keep it in Git. Read the brief
today; session 16 adds the last tools (pivot tables, dates, Excel output) and the time
to start.

## 8. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root (with the virtual environment active):

```bash
python 15-pandas-select-aggregate-join/practice/task1-select.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-select.py` | Rows and columns: masks, `loc`, `iloc`, `isin`, `between`, `query` |
| 2 | `task2-predict-pandas.py` | Predict: masks, groups, joins, missing values |
| 3 | `task3-new-columns.py` | New columns with `np.select`, `pd.cut`, `map` and `assign` |
| 4 | `task4-groupby.py` | Totals by group, named aggregation, `HAVING`, shares with `transform` |
| 5 | `task5-merge.py` | Joins with clients and the rating scale, the anti-join, the EL |
| 6 | `task6-missing.py` (Optional) | Missing values in the export: count, fill, drop, repair |

## Summary

| SQL / SAS | pandas |
|-----------|--------|
| `SELECT a, b` / `KEEP=` | `df[["a", "b"]]`; `df.drop(columns=[...])` |
| `WHERE` | `df[mask]`, `df.loc[mask, cols]`, `df.query("...")`; `&`, `\|`, `~` with brackets |
| `IN`, `BETWEEN`, `LIKE 'x%'` | `isin`, `between`, `.str.startswith` |
| `UPDATE ... SET ... WHERE` | `df.loc[mask, "col"] = value` (one `loc`, never two brackets) |
| derived column, `CASE WHEN` | `df["new"] = ...`, `assign`, `np.where`, `np.select` |
| `PROC FORMAT` ranges / values | `pd.cut(bins, labels)`; `map(dict)` |
| `ORDER BY`, top N, `RANK` | `sort_values`, `nlargest`, `rank` |
| `GROUP BY`, `PROC MEANS CLASS` | `groupby(keys).agg(name=(col, func))`; `as_index=False` |
| `COUNT(*)` / `COUNT(col)` | `size()` / `count()` |
| `HAVING` | a mask on the grouped result |
| `SUM() OVER (PARTITION BY)` | `groupby(...)[col].transform("sum")` |
| `JOIN`, `MERGE BY` + `IN=` | `merge(on, how)`, `indicator=True`; `validate="many_to_one"` |
| `SET a b`, `UNION ALL` | `pd.concat([a, b])` |
| `NULL`, `.`, `COALESCE`, `NMISS` | `NaN`; `isna`; aggregates skip it; `fillna`, `dropna(subset=...)` |

## Homework

1. `15-pandas-select-aggregate-join/homework.py` (in the homework repository): **the
   portfolio report in pandas** - one function per table: exposure and EL by segment
   and stage, the top 10 clients with their region and grade, the concentration of
   the top 10, the clients without loans, the loans of defaulted clients. The checks
   compare with the numbers of sessions 4, 6 and 13. Every check must print `OK`.
2. The practice tasks you did not finish in class.
3. Read the [final project](../project) brief and choose your report date and the
   tables you want in your report.

## Self-study

This part is not covered in class. It is for reading at home: how to write in pandas
the SAS DATA step tricks you use every day, and how to write a long transformation as
one readable chain.

### SAS idioms in pandas

**`FIRST.` and `LAST.`** - the first or last row of each `BY` group. Sort, then keep
the first row per key:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
# proc sort; by client_id descending outstanding; data first; set; by client_id; if first.client_id;
largest = (loans.sort_values(["client_id", "outstanding"], ascending=[True, False])
                .drop_duplicates("client_id", keep="first"))
print(len(largest), "clients")
largest[["client_id", "loan_id", "outstanding"]].head()
```

`groupby("client_id").head(1)` does the same, and `.head(2)` keeps the first two of each
group - not possible with `FIRST.` alone. `keep="last"` is `LAST.`.

**`NODUPKEY`** - `drop_duplicates(subset=[...])` (session 14); `duplicated(keep=False)`
marks **all** copies, to look at them:

```python run
import pandas as pd

export = pd.read_csv("data/loans_export.csv", sep=";", decimal=",", encoding="utf-8-sig", na_values=["."])
copies = export[export.duplicated("Loan ID", keep=False)]
print(len(copies), "rows belong to duplicated ids")
copies.sort_values("Loan ID").head(4)[["Loan ID", "Product", "Outstanding"]]
```

**`LAG` and `RETAIN` by group** - the value of the previous row of the same client,
and a running total that restarts for each client:

```python run
import pandas as pd

history = pd.read_csv("data/ratings_history.csv").sort_values(["client_id", "month_end"])
history["prev_rating"] = history.groupby("client_id")["rating"].shift(1)       # LAG within BY group
history["change"] = history["rating"] - history["prev_rating"]
history["downgrades"] = (history["change"] > 0).astype(int)
history["downgrades_so_far"] = history.groupby("client_id")["downgrades"].cumsum()   # RETAIN + sum
history.loc[history["client_id"] == "C0002", ["month_end", "rating", "prev_rating", "change", "downgrades_so_far"]]
```

`shift(1)` inside the group gives `NaN` on the first row of each client - exactly
what `LAG` with `IF FIRST.client_id THEN prev = .` does, without the trap of `LAG`
in a condition.

**A row counter per group** - `cumcount` (`IF FIRST. THEN n = 0; n + 1;`):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv").sort_values(["client_id", "start_date"])
loans["loan_no"] = loans.groupby("client_id").cumcount() + 1
loans[["client_id", "loan_id", "start_date", "loan_no"]].head(6)
```

**Exercises**

1. For every client, the month (`month_end`) of the worst rating of the last 12 months
   (the highest number). If there are several, take the last one.
2. For every client, the number of months in which the rating changed (up or down).
   Which client changed the most?

::: details Answer
```python
import pandas as pd

history = pd.read_csv("data/ratings_history.csv")

# 1. sort so that the wanted row is LAST in each group, then keep="last"
worst = (history.sort_values(["client_id", "rating", "month_end"])
                .drop_duplicates("client_id", keep="last"))
print(worst.head())

# 2. LAG by group, then count the changes
history = history.sort_values(["client_id", "month_end"])
history["changed"] = history.groupby("client_id")["rating"].diff().fillna(0) != 0
changes = history.groupby("client_id")["changed"].sum()
print(changes.sort_values(ascending=False).head(3))
```
:::

### Method chaining

Many steps with temporary names (`df1`, `df2`, `df3`) are hard to read and easy to mix
up. A chain reads top to bottom, like a SQL query or a DATA step - each line one
step, in brackets so that it can span lines:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")

report = (
    loans
    .query("stage >= 2")
    .merge(clients[["client_id", "segment", "region"]], on="client_id", how="left", validate="many_to_one")
    .assign(late=lambda d: d["days_past_due"] > 30)
    .groupby(["segment", "region"], as_index=False)
    .agg(loans=("loan_id", "count"), outstanding=("outstanding", "sum"), late=("late", "sum"))
    .sort_values("outstanding", ascending=False)
    .round(2)
)
report.head(8)
```

To look inside a chain while you build it, stop it after any line and look at the
result. Do not chain 30 steps: a chain per idea (load, clean, aggregate) is easier to
test.

**Exercise**

Write one chain: the loans of stage 1 in EUR, with the client's rating (`merge`), a
column `rating_band` with `pd.cut` (1 - 3, 4 - 6, 7 - 10), and per band the number of
loans and the mean interest rate, sorted by the band.

::: details Answer
```python
import pandas as pd

loans = pd.read_csv("data/loans.csv")
clients = pd.read_csv("data/clients.csv")

(loans
 .query("stage == 1 and currency == 'EUR'")
 .merge(clients[["client_id", "rating"]], on="client_id", validate="many_to_one")
 .assign(rating_band=lambda d: pd.cut(d["rating"], bins=[0, 3, 6, 10], labels=["1-3", "4-6", "7-10"]))
 .groupby("rating_band", observed=True)
 .agg(loans=("loan_id", "count"), avg_rate=("interest_rate", "mean"))
 .round(2))
```

`groupby` on a category column sorts by the order of the labels, so no `sort_values`
is needed.
:::

## Read more

- pandas: [Indexing and selecting data](https://pandas.pydata.org/docs/user_guide/indexing.html),
  [Group by: split-apply-combine](https://pandas.pydata.org/docs/user_guide/groupby.html),
  [Merge, join, concatenate](https://pandas.pydata.org/docs/user_guide/merging.html),
  [Working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html),
  [Copy-on-write](https://pandas.pydata.org/docs/user_guide/copy_on_write.html)
- [Comparison with SAS](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sas.html)
  and [with SQL](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html)
  (the official tables)

**Next session:** pandas for reports - pivot tables (`PROC TABULATE` /
`TRANSPOSE`), `melt`, dates and month ends, a rating migration matrix, an Excel file
with several sheets, charts - and the start of the final project.
