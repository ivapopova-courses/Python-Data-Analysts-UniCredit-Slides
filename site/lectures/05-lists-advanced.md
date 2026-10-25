---
title: 5. Lists (advanced)
---

# 5. Lists (advanced)

<div class="lecture-meta">
  <span>Session 5</span><span>practice: <code>05-lists-advanced/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- build a new list from an old one in one line, with a **list comprehension** - the
  Python `SELECT expression ... WHERE condition`;
- check a whole list at once with `any` and `all`, and find extremes with `min` and
  `max`;
- sort by several columns, in mixed directions, and take the top N;
- walk over several lists together with `zip`, and number the items with
  `enumerate`;
- apply a function to every item with `map`, and keep some items with `filter`;
- keep a whole table in memory as a **list of rows**, and do `WHERE`, derived
  columns, `ORDER BY` and column totals on it;
- copy a table safely, so that a change of the copy does not change the original.

From SQL to Python - the same question, two ways. The ten largest exposures:

```sql
SELECT loan_id, product, outstanding
FROM loans
ORDER BY outstanding DESC
FETCH FIRST 10 ROWS ONLY;
```

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()                                           # skip the header
    rows = [line.strip().split(",") for line in file]         # a list of rows

loans = [(row[0], row[2], float(row[7])) for row in rows]     # SELECT loan_id, product, outstanding
top10 = sorted(loans, key=lambda loan: loan[2], reverse=True)[:10]

for rank, (loan_id, product, outstanding) in enumerate(top10, start=1):
    print(f"{rank:>2}. {loan_id}  {product:<16}{outstanding:>15,.2f}")
```

Three lines do the work: a comprehension reads the table, a second one selects the
columns, and `sorted(...)[:10]` is `ORDER BY ... FETCH FIRST 10`. By the end of today
you can write each of them.

## 1. List comprehensions

### From a loop to one line

In sessions 2 and 3 you built lists with a loop and `append`:

```python run
amounts = [1156900.0, 1977400.0, 800.0, 15900.0]

in_thousands = []
for amount in amounts:
    in_thousands.append(amount / 1000)

print(in_thousands)
```

This pattern - an empty list, a loop, one `append` - is so common that Python has a
short form for it, the **list comprehension**:

```python run
amounts = [1156900.0, 1977400.0, 800.0, 15900.0]

in_thousands = [amount / 1000 for amount in amounts]
print(in_thousands)
```

Read it from the middle: "**for** each `amount` **in** `amounts`, take `amount /
1000`". The square brackets say: collect the results in a new list.

```text
[expression  for name in iterable]
     |              |
  what to keep   where it comes from
```

It is the same as `SELECT amount / 1000 FROM amounts` in SQL, and the same as a
derived variable in a DATA step:

```sas
data in_thousands;
    set amounts;
    amount_k = amount / 1000;
run;
```

The original list does not change: a comprehension always makes a **new** list.

### Any expression

The expression can be anything that gives a value: a calculation, a method call, a
function call, a tuple.

```python run
ids = ["l000001", "l000002", "l000003"]
print([loan_id.upper() for loan_id in ids])

rates = [8.83, 5.44, 4.79]
print([round(rate / 100, 4) for rate in rates])

print([len(loan_id) for loan_id in ids])
print([(loan_id, loan_id[-3:]) for loan_id in ids])
```

With your own function from session 4:

```python run
def dpd_bucket(days_past_due):
    if days_past_due == 0:
        return "current"
    if days_past_due <= 30:
        return "1-30"
    if days_past_due <= 90:
        return "31-90"
    return "90+"

days = [0, 35, 0, 120, 15]
print([dpd_bucket(d) for d in days])
```

### Filter with `if`: the `WHERE`

Add `if condition` at the end, and only the items that pass go into the new list:

```python run
days = [0, 35, 0, 120, 15, 95, 0]

late = [d for d in days if d > 0]
very_late = [d for d in days if d > 90]
print(late)
print(very_late)
```

```text
[expression  for name in iterable  if condition]
                                     |
                                   WHERE
```

`SELECT d FROM days WHERE d > 90`. With both parts - a new value **and** a filter:

```python run
rates = [8.83, 5.44, 4.79, 8.35, 12.10]

# SELECT rate / 100 FROM rates WHERE rate > 8
print([rate / 100 for rate in rates if rate > 8])
```

### On the portfolio

Read `loans.csv` into a list of rows - one comprehension - and select from it.
Each row is a list of strings, in the order of the header:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    header = file.readline().strip().split(",")
    rows = [line.strip().split(",") for line in file]

print(header)
print(len(rows), "rows; the first one:")
print(rows[0])
```

The ids of the stage 3 loans (`stage` is column 10), and the outstanding amounts in
thousands of the USD loans:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    rows = [line.strip().split(",") for line in file]

stage3 = [row[0] for row in rows if row[10] == "3"]
print(len(stage3), stage3[:5])

usd_k = [round(float(row[7]) / 1000, 1) for row in rows if row[3] == "USD"]
print(len(usd_k), usd_k[:5])
```

The columns are still **text** - `row[10] == "3"`, not `== 3`. Convert where you need
a number (`float(row[7])`), as in session 2.

### `CASE WHEN` inside: `a if condition else b`

A conditional expression (session 2) can be the expression of a comprehension. Then
every item goes into the list, with one of two values:

```python run
days = [0, 35, 0, 120, 15]

# SELECT CASE WHEN d > 30 THEN 'late' ELSE 'ok' END
print(["late" if d > 30 else "ok" for d in days])
```

::: warning The position of `if` decides what it does
- `if` **at the end** filters: fewer items. No `else` is allowed there.
- `a if c else b` **at the start** chooses a value: the same number of items. The
  `else` is required.

```python run
days = [0, 35, 0, 120, 15]

print([d for d in days if d > 30])              # WHERE: 2 items
print([d if d > 30 else 0 for d in days])       # CASE: 5 items
```

```python run
days = [0, 35, 0, 120, 15]
print([d for d in days if d > 30 else 0])       # SyntaxError
```
:::

### Generator expressions: `sum(... for ...)`

When you only need the **total**, you do not need the list. Write the comprehension
without the square brackets, inside the call:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    rows = [line.strip().split(",") for line in file]

total = sum(float(row[7]) for row in rows)
stage3_total = sum(float(row[7]) for row in rows if row[10] == "3")
late_count = sum(1 for row in rows if int(row[9]) > 0)

print(f"{total:,.2f}  {stage3_total:,.2f}  {late_count}")
```

This is a **generator expression**: it gives the values one by one to `sum`, and
never builds a list in memory. It works with any function that takes many values:
`sum`, `min`, `max`, `any`, `all`, `sorted`, `set`, `", ".join(...)`.

`sum(1 for ... if ...)` is `COUNT(*) ... WHERE ...`. Another way to count: `True`
is `1` (session 2), so `sum(int(row[9]) > 0 for row in rows)` gives the same.

### Set comprehensions: `SELECT DISTINCT`

Curly brackets make a **set** - the unique values (session 3):

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    rows = [line.strip().split(",") for line in file]

products = {row[2] for row in rows}
print(sorted(products))

clients_with_usd = {row[1] for row in rows if row[3] == "USD"}
print(len(clients_with_usd))
```

Dictionary comprehensions, with `{key: value for ...}`, are in session 6.

### When not to use a comprehension

A comprehension is for **building a new list**. Use a normal loop when:

- you only want an effect, not a list - for example printing:
  `[print(x) for x in items]` works, but builds a useless list of `None`;
- the logic needs several steps, `try` / `except`, or several `if` / `elif`
  branches - put it into a function (session 4) and call the function in the
  comprehension, or write the loop;
- the line becomes too long to read in one look (more than about 80 characters).

```python run
def classify(rate):
    """A rate band - too many branches for one comprehension."""
    if rate < 4:
        return "low"
    if rate < 8:
        return "medium"
    if rate < 12:
        return "high"
    return "very high"

rates = [2.54, 5.44, 8.83, 13.98]
print([classify(rate) for rate in rates])       # short and clear
```

::: details Advanced: two `for` in one comprehension
Several `for` parts run like nested loops, the first one outside:

```python run
regions = ["Sofia", "Varna"]
segments = ["retail", "sme"]

# every combination, like a CROSS JOIN
print([(r, s) for r in regions for s in segments])

# a list of lists made flat
monthly = [[100, 120], [90], [130, 110, 95]]
print([x for month in monthly for x in month])
```

Read it as the loops it replaces: `for month in monthly:` then `for x in month:`.
More than two `for` parts are hard to read - write the loops.
:::

::: info The same in pandas
In pandas (session 14) you do not loop at all - an operation on a column works on
all its values:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print((loans["outstanding"] / 1000).head(3))
print(loans.loc[loans["stage"] == 3, "loan_id"].head(3).tolist())
```

The idea is the same as a comprehension: a new column from an old one, with a
filter.
:::

::: tip Try it
Predict, then press **Run**:

```python run
days = [0, 35, 0, 120, 15]
print([d // 30 for d in days])
print([d for d in days if d])
print(["yes" if d else "no" for d in days])
print(sum(d > 0 for d in days))
```

Then change the second line to keep only the values between 10 and 100.
:::

## 2. Checks and extremes: `any`, `all`, `min`, `max`

### `any` and `all`: questions about the whole list

- `any(values)` is `True` if **at least one** value is true.
- `all(values)` is `True` if **every** value is true.

With a generator expression, they ask a question about every row - the checks you
run on data before a report:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    rows = [line.strip().split(",") for line in file]

print("any loan over 90 days past due:", any(int(row[9]) > 90 for row in rows))
print("all ids start with L:          ", all(row[0].startswith("L") for row in rows))
print("all amounts positive:          ", all(float(row[6]) > 0 for row in rows))
print("any currency other than EUR/USD:", any(row[3] not in ("EUR", "USD") for row in rows))
```

In SQL these are `EXISTS (SELECT ... WHERE ...)` and `NOT EXISTS (... WHERE NOT
...)`. Both stop as soon as the answer is known: `any` at the first true value,
`all` at the first false one.

::: warning Empty lists
`any([])` is `False` - nothing is true. `all([])` is `True` - nothing is false. A
check with `all` on an empty file "passes". Check the number of rows too.

```python run
print(any([]), all([]))
```
:::

### `min` and `max` with `key`

Session 4 showed `key=` with `sorted`, `min` and `max`. With rows, `key` says which
column to compare - and you get back the **whole row**, not only the value:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    rows = [line.strip().split(",") for line in file]

largest = max(rows, key=lambda row: float(row[7]))
cheapest = min(rows, key=lambda row: float(row[8]))
print(largest[0], largest[2], largest[7])
print(cheapest[0], cheapest[2], cheapest[8])
```

Without `key`, `max(rows)` compares the rows as lists of strings - the first column
first. That is the largest **id**, not the largest loan. And `max` of the column
alone gives only the number:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    rows = [line.strip().split(",") for line in file]

print(max(rows)[0])                             # by loan_id, as text
print(max(float(row[7]) for row in rows))       # the largest amount, without the row
```

::: warning A trap: numbers as text
`max(["9", "10", "100"])` is `"9"`: strings compare letter by letter (session 2).
Convert first - `key=float` or `float(...)` in the generator.

```python run
print(max(["9", "10", "100"]))
print(max(["9", "10", "100"], key=float))
```
:::

### `default=`: when the list can be empty

`max([])` is a `ValueError`. When a filter may leave nothing, give a `default`:

```python run
days = [0, 0, 15]

print(max((d for d in days if d > 90), default=0))
print(max(d for d in days if d > 90))           # ValueError: the sequence is empty
```

### `sum`, `len` and the average

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    rows = [line.strip().split(",") for line in file]

rates = [float(row[8]) for row in rows]
print("count  ", len(rates))
print("min    ", min(rates))
print("max    ", max(rates))
print("average", round(sum(rates) / len(rates), 2))
```

This is `PROC MEANS` for one variable. The module `statistics` (session 10) adds
`median`, `stdev` and more; pandas gives all of them in one `describe()` (session 14).

::: tip Try it
Change the checks block above: is there a loan with `outstanding` greater than
`amount`? Is every `stage` one of `"1"`, `"2"`, `"3"`? Predict the answers first.
:::

## 3. Sorting, in depth

### A recap

Session 3: `list.sort()` changes the list, `sorted(x)` returns a new list. Session 4:
`key=` sorts by any expression, `reverse=True` sorts from the largest. Today: several
columns, mixed directions, and the top N.

### Several columns: a tuple as the key

A key that returns a **tuple** sorts by the first value, then by the second for equal
first values, and so on - like `ORDER BY a, b`:

```python run
loans = [
    ("L000004", "overdraft", 5875.11),
    ("L000002", "investment", 651927.30),
    ("L000003", "credit_card", 644.25),
    ("L000001", "investment", 1044231.30),
]

# ORDER BY product, outstanding
for loan in sorted(loans, key=lambda loan: (loan[1], loan[2])):
    print(loan)
```

### Mixed directions: `ORDER BY product, outstanding DESC`

`reverse=True` reverses **all** columns. For mixed directions there are two ways.

**1. Negate a number.** `-outstanding` sorts the largest first, inside an ascending
sort:

```python run
loans = [
    ("L000004", "overdraft", 5875.11),
    ("L000002", "investment", 651927.30),
    ("L000003", "credit_card", 644.25),
    ("L000001", "investment", 1044231.30),
]

for loan in sorted(loans, key=lambda loan: (loan[1], -loan[2])):
    print(loan)
```

This works only for numbers - you cannot negate a string.

**2. Two sorts.** Python's sort is **stable**: items with equal keys keep their
order. So sort by the **last** column first, then by the first one:

```python run
loans = [
    ("L000004", "overdraft", 5875.11),
    ("L000002", "investment", 651927.30),
    ("L000003", "credit_card", 644.25),
    ("L000001", "investment", 1044231.30),
]

# ORDER BY product DESC, loan_id
result = sorted(loans, key=lambda loan: loan[0])                    # the second column first
result = sorted(result, key=lambda loan: loan[1], reverse=True)     # then the first column
for loan in result:
    print(loan)
```

`PROC SORT` is stable too (with the default `EQUALS` option), so this is familiar.

### `operator.itemgetter`

For keys that only pick columns, the module `operator` has a ready function:
`itemgetter(2)` is the same as `lambda row: row[2]`, and `itemgetter(1, 2)` gives the
tuple `(row[1], row[2])`. It is a bit faster and reads like a column list:

```python run
from operator import itemgetter

loans = [
    ("L000004", "overdraft", 5875.11),
    ("L000002", "investment", 651927.30),
    ("L000003", "credit_card", 644.25),
]

print(sorted(loans, key=itemgetter(2)))
print(sorted(loans, key=itemgetter(1, 0)))
```

### The top N

`sorted(...)[:n]` - sort, then take a slice (session 3). With `enumerate` (section
4) you get the rank:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    rows = [line.strip().split(",") for line in file]

top5 = sorted(rows, key=lambda row: float(row[7]), reverse=True)[:5]
for rank, row in enumerate(top5, start=1):
    print(rank, row[0], row[1], row[7])
```

The five clients with the **most** loans - count with a comprehension, sort the
pairs:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    rows = [line.strip().split(",") for line in file]

client_ids = [row[1] for row in rows]
counts = {(c, client_ids.count(c)) for c in client_ids}       # a set of (client, count)
top = sorted(counts, key=lambda pair: (-pair[1], pair[0]))[:5]
print(top)
```

(Counting with `list.count` inside a loop reads the list again for every item - slow
for big lists. Session 6 counts with a dictionary in one pass.)

### A trap: `None` and mixed types

`sorted` compares the keys with `<`. Two values that cannot be compared - a number
and `None`, a number and a string - stop the sort with a `TypeError`:

```python run
amounts = [100.0, None, 50.0]
print(sorted(amounts))          # TypeError: '<' not supported between instances of 'NoneType' and 'float'
```

In data, a missing value is common. Decide where it goes, and say it in the key:

```python run
amounts = [100.0, None, 50.0]

# missing values last: (True/False, value) - False sorts before True
print(sorted(amounts, key=lambda x: (x is None, x if x is not None else 0)))
```

SAS sorts a missing value **first** (it is the smallest number); SQL puts `NULL`s first
or last depending on the database. In Python you choose.

::: details Advanced: `heapq.nlargest`
For the top N of a very long list, the module `heapq` does not sort the whole list:

```python run
import heapq

amounts = [5875.11, 651927.30, 644.25, 1044231.30, 15900.0]
print(heapq.nlargest(3, amounts))
print(heapq.nsmallest(2, amounts))
```

It also takes `key=`. For a few thousand rows `sorted(...)[:n]` is just as good.
:::

::: tip Try it
In the "ORDER BY product, outstanding DESC" example, sort by `product DESC,
outstanding DESC` instead. Which of the two ways do you need? (Answer: `reverse=True`
on the tuple key is enough - both columns go down.)
:::

## 4. `zip` and `enumerate`

### `zip`: several lists side by side

`zip` takes several lists and gives **tuples**: the first items together, then the
second items, and so on:

```python run
loan_ids = ["L000001", "L000002", "L000003"]
products = ["investment", "investment", "credit_card"]
amounts = [1044231.30, 651927.30, 644.25]

for loan_id, product, amount in zip(loan_ids, products, amounts):
    print(loan_id, product, amount)

print(list(zip(loan_ids, amounts)))
```

Columns become rows. A common use: two lists of the same months, compared month by
month:

```python run
months = ["Jul", "Aug", "Sep"]
outstanding_2025 = [128.4, 129.1, 130.2]       # EUR million
outstanding_2026 = [129.9, 130.8, 131.4]

for month, before, now in zip(months, outstanding_2025, outstanding_2026):
    print(f"{month}: {now - before:+.1f} million ({(now / before - 1):+.2%})")
```

And a list with itself, one step apart - the change from month to month (in SAS:
`LAG`):

```python run
outstanding = [128.4, 129.1, 130.2, 129.6, 131.4]

changes = [round(now - before, 1) for before, now in zip(outstanding, outstanding[1:])]
print(changes)
```

### `zip(*rows)`: transpose a table

With the `*` of session 4, `zip(*rows)` turns a list of rows into a list of
**columns** - a small `PROC TRANSPOSE`:

```python run
rows = [
    ("L000001", "investment", 1044231.30),
    ("L000002", "investment", 651927.30),
    ("L000003", "credit_card", 644.25),
]

ids, products, amounts = zip(*rows)
print(ids)
print(amounts)
print(sum(amounts))
```

### A trap: the shortest list wins

`zip` stops at the end of the **shortest** list - without an error. A missing value
in one list silently drops the last row:

```python run
loan_ids = ["L000001", "L000002", "L000003"]
amounts = [1044231.30, 651927.30]                  # one is missing!

print(list(zip(loan_ids, amounts)))                # L000003 is gone
```

Since Python 3.10, `strict=True` turns this into an error - use it when the lists
must have the same length:

```python run
loan_ids = ["L000001", "L000002", "L000003"]
amounts = [1044231.30, 651927.30]

print(list(zip(loan_ids, amounts, strict=True)))   # ValueError
```

### `enumerate`: the number of each item

`enumerate` (session 2) gives pairs `(number, item)`. `start=1` numbers from 1 - a
rank, or the line number of a file (the line 1 is the header):

```python run
products = ["investment", "overdraft", "mortgage"]

for i, product in enumerate(products, start=1):
    print(i, product)

print(list(enumerate(products)))
```

The line numbers of the bad rows - in SAS: `_N_`:

```python run
lines = ["L000001,800.00", "L000002,abc", "L000003,15900.00", "L000004,"]

for line_no, line in enumerate(lines, start=2):          # line 1 is the header
    amount = line.split(",")[1]
    if not amount.replace(".", "").isdigit():
        print(f"line {line_no}: bad amount {amount!r}")
```

### A trap: `zip`, `enumerate` and `map` are used up

`zip`, `enumerate`, `map` and `filter` (section 5) do not build a list. They are
**iterators**: they give the values one by one, **once**. The second time they are
empty:

```python run
pairs = zip(["a", "b"], [1, 2])

print(list(pairs))
print(list(pairs))          # [] - already used up
```

If you need the values twice, keep a list: `pairs = list(zip(...))`.

::: info The same in pandas
In a DataFrame, the columns are already side by side - no `zip` is needed. The
month-to-month change is `shift` (session 16):

```python run
import pandas as pd

s = pd.Series([128.4, 129.1, 130.2, 129.6, 131.4])
print((s - s.shift(1)).round(1).tolist())
```
:::

::: tip Try it
Predict the output, then run it:

```python run
a = [1, 2, 3, 4]
b = ["x", "y"]
z = zip(a, b)
print(list(z))
print(len(list(z)))
print(list(enumerate(b, start=10)))
```
:::

## 5. `map` and `filter`

### `map`: one function, every item

`map(function, iterable)` calls the function for every item. It is an iterator - wrap
it in `list()` to see the values:

```python run
fields = ["1156900.00", "1044231.30", "8.83"]

numbers = list(map(float, fields))
print(numbers)
```

It is most useful with a function that already exists - `float`, `int`, `str.strip`,
`str.upper`, your own:

```python run
row = " L000001 , C0080 ,investment , EUR "
print(list(map(str.strip, row.split(","))))
```

### `filter`: keep some items

`filter(function, iterable)` keeps the items for which the function returns
something true:

```python run
def is_late(days):
    return days > 30

days = [0, 35, 0, 120, 15]
print(list(filter(is_late, days)))
print(list(filter(lambda d: d > 30, days)))
```

### `map` / `filter` or a comprehension?

Both do the same job:

```python run
fields = ["1156900.00", "1044231.30", "8.83"]
days = [0, 35, 0, 120, 15]

print(list(map(float, fields)), [float(f) for f in fields])
print(list(filter(lambda d: d > 30, days)), [d for d in days if d > 30])
print(list(map(lambda d: d // 30, filter(lambda d: d > 30, days))),
      [d // 30 for d in days if d > 30])
```

Most Python programmers prefer the **comprehension**: it reads like a sentence and
needs no `lambda`. `map` is nice when the function already has a name:
`map(float, fields)`. You will meet both in other people's code.

In pandas, `map` comes back: `series.map(function)` or `series.map(dictionary)` -
the Python version of a SAS format (sessions 6 and 15).

::: details Advanced: `functools.reduce`
`reduce` combines the items into **one** value, two at a time:

```python run
from functools import reduce

amounts = [100.0, 250.0, 50.0]
print(reduce(lambda total, x: total + x, amounts))       # ((100 + 250) + 50)
print(reduce(lambda a, b: a if a > b else b, amounts))   # the maximum
```

For sums, minimums and maximums the built-in functions are clearer. `reduce` is useful
for "fold" operations without a built-in - for example, combining many sets with `|`.
:::

::: tip Try it
Change `row` in the `map(str.strip, ...)` example: convert the fields to upper case
too. Can you do both with one `map`? (Hint: a `lambda`, or a comprehension:
`[f.strip().upper() for f in row.split(",")]`.)
:::

## 6. A table as a list of rows

### The shape of a table in Python

A SAS dataset or an SQL table has rows and columns. In plain Python, the simplest
form is a **list of rows**, where each row is a list or a tuple, and a separate list
of column names:

```python run
header = ["loan_id", "product", "outstanding", "stage"]
rows = [
    ["L000001", "investment", 1044231.30, 1],
    ["L000002", "investment", 651927.30, 2],
    ["L000003", "credit_card", 644.25, 2],
]

print(rows[1])          # a row
print(rows[1][2])       # a cell: row 1, column 2
print([row[2] for row in rows])     # a column
```

![A table drawn as a grid; one row is rows[1], one column is the list [row[2] for row in rows], one cell is rows[1][2]](/diagrams/table-rows.svg){.diagram}

- **a row**: `rows[i]`;
- **a cell**: `rows[i][j]` - first the row, then the column;
- **a column**: `[row[j] for row in rows]` - a comprehension over the rows.

### Read a CSV file into rows, with types

The fields of a file are text. A function that reads the file and converts each
column once, at the start:

```python run
def read_loans(path):
    """loans.csv as (header, rows); rows: lists with numbers converted."""
    with open(path, encoding="utf-8") as file:
        header = file.readline().strip().split(",")
        rows = []
        for line in file:
            f = line.strip().split(",")
            rows.append([f[0], f[1], f[2], f[3], f[4], f[5],
                         float(f[6]), float(f[7]), float(f[8]), int(f[9]), int(f[10])])
    return header, rows


header, rows = read_loans("data/loans.csv")
print(len(rows), "rows")
print(rows[0])
```

Column numbers like `7` are hard to remember. Find them by name with
`header.index`:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    header = file.readline().strip().split(",")

OUT = header.index("outstanding")
STAGE = header.index("stage")
print(OUT, STAGE)
```

(Session 6 gives each row its column names, with dictionaries. pandas does it for
you.)

### SQL on a list of rows

The usual SQL operations, one line each. Read the file once, then:

```python run
def read_loans(path):
    with open(path, encoding="utf-8") as file:
        header = file.readline().strip().split(",")
        rows = []
        for line in file:
            f = line.strip().split(",")
            rows.append([f[0], f[1], f[2], f[3], f[4], f[5],
                         float(f[6]), float(f[7]), float(f[8]), int(f[9]), int(f[10])])
    return header, rows

header, rows = read_loans("data/loans.csv")

# SELECT loan_id, product, outstanding FROM loans
selected = [(r[0], r[2], r[7]) for r in rows]

# ... WHERE currency = 'USD' AND stage > 1
usd_risky = [r for r in rows if r[3] == "USD" and r[10] > 1]

# derived column: repaid share = 1 - outstanding / amount
with_share = [r + [round(1 - r[7] / r[6], 4)] for r in rows]

# ORDER BY outstanding DESC, FETCH FIRST 3
top3 = sorted(rows, key=lambda r: r[7], reverse=True)[:3]

# SUM(outstanding), COUNT(*), AVG(interest_rate)
total = sum(r[7] for r in rows)
average_rate = sum(r[8] for r in rows) / len(rows)

print(selected[0])
print(len(usd_risky), "USD loans in stage 2 or 3")
print(with_share[0][-1])
print([r[0] for r in top3])
print(f"{total:,.2f}  {len(rows)}  {average_rate:.2f}")
```

Note `r + [value]`: a new row, longer by one column. `r.append(value)` would change
the original row - section 7.

### Column totals by group, with a loop

`GROUP BY stage` with a list: one total per stage, and the stage number as the index
(stage `1` at position `0`):

```python run
def read_loans(path):
    with open(path, encoding="utf-8") as file:
        file.readline()
        rows = []
        for line in file:
            f = line.strip().split(",")
            rows.append([f[0], f[1], f[2], f[3], f[4], f[5],
                         float(f[6]), float(f[7]), float(f[8]), int(f[9]), int(f[10])])
    return rows

rows = read_loans("data/loans.csv")

totals = [0.0, 0.0, 0.0]
counts = [0, 0, 0]
for r in rows:
    totals[r[10] - 1] += r[7]
    counts[r[10] - 1] += 1

for stage, (count, total) in enumerate(zip(counts, totals), start=1):
    print(f"stage {stage}: {count:>4} loans {total:>18,.2f}")
```

This works because the groups are the numbers 1, 2, 3. For groups like products or
regions you need a dictionary - session 6.

### A cross table: a list of lists

A table of counts: stages in the rows, currencies in the columns - `PROC FREQ` with
`TABLES stage * currency`:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    rows = [line.strip().split(",") for line in file]

currencies = ["EUR", "USD"]
table = [[0, 0] for stage in range(3)]           # 3 rows, 2 columns - all zeros

for r in rows:
    table[int(r[10]) - 1][currencies.index(r[3])] += 1

print("stage   EUR  USD")
for stage, counts in enumerate(table, start=1):
    print(f"{stage:>5} {counts[0]:>5} {counts[1]:>4}")
```

### A trap: `[[0] * 3] * 3`

Why `[[0, 0] for stage in range(3)]`, and not the shorter `[[0, 0]] * 3`? The `*`
repeats the **reference**, not the list: all three rows are **one** list.

```python run
table = [[0, 0]] * 3
table[0][0] = 99
print(table)                    # [[99, 0], [99, 0], [99, 0]] - all rows changed!

table = [[0, 0] for _ in range(3)]
table[0][0] = 99
print(table)                    # [[99, 0], [0, 0], [0, 0]]
```

The comprehension runs `[0, 0]` three times - three new lists. (The name `_` is the
custom for a loop variable that is not used.)

::: info The same in pandas
A DataFrame is a table with names for the columns, and the operations of this section
are one call each (sessions 14 - 15):

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(loans.nlargest(3, "outstanding")[["loan_id", "product", "outstanding"]])
print(pd.crosstab(loans["stage"], loans["currency"]))
```
:::

::: tip Try it
In the "SQL on a list of rows" block, add a line for `WHERE product = 'mortgage'
AND interest_rate > 6` - how many loans? Then add the derived column "years to
maturity" (hint: the year is `int(r[5][:4])`, the report year is 2026).
:::

## 7. Copies of nested lists

### A shallow copy shares the rows

Session 3: `rows.copy()`, `rows[:]` and `list(rows)` make a **new list**. But the
items in it - here the rows - are the **same** objects. The copy is *shallow*:

```python run
rows = [["L000001", 1044231.30], ["L000002", 651927.30]]
backup = rows.copy()

rows[0][1] = 0.0                   # change a cell of the original
print(backup[0])                   # the "backup" changed too!

rows.append(["L000003", 644.25])   # add a row to the original
print(len(rows), len(backup))      # this does not touch the copy
```

The outer list is copied; the inner lists are shared. Changing a **cell** shows in
both; adding or removing a **row** does not.

### `copy.deepcopy`: copy everything

`copy.deepcopy` copies the list **and** every list inside it, at every level:

```python run
import copy

rows = [["L000001", 1044231.30], ["L000002", 651927.30]]
backup = copy.deepcopy(rows)

rows[0][1] = 0.0
print(rows[0], backup[0])          # the backup keeps the old value
```

Use it before you change cells of a table that you still need in its original form -
like `data backup; set loans; run;` before an update in SAS.

### Better: rows that cannot change

If the rows are **tuples**, nobody can change a cell - not by mistake, not through a
shared reference. To change a value, you build a new row:

```python run
rows = [("L000001", 1044231.30), ("L000002", 651927.30)]
backup = rows.copy()               # a shallow copy is enough now

rows[0] = (rows[0][0], 0.0)        # a new tuple in the original list
print(rows[0], backup[0])
```

The comprehensions of this lecture always build new rows - `r + [value]`, `(r[0],
r[2])` - so they never change the input. That is the safe default for data work.

::: info pandas and copies
In pandas 3 (and in 2.2 with copy-on-write switched on), a selection behaves like a
copy: changing it never changes the original DataFrame. Session 15 shows it.
:::

**Check yourself.** What does this print?

```python
a = [[1, 2], [3, 4]]
b = a[:]
b[0] = [9, 9]
b[1][0] = 7
print(a)
```

::: details Answer
`[[1, 2], [7, 4]]`. `b[0] = [9, 9]` puts a new list into `b` only (the outer lists are
different). `b[1][0] = 7` changes the inner list that `a` and `b` share.
:::

## 8. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: `git pull upstream main`) and run the tasks from the
terminal, in the repository root:

```bash
python 05-lists-advanced/practice/task1-comprehensions.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-comprehensions.py` | Derived lists and filters on a list of loans |
| 2 | `task2-predict-lists.py` | Predict: comprehension filters, `zip` length, a used-up `map`, `[[0] * 2] * 2` |
| 3 | `task3-checks-extremes.py` | Data checks with `any` / `all`; `min` / `max` with `key` and `default` |
| 4 | `task4-sort-top-n.py` | Several sort keys with mixed directions; the top 10 with a rank |
| 5 | `task5-zip-columns.py` | Columns to rows and back; the change from month to month |
| 6 | `task6-table-of-rows.py` (Optional) | `loans.csv` as a list of rows: convert, select, filter, sort, totals, a safe copy |

## Summary

| Topic | Remember |
|-------|----------|
| Comprehension | `[expr for x in items if cond]` = `SELECT expr ... WHERE cond`; always a new list |
| `if` position | `if` at the end filters; `a if c else b` at the start chooses a value (CASE) |
| Generator expression | `sum(x for x in items)` - no list in memory; also `min`, `max`, `any`, `all` |
| Set comprehension | `{x for x in items}` = `SELECT DISTINCT` |
| Checks | `any(...)` = `EXISTS`; `all(...)` - every row; `all([])` is `True` |
| Extremes | `max(rows, key=...)` gives the whole row; `default=` for empty input; convert text first |
| Sorting | a tuple key = `ORDER BY a, b`; `-x` for a descending number; or two stable sorts; top N: `sorted(...)[:n]` |
| `zip` | parallel lists -> tuples; `zip(*rows)` transposes; stops at the shortest - `strict=True` |
| `enumerate` | `(number, item)`; `start=1` for a rank or a line number |
| Iterators | `zip`, `map`, `filter`, `enumerate` give their values once |
| `map` / `filter` | `map(float, fields)`; a comprehension is usually clearer |
| Table | a list of rows; cell `rows[i][j]`; column `[r[j] for r in rows]`; never `[[0] * n] * m` |
| Copies | `rows.copy()` shares the rows; `copy.deepcopy` copies all; tuples cannot change |

## Homework

1. `05-lists-advanced/homework.py` (in the homework repository): **the portfolio as a
   list of records** - read `loans.csv` into rows with types, find the ten largest
   exposures and their share of the portfolio (the concentration), build the stage x
   product count table as a list of lists (a `PROC FREQ` cross table by hand), and
   check the data with `any` / `all`. Every check must print `OK`.
2. The practice tasks you did not finish in class.
3. Optional: print the cross table of the homework as a small report, with the
   products as columns, totals at the end of each row and a total row at the bottom.

## Self-study

This part is not covered in class. It is for reading at home: two tools that SAS
users miss in plain Python - `RETAIN`, `LAG` and BY groups - and a way to read files
that do not fit in memory.

### `itertools`: running totals, `LAG` and BY groups

The module `itertools` has building blocks for loops. Three of them replace common
DATA step patterns.

**`accumulate` - a running total (`RETAIN`).** In SAS: `retain total 0; total + x;`.

```python run
from itertools import accumulate

payments = [1200.0, 800.0, 1500.0, 900.0]
print(list(accumulate(payments)))                  # running sum
print(list(accumulate(payments, max)))             # running maximum
```

**`pairwise` - the value and the one before (`LAG`).** Since Python 3.10:

```python run
from itertools import pairwise

outstanding = [128.4, 129.1, 130.2, 129.6]
for before, now in pairwise(outstanding):
    print(before, "->", now, round(now - before, 1))
```

It is the same as `zip(xs, xs[1:])` from section 4, without the copy of the list.

**`groupby` - BY-group processing (`FIRST.` / `LAST.`).** `groupby` cuts a **sorted**
list into groups of equal keys - like a DATA step with `BY product`:

```python run
from itertools import groupby

with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    rows = [line.strip().split(",") for line in file]

rows.sort(key=lambda r: r[2])                       # PROC SORT; BY product
for product, group in groupby(rows, key=lambda r: r[2]):
    group = list(group)                             # the rows of one product
    total = sum(float(r[7]) for r in group)
    print(f"{product:<16}{len(group):>4}{total:>18,.2f}")
```

::: warning Sort first
`groupby` starts a new group every time the key **changes**. On unsorted data the same
product appears in many small groups - exactly like a SAS `BY` without `PROC SORT`,
except that Python does not stop with an error.
:::

Two more: `islice(iterable, n)` takes the first `n` items of any iterator (`OBS=n`),
and `chain(a, b)` reads several lists one after another (`SET a b;`).

```python run
from itertools import chain, islice

print(list(islice(range(1000), 3)))
print(list(chain(["L000001", "L000002"], ["L000400"])))
```

**Exercises**

1. With `accumulate`, find the first month in which the running total of
   `[1200, 800, 1500, 900, 1100]` goes over 3000.
2. With `groupby`, count the loans per currency in `loans.csv`. Why must you sort
   first?

::: details Answer
1.
```python
from itertools import accumulate
payments = [1200, 800, 1500, 900, 1100]
for month, total in enumerate(accumulate(payments), start=1):
    if total > 3000:
        print(month, total)      # 3 3500
        break
```
2. Sort by currency, then `groupby(rows, key=lambda r: r[3])` and `len(list(group))`:
EUR 361, USD 39. Without sorting, EUR and USD rows alternate, and you get many small
groups instead of two.
:::

### Generator functions: `yield`

A function with `yield` instead of `return` is a **generator function**. Each call of
`next` runs it until the next `yield`, and the function **waits** there, with its local
variables, until the next value is asked for:

```python run
def months(n):
    for i in range(1, n + 1):
        print("  (making month", i, ")")
        yield i

for m in months(3):
    print("got", m)
```

This is useful for big files: a generator that reads one row at a time, converts it
and gives it on. The whole file is never in memory - only the current row:

```python run
def loan_rows(path):
    """The rows of loans.csv, one at a time, with the numbers converted."""
    with open(path, encoding="utf-8") as file:
        file.readline()
        for line in file:
            f = line.strip().split(",")
            yield f[0], f[2], float(f[7]), int(f[10])

total = sum(outstanding for loan_id, product, outstanding, stage in loan_rows("data/loans.csv"))
largest = max(loan_rows("data/loans.csv"), key=lambda row: row[2])
print(f"{total:,.2f}", largest)
```

A generator, like `zip` or `map`, is used up after one pass - here each line calls
`loan_rows(...)` again, which opens the file again. A SAS DATA step works this way
too: it reads one observation at a time.

**Exercises**

1. Write a generator `late_loans(path, limit)` that yields only the `loan_id` of the
   loans with `days_past_due` greater than `limit`. Count them for `limit=90`.
2. What does `list(g)` print the second time, for `g = loan_rows("data/loans.csv")`?

::: details Answer
1.
```python
def late_loans(path, limit):
    with open(path, encoding="utf-8") as file:
        file.readline()
        for line in file:
            f = line.strip().split(",")
            if int(f[9]) > limit:
                yield f[0]

print(sum(1 for _ in late_loans("data/loans.csv", 90)))     # 17
```
2. `[]` - the generator is used up after the first `list(g)`.
:::

## Read more

- Python tutorial: [List comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions),
  [Nested list comprehensions](https://docs.python.org/3/tutorial/datastructures.html#nested-list-comprehensions)
- [Sorting techniques](https://docs.python.org/3/howto/sorting.html) (keys, stability,
  `operator.itemgetter`)
- Reference: [`zip`](https://docs.python.org/3/library/functions.html#zip),
  [`enumerate`](https://docs.python.org/3/library/functions.html#enumerate),
  [`map`](https://docs.python.org/3/library/functions.html#map),
  [`filter`](https://docs.python.org/3/library/functions.html#filter),
  [`copy`](https://docs.python.org/3/library/copy.html),
  [`itertools`](https://docs.python.org/3/library/itertools.html)
- Real Python: [When to use a list comprehension](https://realpython.com/list-comprehension-python/),
  [Python's `zip()` function](https://realpython.com/python-zip-function/)

**Next session:** dictionaries - a key and a value, the Python version of a SAS format
and of a lookup table; counting and `GROUP BY` without pandas.
