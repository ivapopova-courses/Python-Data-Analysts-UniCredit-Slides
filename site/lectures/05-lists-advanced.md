---
title: 5. Lists (advanced)
---

# 5. Lists (advanced)

<div class="lecture-meta">
  <span>Session 5</span><span>practice: <code>05-lists-advanced/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- remove items from a list, find the position of an item, and sort a list - the
  methods of a list that session 3 did not show in class;
- build a new list from an old one in one line, with a **list comprehension** - the
  Python version of SQL `SELECT expression ... WHERE condition`;
- sum and count with a condition without building a list, with a **generator
  expression** - and see why it saves memory;
- walk over several lists together with `zip`, and number the items with
  `enumerate`.

From SQL to Python - the same question, two ways. The loans more than 30 days past
due, in EUR thousands, the largest first:

```sql
SELECT loan_id, ROUND(outstanding / 1000, 1) AS outstanding_k
FROM loans
WHERE days_past_due > 30
ORDER BY outstanding_k DESC;
```

```python run
# (loan_id, outstanding, days_past_due)
loans = [
    ("L000001", 1044231.30, 0),
    ("L000002", 651927.30, 35),
    ("L000005", 3127.40, 120),
    ("L000007", 12400.00, 60),
]

late = [(loan[0], round(loan[1] / 1000, 1)) for loan in loans if loan[2] > 30]   # SELECT ... WHERE
late.sort(key=lambda loan: loan[1], reverse=True)                      # ORDER BY ... DESC
print(late)
```

Two lines do the work: a comprehension is the `SELECT ... WHERE`, and `sort` is the
`ORDER BY`. By the end of today you can write both.

## 1. More list methods

[Session 3](./03-lists-tuples-sets.md#_6-the-methods-of-a-list) has the table of all
list methods. In class we used `append` and `extend`. Here are the others you need
most: remove items, find an item, sort.

### Remove items: `remove`, `pop`, `del`

```python run
ids = ["L000001", "L000002", "L000003", "L000004", "L000005"]

ids.remove("L000003")        # remove by value
print(ids)

last = ids.pop()             # remove the last item, and get it back
print(last, ids)

first = ids.pop(0)           # remove the item at index 0
print(first, ids)

del ids[0]                   # remove by index, nothing comes back
print(ids)
```

| You know | Use |
|---|---|
| the value | `lst.remove(value)` |
| the index, and you need the item | `item = lst.pop(index)` (`lst.pop()`: the last one) |
| the index, or a slice | `del lst[index]`, `del lst[start:stop]` |

These change the list **in place** - there is no new list. In SQL it is a `DELETE`
on the table itself; in SAS you would write a new data set without the rows.

### `remove`: only the first one, and an error if it is not there

`remove` removes **one** item - the first one equal to the value. When the value is
not in the list, it stops with a `ValueError`. Test with `in` first
([session 3](./03-lists-tuples-sets.md#membership-in-not-in)):

```python run
products = ["mortgage", "overdraft", "consumer", "overdraft"]

products.remove("overdraft")
print(products)              # the second "overdraft" is still there

if "leasing" in products:
    products.remove("leasing")
print(products)

products.remove("leasing")   # ValueError: list.remove(x): x not in list
```

To remove **all** items with one value, build a new list without them - the list
comprehension of [section 2](#_2-list-comprehensions).

### `clear`: empty the list

```python run
batch = ["L000001", "L000002", "L000003"]
print(len(batch))

batch.clear()                # the same list, now empty
print(batch, len(batch))
```

A common use: collect items in a loop, process them in groups, and empty the list
after each group.

### `index`: the position of an item

`lst.index(value)` gives the index of the **first** item equal to the value - and,
like `remove`, a `ValueError` when there is none:

```python run
months = ["Jul", "Aug", "Sep", "Oct"]
outstanding = [128.4, 129.1, 130.2, 129.6]       # EUR million

i = months.index("Sep")
print(i, outstanding[i])          # the outstanding in September

print("Dec" in months)            # False - so do not call months.index("Dec")
```

With two lists in the same order, `index` finds the position in one list, and the
same position reads the other. (Section 4 shows `zip`, which walks over both lists
together.)

`lst.count(value)` ([session 3](./03-lists-tuples-sets.md#len-min-max-sum-count-index))
says how many times the value is there; `count(x) > 0` is the same as `x in lst`.

::: tip Try it
In the `index` example, find the outstanding of `"Oct"`. Then add `"Sep"` once more
at the end of `months` (and a value at the end of `outstanding`): which September
does `index` find?
:::

### Sort a list: `sort()` and `sorted()`

- `lst.sort()` sorts **this** list, in place. Only lists have it.
- `sorted(x)` returns a **new**, sorted list and does not change `x`. It works on any
  sequence: a list, a tuple, a set, a string.
- Both take `reverse=True`: from the largest.

```python run
amounts = [5875.11, 651927.30, 644.25, 1044231.30]

print(sorted(amounts))              # a new list
print(amounts)                      # not changed

amounts.sort(reverse=True)          # this list, from the largest
print(amounts)
```

Text sorts alphabetically, capital letters before small ones
([session 2](./02-conditions-and-loops.md#strings-are-compared-letter-by-letter)):

```python run
print(sorted(["overdraft", "Mortgage", "consumer"]))
```

In SAS this is `PROC SORT` (it sorts the data set in place, like `sort()`, unless you
give `OUT=`); in SQL `ORDER BY` (it returns new rows, like `sorted()`).

::: warning The methods return `None`
`sort`, `append`, `remove`, `clear` and the other methods change the list and return
`None`, not the list. A classic bug:

```python run
amounts = [3.0, 1.0, 2.0]
amounts = amounts.sort()        # wrong!
print(amounts)
```

`amounts.sort()` sorts the list and returns `None`, and `amounts = ...` keeps that
`None` - the list is lost. Write only `amounts.sort()`, or `amounts =
sorted(amounts)`.
:::

### Sort by a key

[Session 4](./04-functions.md#sorting-by-a-key) showed `key=`: a function that says
**what** to compare. With records - tuples or lists - the key picks the column:

```python run
# (loan_id, product, outstanding)
loans = [
    ("L000004", "overdraft", 5875.11),
    ("L000002", "investment", 651927.30),
    ("L000003", "credit_card", 644.25),
    ("L000001", "investment", 1044231.30),
]

by_amount = sorted(loans, key=lambda loan: loan[2], reverse=True)   # ORDER BY outstanding DESC
for loan in by_amount:
    print(loan)

loans.sort(key=lambda loan: loan[1])                                # ORDER BY product
print([loan[1] for loan in loans])
```

`max` and `min` take the same `key=`, and give back the **whole record**:

```python run
loans = [
    ("L000004", "overdraft", 5875.11),
    ("L000002", "investment", 651927.30),
    ("L000003", "credit_card", 644.25),
]

print(max(loans, key=lambda loan: loan[2]))      # the largest loan
print(min(loans, key=lambda loan: loan[2]))      # the smallest loan
```

### The top N

Sort from the largest, then take a slice ([session 3](./03-lists-tuples-sets.md#slices-start-stop-step)):
`sorted(...)[:n]` is SQL `ORDER BY ... DESC FETCH FIRST n ROWS ONLY`, or in SAS
`PROC SORT` with `BY DESCENDING`, then `SET sorted(OBS=n)`.

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()                                     # skip the header
    rows = [line.strip().split(",") for line in file]   # a list of rows (section 2)

top3 = sorted(rows, key=lambda row: float(row[7]), reverse=True)[:3]
for row in top3:
    print(row[0], row[2], row[7])
```

The fields of a file are text: `float(row[7])` in the key compares the amounts as
numbers. Without it, `"9"` would be larger than `"10"`.

::: info The same in pandas
In pandas ([session 15](./15-pandas-select-aggregate-join.md#_3-sorting-and-the-top-n))
a table is sorted by the name of a column:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
print(loans.sort_values("outstanding", ascending=False).head(3)[["loan_id", "product", "outstanding"]])
print(loans.nlargest(3, "outstanding")["loan_id"].tolist())     # the same top 3
```
:::

::: warning Do not remove items while you loop over the same list
The loop goes through the list **by position**. When you remove an item, the next
one moves into its place - and the loop skips it:

```python run
amounts = [0.0, 0.0, 500.0, 0.0]
for amount in amounts:
    if amount == 0:
        amounts.remove(amount)
print(amounts)             # [500.0, 0.0] - one zero is still there
```

Build a **new** list with the items you keep. The next section does it in one line.
:::

**Check yourself.** What does this print?

```python
stages = [2, 1, 3, 1]
result = stages.sort()
print(result, stages)
```

::: details Answer
`None [1, 1, 2, 3]`. `sort()` sorted the list `stages` in place and returned `None`.
:::

## 2. List comprehensions

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
derived variable in a SAS DATA step:

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

print([(loan_id, loan_id[-3:]) for loan_id in ids])
```

With your own function from [session 4](./04-functions.md) - a `CASE WHEN` with many branches, written
once and used in one short line:

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

In SQL: `SELECT d FROM days WHERE d > 90`; in SAS: a subsetting `IF` in a DATA step.
With both parts - a new value **and** a filter:

```python run
rates = [8.83, 5.44, 4.79, 8.35, 12.10]

# SELECT rate / 100 FROM rates WHERE rate > 8
print([rate / 100 for rate in rates if rate > 8])
```

This is also the safe way to "remove" items (the warning of section 1): keep the
ones you want, in a new list.

```python run
amounts = [0.0, 0.0, 500.0, 0.0]
amounts = [a for a in amounts if a != 0]
print(amounts)
```

### On the portfolio

Read `loans.csv` into a list of rows - one comprehension - and select from it.
Each row is a list of strings, in the order of the header. The ids of the stage 3
loans (`stage` is column 10), and the outstanding amounts in thousands of the USD
loans:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    header = file.readline().strip().split(",")
    rows = [line.strip().split(",") for line in file]

print(header)
print(len(rows), "rows; the first one:", rows[0])

stage3 = [row[0] for row in rows if row[10] == "3"]
print(len(stage3), stage3[:5])

usd_k = [round(float(row[7]) / 1000, 1) for row in rows if row[3] == "USD"]
print(len(usd_k), usd_k[:5])
```

The columns are still **text** - `row[10] == "3"`, not `== 3`. Convert where you need
a number (`float(row[7])`), as in [session 2](./02-conditions-and-loops.md#the-rows-of-a-file).
The position of a column is `header.index("stage")` (section 1).

### `CASE WHEN` inside: `a if condition else b`

A conditional expression ([session 2](./02-conditions-and-loops.md#_7-conditional-expressions)) can be the expression of a comprehension. Then
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

With curly brackets instead of square ones, you get a **set** - the distinct values
([session 3](./03-lists-tuples-sets.md#unique-values-sql-select-distinct)):
`{row[2] for row in rows}` is `SELECT DISTINCT product`.

### When not to use a comprehension

A comprehension is for **building a new list**. Use a normal loop when:

- you only want an effect, not a list - for example printing;
- the logic needs several steps or several `if` / `elif` branches - put it into a
  function and call the function in the comprehension, as with `dpd_bucket` above,
  or write the loop;
- the line becomes too long to read in one look (more than about 80 characters).

::: details Advanced: `map` and `filter`
You will meet them in other people's code. Both take a **function** and a list,
and call the function for every item:

- `map(function, items)` gives the result of the function for every item: as many
  items out as in, like the expression of a comprehension (SQL: `SELECT`
  expression).
- `filter(function, items)` keeps the items for which the function returns
  something true: fewer items, like the `if` at the end of a comprehension (SQL:
  `WHERE`).

![map sends every item of days through d // 30 and gives 5 new values; filter tests every item with d > 30 and keeps only 35 and 120](/diagrams/map-filter.svg){.diagram width=920 height=400}

Both give their values one by one, like a generator (section 3) - wrap them in
`list()` to see them. A comprehension does the same job and reads better:

```python run
days = [0, 35, 0, 120, 15]

print(list(map(lambda d: d // 30, days)), [d // 30 for d in days])
print(list(filter(lambda d: d > 30, days)), [d for d in days if d > 30])

fields = ["1156900.00", "1044231.30", "8.83"]
print(list(map(float, fields)))           # short when the function has a name
```

In pandas, `map` comes back: `series.map(function)` or `series.map(dictionary)`
(sessions 6 and 15).
:::

::: info The same in pandas
In pandas ([session 14](./14-numpy-pandas-intro.md#columns)) you do not loop at all - an operation on a column works on
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
```

Then change the second line to keep only the values between 10 and 100.
:::

## 3. Generator expressions: no list in memory

### `sum(... for ...)`: SUM and COUNT with a condition

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

- `sum(x for ... if ...)` is SQL `SUM(x) ... WHERE ...`;
- `sum(1 for ... if ...)` is SQL `COUNT(*) ... WHERE ...`: one `1` for each row
  that passes.

This is a **generator expression**. It works inside any function that takes many
values: `sum`, `min`, `max`, `sorted`, `list`, `", ".join(...)`.

### Why: a generator does not keep the values

A list comprehension builds the **whole list** first, and keeps all its values in
memory. A generator expression keeps **none** of them: it makes the next value only
when `sum` asks for it, gives it, and forgets it.

```python run
import sys

as_list = [x * 2 for x in range(1_000_000)]     # a million values in memory
as_generator = (x * 2 for x in range(1_000_000))  # a recipe for the values

print(sys.getsizeof(as_list))         # millions of bytes - and the numbers come on top
print(sys.getsizeof(as_generator))    # about a hundred bytes, for any number of values
print(sum(as_list), sum(as_generator))
```

The result is the same; the memory is not. (On your computer the list takes
about 8 MB; in the browser of this site about 4 MB. The numbers inside it take more
memory again.) It is the idea of `range` in
[session 3](./03-lists-tuples-sets.md#a-range-does-not-keep-its-numbers): a range of a
billion numbers is small, because it does not keep them. A SAS DATA step works this
way too: it reads one observation, processes it, and goes to the next.

(The round brackets make a generator on its own line. Inside a call - `sum(x for x
in ...)` - the brackets of the call are enough.)

### A file, one line at a time

A file works the same way: `for line in file` reads **one line at a time**. A
generator over the file gives the total of a file of any size, and only one line is
in memory at a time:

```python run
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()                                           # skip the header
    total = sum(float(line.split(",")[7]) for line in file)   # one line at a time

print(f"{total:,.2f}")
```

The list of rows of section 2 (`rows = [... for line in file]`) keeps the whole file
in memory. For `loans.csv` (400 rows) both are fine. For a file of 10 million rows,
the generator still works on a laptop.

::: info The same in pandas
`pd.read_csv` reads the **whole** file into memory. For a file larger than the
memory, `chunksize=` reads it in pieces, and you add up the pieces - the same idea:

```python run
import pandas as pd

total = 0
for chunk in pd.read_csv("data/loans.csv", chunksize=100):    # 100 rows at a time
    total += chunk["outstanding"].sum()
print(f"{total:,.2f}")
```
:::

### A trap: a generator is used once

A generator gives its values **once**. After that it is empty - there is nothing
kept to give again:

```python run
late = (d for d in [0, 35, 120, 15] if d > 0)

print(sum(late))        # 170
print(sum(late))        # 0 - already used up
```

It also has no `len()` and no index (`late[0]` is an error). When you need the
values more than once, or their number, make a **list** - that is what lists are
for.

::: tip Try it
Predict, then press **Run**:

```python run
days = [0, 35, 0, 120, 15]
print(sum(1 for d in days if d > 30))
print(sum(d for d in days if d > 30))
print(max(d for d in days if d < 100))
g = (d for d in days)
print(list(g), list(g))
```
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

Each item of `zip` is a tuple, and `for loan_id, product, amount in ...` takes it
apart into three names - the **unpacking** of [session 3](./03-lists-tuples-sets.md#unpacking),
`loan_id, product, amount = ("L000001", "investment", 1044231.30)`, done for every
item.

Columns become rows. A common use: two lists of the same months, compared month by
month:

```python run
months = ["Jul", "Aug", "Sep"]
outstanding_2025 = [128.4, 129.1, 130.2]       # EUR million
outstanding_2026 = [129.9, 130.8, 131.4]

for month, before, now in zip(months, outstanding_2025, outstanding_2026):
    print(f"{month}: {now - before:+.1f} million ({(now / before - 1):+.2%})")
```

And in a comprehension - a new list from two lists, item by item:

```python run
outstanding = [1044231.30, 651927.30, 644.25]
rates = [8.83, 5.44, 4.79]

interest = [round(o * r / 100, 2) for o, r in zip(outstanding, rates)]
print(interest)
```

`zip` gives its pairs one by one, like a generator: `list(zip(...))` shows them all.
Two lists - the keys and the values - become a dictionary with `dict(zip(keys,
values))` in [session 6](./06-dictionaries.md).

### A trap: the shortest list wins

`zip` stops at the end of the **shortest** list - without an error. A missing value
in one list silently drops the last row:

```python run
loan_ids = ["L000001", "L000002", "L000003"]
amounts = [1044231.30, 651927.30]                  # one is missing!

print(list(zip(loan_ids, amounts)))                # L000003 is gone
```

Check the lengths first when the lists come from different places:
`len(loan_ids) == len(amounts)`.

### `enumerate`: the number of each item

Sometimes you need the **position** of each item, not only the item.
[`enumerate(items, start=0)`](https://docs.python.org/3/library/functions.html#enumerate)
gives pairs `(number, item)` - it is a `zip` of the numbers 0, 1, 2, ... and the
items:

```python run
products = ["investment", "overdraft", "mortgage"]

for i, product in enumerate(products):
    print(i, product)

print(list(enumerate(products, start=1)))
```

With `start=1` the number is a **rank** - here for the top N of section 1:

```python run
loans = [
    ("L000004", 5875.11),
    ("L000002", 651927.30),
    ("L000003", 644.25),
    ("L000001", 1044231.30),
]

top3 = sorted(loans, key=lambda loan: loan[1], reverse=True)[:3]
for rank, loan in enumerate(top3, start=1):
    print(f"{rank}. {loan[0]} {loan[1]:>15,.2f}")
```

In SAS, the number of the current row in a DATA step is `_N_`; in SQL, a rank is
`ROW_NUMBER() OVER (ORDER BY outstanding DESC)`.

::: info The same in pandas
In a DataFrame, the columns are already side by side - no `zip` is needed. A new
column from two columns is one line:

```python run
import pandas as pd

loans = pd.read_csv("data/loans.csv")
loans["interest"] = (loans["outstanding"] * loans["interest_rate"] / 100).round(2)
print(loans[["loan_id", "outstanding", "interest_rate", "interest"]].head(3))
```
:::

::: tip Try it
Predict the output, then run it:

```python run
a = [1, 2, 3, 4]
b = ["x", "y"]
print(list(zip(a, b)))
print([n * 10 for n, letter in zip(a, b)])
print(list(enumerate(b, start=10)))
```
:::

## 5. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root:

```bash
python 05-lists-advanced/practice/task1-list-methods.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-list-methods.py` | Remove, find and sort with the list methods; the top 3 |
| 2 | `task2-comprehensions.py` | Derived lists, filters and `CASE WHEN` with comprehensions |
| 3 | `task3-predict-lists.py` | Predict: `sort()` and `None`, the position of `if`, a used generator, `zip` |
| 4 | `task4-generators.py` | Sums and counts with a condition, without a list; a file line by line |
| 5 | `task5-zip.py` | Two lists side by side; a rank with `enumerate` |
| 6 | `task6-clean-a-list.py` (Optional) | Clean a list of loans step by step, then report on it |

## Summary

| Topic | Remember |
|-------|----------|
| Remove | `remove(value)` - the first one, `ValueError` if missing; `pop(i)` gives the item back; `del lst[i]`; `clear()` empties |
| Find | `index(value)` - the first position, `ValueError` if missing: test with `in` first |
| Sort | `lst.sort()` changes the list; `sorted(x)` gives a new one; `key=`, `reverse=True`; top N: `sorted(...)[:n]` |
| `None` | the methods change the list and return `None`: never `x = x.sort()` |
| Comprehension | `[expr for x in items if cond]` = `SELECT expr ... WHERE cond`; always a new list |
| `if` position | `if` at the end filters; `a if c else b` at the start chooses a value (CASE) |
| Generator expression | `sum(x for x in items)` - no list in memory; `sum(1 for ... if ...)` = `COUNT(*) ... WHERE`; used once |
| `zip` | parallel lists -> tuples; stops at the shortest list |
| `enumerate` | `(number, item)`; `start=1` for a rank |

## Homework

1. `05-lists-advanced/homework.py` (in the homework repository): **a small list of
   loans** - clean it with the list methods, find the five largest exposures with a
   rank and their share of the total, sum and count with a condition, and compare
   two years month by month with `zip`. Every check must print `OK`.
2. The practice tasks you did not finish in class.

## Read more

- Python tutorial: [More on lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists),
  [List comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
- [Sorting techniques](https://docs.python.org/3/howto/sorting.html)
- Reference: [generator expressions](https://docs.python.org/3/reference/expressions.html#generator-expressions),
  [`zip`](https://docs.python.org/3/library/functions.html#zip),
  [`enumerate`](https://docs.python.org/3/library/functions.html#enumerate)
- Real Python: [When to use a list comprehension](https://realpython.com/list-comprehension-python/),
  [Python's `zip()` function](https://realpython.com/python-zip-function/)

**Next session:** dictionaries - a key and a value, the Python version of a SAS format
and of a lookup table; counting and SQL `GROUP BY` without pandas.
