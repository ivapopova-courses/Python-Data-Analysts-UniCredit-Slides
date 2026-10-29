---
title: 3. Lists (basics), tuples and sets
---

# 3. Lists (basics), tuples and sets

<div class="lecture-meta">
  <span>Session 3</span><span>practice: <code>03-lists-tuples-sets/</code> in the homework repository</span>
  <span><a href="../sample-data">the sample data</a></span>
</div>

**Today you will learn to:**

- keep many values in one **list**, and read them by index (from 0!) and by slices;
- use the operations that all sequences share: `+`, `*`, `in`, `len`, `min`, `max`;
- change a list with its methods, and sort it;
- understand why two names can show the same list - and how to make a copy;
- use **tuples** as records that cannot change, and unpack them;
- use `range` for sequences of numbers;
- find unique values with **sets**, and compare groups with `UNION`, `INTERSECT` and
  `EXCEPT` - the Python way.

From SQL to Python - the same question, two ways. Which clients have no loans?

```sql
SELECT client_id FROM clients
EXCEPT
SELECT client_id FROM loans;
```

```python run
all_clients = set()
with open("data/clients.csv", encoding="utf-8") as file:
    file.readline()                                  # skip the header
    for line in file:
        all_clients.add(line.split(",")[0])          # the 1st column: client_id

with_loans = set()
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    for line in file:
        with_loans.add(line.split(",")[1])           # the 2nd column: client_id

without_loans = all_clients - with_loans             # EXCEPT
print(len(all_clients), "clients,", len(with_loans), "with loans")
print(sorted(without_loans))
```

## 1. Sequences

### What is a sequence?

Session 2 used `for` on strings, lists and ranges. They are all **sequences**:
containers that keep an **ordered** collection of values. The main sequence types:

| Type | Example | Can it change? |
|---|---|---|
| `list` | `["mortgage", "consumer", "overdraft"]` | yes |
| `tuple` | `("L000001", "investment", 1044231.30)` | no |
| `range` | `range(1, 13)` | no |
| `str` | `"L000001"` | no |

```python run
products = ["mortgage", "consumer", "credit_card", "consumer", "overdraft"]   # a list
record = ("L000001", "investment", 1044231.30)                                # a tuple
months = range(1, 13)                                                         # a range
loan_id = "L000001"                                                           # a string

for value in [products, record, months, loan_id]:
    print(type(value).__name__, len(value))
```

Every item of a sequence has a number - its position, or **index**. The index
**starts from 0**.

::: warning Python counts from 0, SAS from 1
The first character of a string: `SUBSTR(loan_id, 1, 1)` in SAS and SQL, but
`loan_id[0]` in Python. The first element of a SAS array is `arr{1}`; of a Python list
it is `items[0]`. This is the most common mistake in the first weeks - count with
care.
:::

### What all sequences can do

All sequences support the same **common operations** - you learn them once:

| Operation | Example | Result |
|---|---|---|
| length | `len(s)` | the number of items |
| indexing | `s[0]`, `s[-1]` | the first, the last item |
| slicing | `s[1:3]` | a part of the sequence |
| concatenation | `s + t` | the two joined (not for `range`) |
| repetition | `s * 3` | three times (not for `range`) |
| membership | `x in s`, `x not in s` | `True` / `False` |
| minimum, maximum | `min(s)`, `max(s)` | the smallest, the largest item |
| counting | `s.count(x)` | how many times `x` is in `s` |
| searching | `s.index(x)` | the index of the first `x` |

Each type also has its **own** methods: lists can be sorted and changed, strings
can be made upper case. Reference:
[Common sequence operations](https://docs.python.org/3/library/stdtypes.html#common-sequence-operations).

## 2. Lists

### What is a list?

A **list** is a **mutable** (changeable) sequence of values:

- you can add, remove and change items: a list can grow and shrink;
- the items can be of any type, and of different types in one list;
- the same value can be in a list many times.

Lists are the general-purpose container of Python. A list is close to a column of a
table, or to a SAS array - but it can grow, and it lives in memory.

### Create a list

A list is written in **square brackets**, with the items separated by **commas**:

```python run
empty = []
stages = [1, 2, 3]
products = ["mortgage", "consumer", "credit_card"]
loan = ["L000001", "investment", 1044231.30, 8.83]     # different types
matrix = [                                             # a list of lists (session 5)
    [1, 2, 3],
    [4, 5, 6],
]
print(empty, stages, products)
print(loan)
print(len(products), len(empty), len(matrix))
```

### Read an item

```text
item = list_name[index]
```

```python run
fruits = ["apple", "banana", "strawberry", "banana", "orange"]
print(fruits[0])        # the first item: apple
print(fruits[2])        # the third item: strawberry
print(fruits[-1])       # the last item: orange
```

An index that does not exist is an error:

```python run
fruits = ["apple", "banana", "strawberry"]
print(fruits[3])        # 3 items: the indexes are 0, 1, 2
```

### Change an item

```text
list_name[index] = value
```

```python run
fruits = ["apple", "banana", "strawberry"]
fruits[1] = "plum"          # change the second item
print(fruits)
fruits[-1] = "orange"       # change the last item
print(fruits)
```

`del` removes an item by its index:

```python run
fruits = ["apple", "plum", "orange"]
del fruits[1]
print(fruits)
```

## 3. Indexes and slices

### Indexes from the start and from the end

- The first item has the index **0**; each next one is 1 more.
- The last item has the index **-1**; counting back, each one is 1 less.
- Only whole numbers are valid indexes.

![A list of six loans with the indexes 0 to 5 above the items and -6 to -1 below them; the slice loans[1:4] is highlighted](/diagrams/list-indexing.svg){.diagram}

```python run
numbers = [1, 2, 3, 4, 5]
print(numbers[0], numbers[1], numbers[2], numbers[3], numbers[4])
print(numbers[-1], numbers[-2], numbers[-3], numbers[-4], numbers[-5])
```

Negative indexes are handy for "the last ones": the last month of a list of monthly
values is `values[-1]`, whatever the length of the list.

### Slices: `[start:stop:step]`

A **slice** takes a part of a sequence:

```text
sequence[start:stop:step]
```

- `start` - the index of the first item taken (included); empty = from the start;
- `stop` - the index where the slice **stops** (this item is **not** included); empty =
  to the end;
- `step` - take every n-th item; empty = 1. A negative step goes backwards.

```text
a[start:stop]     items from start up to stop - 1
a[start:]         items from start to the end
a[:stop]          items from the beginning up to stop - 1
a[:]              all items - a copy of the whole sequence
```

The rule "the stop is not included" is the same as in `range` (session 2). It has a
nice side: `a[:3]` is the first 3 items, `a[3:]` the rest, and `a[2:5]` has 5 - 2 = 3
items.

```python run
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(numbers[2:5])      # [2, 3, 4]
print(numbers[1:9:2])    # [1, 3, 5, 7]
print(numbers[:3])       # the first 3: [0, 1, 2]
print(numbers[-3:])      # the last 3: [7, 8, 9]
print(numbers[:-4:-1])   # the last 3, reversed: [9, 8, 7]
print(numbers[::-1])     # all, reversed
numbers_copy = numbers[:]
print(numbers_copy)
```

A slice never gives an `IndexError` - out of range, it simply takes what there is:

```python run
numbers = [0, 1, 2]
print(numbers[1:100])
print(numbers[5:10])
```

### Slices of strings: `SUBSTR`

A string is a sequence of characters, so the same indexes and slices work - this is
the Python `SUBSTR`:

| SAS / SQL | Python |
|---|---|
| `SUBSTR(loan_id, 1, 1)` | `loan_id[0]` |
| `SUBSTR(loan_id, 2)` | `loan_id[1:]` |
| `SUBSTR(report_date, 1, 4)` | `report_date[:4]` |
| `SUBSTR(report_date, 6, 2)` | `report_date[5:7]` |

```python run
greeting = "Hello, World!"
print(greeting[1:5])            # 'ello'

loan_id = "L000123"
print(loan_id[0], loan_id[1:], int(loan_id[1:]))

report_date = "2026-09-30"
year, month, day = report_date[:4], report_date[5:7], report_date[8:]
print(year, month, day)
```

Strings cannot be changed: `loan_id[0] = "X"` is an error. String methods (session 7)
make **new** strings.

## 4. More common operations

### Concatenation `+` and repetition `*`

`+` joins two sequences of the **same type** into a new one; `*` repeats a sequence. The
multiplier must be a whole number.

```python run
num_list = [1, 2, 3]
alpha_list = ["a", "b", "c"]
print(num_list + alpha_list)      # a new list

date1 = (31, "December", 2017)
date2 = (10, "March", 1999)
print(date1 + date2)              # a new tuple

print(num_list * 3)
print(alpha_list * 3)
print([0.0] * 12)                 # 12 months, all 0.0 - a common start value
```

Only strings, lists and tuples can be joined and repeated. A `range` cannot (but you
can make a list of it first: `list(range(3)) * 2`).

`+` makes a **new** list. Joining lists of rows one under the other is `UNION ALL` in
SQL, or `SET a b;` in a DATA step:

```python run
first_names = ["ivan", "maria", "petar"]
sur_names = ["ivanov", "popova", "petrov"]
names = first_names + sur_names
print(names)
```

### Membership: `in`, `not in`

`x in sequence` is `True` when `x` is one of the items - like `IN (...)` in SQL and SAS:

```python run
fruits = ["apple", "banana", "strawberry"]
numbers = [1, 2, 3]
print("banana" in fruits)
print("banana" in numbers)
print("banana" not in fruits)
print("banana" not in numbers)

r = range(0, 10)
print(3 in r, 21 in r)

product = "consumer"
if product in ["mortgage", "consumer", "credit_card", "overdraft"]:
    print("retail")
```

For strings, `in` looks for a part of the string: `"USD" in "EUR,USD"` is `True`.

### `len`, `min`, `max`, `sum`, `count`, `index`

```python run
outstanding = [1044231.30, 651927.30, 644.25, 5875.11]
print(len(outstanding))
print(min(outstanding), max(outstanding))
print(sum(outstanding))
print(sum(outstanding) / len(outstanding))      # the average

stages = [1, 2, 1, 1, 3, 2, 1]
print(stages.count(1))          # how many times 1 is in the list
print(stages.index(3))          # the index of the first 3
```

`min` and `max` work on strings too (alphabetically, session 2). `sum` only on
numbers. `index` gives a `ValueError` when the value is not in the list - test with
`in` first.

## 5. Create lists from other values

### `list()`: a list from any sequence

`list()` makes a new list from the items of any sequence (any *iterable*):

```python run
l = list()                       # the same as l = []
print(l)

point3d = (4, 0, 3)
print(list(point3d))             # from a tuple

digits = range(0, 10)
print(list(digits))              # from a range

user_name = "ada byron"
print(list(user_name))           # from a string: one item per character
```

### From text: `split`

`split()` (session 1) cuts a string into a list of strings:

```python run
row = "L000002,C0132,investment,EUR,2019-04-16,2029-04-16,1977400.00,651927.30,5.44,35,2"
fields = row.split(",")
print(len(fields), fields[2], fields[-2])

text = "some words delimited by spaces"
print(text.split())              # without an argument: by spaces
```

### Collect values in a loop: `append`

Start with an empty list and **append** a value in each iteration. It is the Python
`OUTPUT` statement: the DATA step writes a row to the output data set, `append` adds an
item to the list.

```python run
late_loans = []

with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    for line in file:
        fields = line.strip().split(",")
        if int(fields[9]) > 90:              # days_past_due
            late_loans.append(fields[0])     # loan_id

print(len(late_loans), "loans more than 90 days past due")
print(late_loans[:5], "...")
```

```sas
data late_loans;
    set loans;
    if days_past_due > 90 then output;
    keep loan_id;
run;
```

## 6. The methods of a list

### Add, remove, reverse, sort

| Method | What it does |
|---|---|
| `lst.append(x)` | adds `x` at the end |
| `lst.extend(other)` | adds all items of `other` at the end |
| `lst.insert(i, x)` | inserts `x` before the index `i` |
| `lst.pop()` | removes the last item and returns it |
| `lst.pop(i)` | removes the item at index `i` and returns it |
| `lst.remove(x)` | removes the first item equal to `x` (`ValueError` if there is none) |
| `lst.clear()` | removes all items |
| `lst.index(x)`, `lst.count(x)` | the index of the first `x`; how many `x` |
| `lst.reverse()` | reverses the list in place |
| `lst.sort()` | sorts the list in place; `sort(reverse=True)`: from the largest |
| `lst.copy()` | a new list with the same items (section 7) |
| `del lst[i]`, `del lst[i:j]` | removes an item, a slice |

```python run
fruits = ["apple", "banana", "strawberry"]

fruits.append("plum")               # at the end
print(fruits)

fruits.insert(2, "NEW")             # before the index 2
print(fruits)

item = fruits.pop()                 # remove the last item, and get it
print(item, fruits)

item = fruits.pop(2)                # remove the item at index 2
print(item, fruits)

fruits.remove("banana")             # remove by value
print(fruits)

fruits.extend(["kiwi", "lemon"])    # add several items
print(fruits)

fruits.reverse()
print(fruits)

numbers = [1, 3, 4, 2]
numbers.sort()
print(numbers)
numbers.sort(reverse=True)
print(numbers)
```

More: [More on lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)
in the tutorial.

### `append` or `extend`?

```python run
a = [1, 2]
a.append([3, 4])        # one item: the list [3, 4]
print(a, len(a))

b = [1, 2]
b.extend([3, 4])        # two items: 3 and 4
print(b, len(b))
```

### The methods change the list - and return `None`

`append`, `sort`, `reverse` and the others change the list **in place**. They return
`None`, not the list. A classic bug:

```python run
numbers = [3, 1, 2]
numbers = numbers.sort()       # wrong: sort() returns None
print(numbers)
```

::: details Answer
`numbers.sort()` sorts the list and returns `None`, and `numbers = ...` binds the
name to that `None` - the sorted list is lost. Write only `numbers.sort()`, or use
`sorted()` (next).
:::

### `sort()` or `sorted()`?

- `lst.sort()` sorts **this** list. Only lists have it.
- `sorted(x)` returns a **new**, sorted list, and does not change `x`. It works on any
  sequence: a tuple, a string, a set, a range.

```python run
names = ["Maria", "Ivan", "Asen"]
sorted_names = sorted(names)
print(names)               # not changed
print(sorted_names)
print(sorted("python"))    # the characters of a string, sorted
print(sorted(names, reverse=True))
```

Sorting compares the items with `<` (session 2): strings alphabetically - capital
letters before small ones - and a mix of numbers and strings is an error:

```python run
print(sorted(["banana", "Cherry", "apple"]))
print(sorted([3, "1", 2]))
```

`PROC SORT` and `ORDER BY` can sort by a column, or by several. In Python that is
`sorted(..., key=...)`: sessions 4 and 5.

## 7. A list is mutable: names and references

### Two names, one list

Session 1 showed that a variable is a **name** bound to an **object**. With numbers
and strings this hardly matters, because they cannot change. A list **can** change -
and then it matters a lot:

```python run
original = [1, 2, 3]
new_list = original          # not a copy: the same list has a second name

new_list[0] = 100
print(original)              # [100, 2, 3] - changed too!
print(new_list)
print(original is new_list, id(original) == id(new_list))
```

`new_list = original` does not copy anything. Both names point to **the same list
object** in memory, so a change through one name is seen through the other. `is` (and
`id()`) shows it.

::: info Animation
**Lists and references:**
[1. A list changes in place](../animations/listsAndReferences.html#1){target="_blank"},
[2. Two names, one list](../animations/listsAndReferences.html#2){target="_blank"},
[3. A copy](../animations/listsAndReferences.html#3){target="_blank"},
[4. `sort()` and `sorted()`](../animations/listsAndReferences.html#4){target="_blank"}
:::

### Make a copy

When you need an independent list, make a **copy**. Three ways give the same:

```python run
original = [1, 2, 3]

copy1 = original[:]          # a slice of everything
copy2 = original.copy()      # the copy() method
copy3 = list(original)       # list() makes a new list

copy1.append(4)
print(original, copy1, copy2, copy3)
print(original is copy1)
```

These are **shallow** copies: the new list has the same items. When the items are
lists themselves (a table as a list of rows), the rows are still shared - session 5
explains shallow and deep copies.

## 8. Tuples

### What is a tuple?

A **tuple** is an **immutable** sequence: once created, it cannot change - no item can
be added, removed or replaced.

- Good for fixed data: a record (one row of a table), a date, a pair of coordinates.
- A tuple uses a little less memory than a list, and is a little faster.
- Tuples can do everything a sequence can (section 1), but have only two methods:
  `count` and `index`.

### Create a tuple

A tuple is written in **round brackets**, with the items separated by **commas**:

```python run
t = ()
print(type(t))              # an empty tuple

t = (99,)                   # one item: note the comma!
print(type(t), t)

t = (99)                    # without the comma, it is just 99 in brackets
print(type(t), t)

point3d = (4, 0, 3)
print(point3d)

point3d = 4, 0, 3           # the brackets may be left out
print(point3d)
```

It is the **comma** that makes a tuple, not the brackets. That is why `x, y = 1, 2`
(session 1) works: the right side is a tuple.

### Read the items

```python run
address = ("Bulgaria", "Sofia", "Nezabravka str", 14)
country = address[0]
town = address[1]
print(country, town, address[-1])

ada_birth_date = (10, "December", 1815)
print(f"Ada was born on {ada_birth_date[1]} {ada_birth_date[0]}, {ada_birth_date[2]}")
```

### A tuple cannot change

```python run
address = ("Bulgaria", "Sofia", "Nezabravka str", 14)
address[0] = "France"
```

To "change" a tuple, you make a new one (the name moves to it, like with numbers):

```python run
record = ("L000001", "investment", 1)
record = record[:2] + (2,)          # a new tuple with stage 2
print(record)
```

### A list inside a tuple can change

A tuple cannot change **which objects** it holds. If one of them is a list, the list
itself can still change:

```python run
t = ([1, 2, 3], "fixed")
t[0][2] = 100              # change the list inside the tuple
print(t)
```

```python run
users = (
    ["Ivan", "Ivanov", 34],
    ["Maria", "Ivanova", 36],
)
users[0][2] = 100               # the list inside: works
print(users[0])
users[0] = ["Petar", "Petrov", 45]   # the tuple itself: TypeError
```

::: info Animation
**Lists and references:**
[5. A tuple cannot change](../animations/listsAndReferences.html#5){target="_blank"},
[6. A list inside a tuple (advanced)](../animations/listsAndReferences.html#6){target="_blank"}
:::

### Unpacking

A tuple (or a list) can be **unpacked** into several names at once - the number of
names must be the number of items:

```python run
record = ("L000002", "investment", 651927.30)

loan_id, product, outstanding = record
print(loan_id)
print(product)
print(outstanding)
```

```python run
loan_id, product = ("L000002", "investment", 651927.30)     # 2 names, 3 items
```

A name with a star `*` takes "the rest", as a list:

```python run
row = ("L000002", "C0132", "investment", "EUR", 651927.30)
loan_id, client_id, *other = row
print(loan_id, client_id, other)

first, *middle, last = [1, 2, 3, 4, 5]
print(first, middle, last)
```

`_` is the usual name for a value you do not need: `loan_id, _, product = ...`.

### Tuples as records

A list of tuples is a small **table**: each tuple is a row, each position a column.
`for` with unpacking (session 2) reads it row by row:

```python run
loans = [
    ("L000001", "investment", 1044231.30, 0),
    ("L000002", "investment", 651927.30, 35),
    ("L000003", "credit_card", 644.25, 0),
    ("L000014", "consumer", 14286.75, 200),
]

print(loans[1])             # the second row
print(loans[1][2])          # its third column
print(loans[-1][0])         # the first column of the last row

for loan_id, product, outstanding, days_past_due in loans:
    if days_past_due > 30:
        print(loan_id, product, outstanding)
```

A common use of a list of tuples - coordinates, or a value with its label - and
separating it into two lists again:

```python run
distances = [("Bansko", 97), ("Szeged", 469), ("Palermo", 987), ("Dublin", 2479)]

names = []
km = []
for name, distance in distances:
    names.append(name)
    km.append(distance)
print(names)
print(km)
```

The other way round - a **tuple of lists** - is a fixed structure of groups that can
change inside:

```python run
products = (
    ["Shirt", "Pants"],      # the names
    [20, 35],                # the quantities
)
print(f"Product: {products[0][0]}, quantity: {products[1][0]}")
products[1][0] = 100         # a quantity can change
print(products)
```

Tuples are also used for **several return values of a function** (session 4) and as
**keys of a dictionary** (session 6), where a list is not allowed.

::: details Advanced: named tuples
In a plain tuple, `loan[2]` does not say what the third column is. A **named tuple**
gives the positions names - a lightweight record:

```python run
from collections import namedtuple

Loan = namedtuple("Loan", ["loan_id", "product", "outstanding"])
loan = Loan("L000001", "investment", 1044231.30)

print(loan)
print(loan.outstanding)          # by name
print(loan[2])                   # still by position
loan_id, product, outstanding = loan
```

Classes and data classes (sessions 11 - 12) go further: records that can also check
their data and have their own methods.
:::

## 9. Lists or tuples?

| | List | Tuple |
|---|---|---|
| Brackets | `[1, 2, 3]` | `(1, 2, 3)` |
| Can change | yes: add, remove, sort | no |
| Use for | a collection that grows: the loans of a report, the values of a column | a fixed record: one row, a date, a pair |
| Memory, speed | a little more, a little slower | a little less, a little faster |

```python run
import sys

as_list = [1044231.30, 651927.30, 644.25]
as_tuple = (1044231.30, 651927.30, 644.25)
print(sys.getsizeof(as_list), "bytes for the list")
print(sys.getsizeof(as_tuple), "bytes for the tuple")
```

(The exact numbers depend on the Python version; the tuple is always smaller.)

Rule of thumb: a **list** for many values of the **same kind** (all loan ids), a
**tuple** for a few values of **different kinds** that belong together (one loan).

### Convert between them

`list()` and `tuple()` convert in both directions:

```python run
address = ("Bulgaria", "Sofia", "Nezabravka str", 14)
address = list(address)          # now it can change
address[3] = 25
print(address)

fruits = ["apple", "banana", "strawberry", "banana", "orange"]
print(tuple(fruits))
print(tuple(range(0, 10)))
print(tuple("ada byron"))
```

## 10. `range`

### Syntax

`range` gives an **immutable sequence of whole numbers**:

```text
range(stop)
range(start, stop)
range(start, stop, step)
```

- `stop` is the only required argument. The numbers end at **`stop - 1`**.
- `start` is 0 when left out; `step` is 1 when left out.
- All three must be whole numbers. `step` can be negative, but not 0 (`ValueError`).
- If the arguments give no numbers, the range is empty.

Reference: [Ranges](https://docs.python.org/3/library/stdtypes.html#ranges).

```python run
print(list(range(0, 10)))        # 0 ... 9
print(list(range(10)))           # the same
print(list(range(2, 10, 2)))     # 2, 4, 6, 8
print(list(range(9, -1, -1)))    # 9 ... 0, backwards
print(list(range(-3, 4)))        # -3 ... 3
print(list(range(9, -1, 1)))     # empty: you cannot go from 9 up to -1
```

| SAS `DO` loop | Python |
|---|---|
| `do i = 1 to 12;` | `for i in range(1, 13):` |
| `do i = 0 to 100 by 10;` | `for i in range(0, 101, 10):` |
| `do i = 10 to 1 by -1;` | `for i in range(10, 0, -1):` |

### A range does not keep its numbers

- **Immutable**: a range cannot change.
- **Small in memory**: a range keeps only `start`, `stop` and `step`, and calculates
  each number when it is needed. A range of a billion numbers is as small as a range
  of ten.
- Used mostly in `for` loops, to repeat something a given number of times.

```python run
import sys

print(sys.getsizeof(range(10)), sys.getsizeof(range(1_000_000_000)))
print(sys.getsizeof(list(range(1000))))     # a list keeps every number
```

When you print a range, you see only the "formula". To see the numbers, make a list or
a tuple of it - or loop over it:

```python run
r = range(0, 10, 2)
print(r)
print(list(r))
for i in r:
    print(i, end=" ")
```

A range is a real sequence: `len`, indexes, slices and `in` work, and fast:

```python run
r = range(0, 1_000_000, 5)
print(len(r), r[3], r[-1], 500 in r, 501 in r)
print(range(10)[:3])
```

## 11. Sets

### What is a set?

A **set** is an **unordered** collection of **unique** values - the sets of
mathematics.

- No duplicates: each value is in a set **once**.
- No order: a set has no first and no last item, and no indexes.
- The items must be **immutable** (*hashable*): numbers, strings, tuples - not lists.
- The set itself is mutable: you can add and remove items.

Sets are used to test membership, to remove duplicates, and to compare groups:
union, intersection, difference (section 12).

### Create a set

A set is written in **curly brackets**:

```python run
set_of_immutables = {"a", 1, "b", 2, 3}
print(set_of_immutables)

int_dup_numbers = {1, 2, 3, 1, 2, 4, 3, 5, 1, 2, 3}
print(int_dup_numbers)                       # the duplicates are gone
print(int_dup_numbers == {1, 2, 3, 4, 5})    # order and duplicates do not matter
```

```python run
set_of_mutables = {[1, 2, 3], ["a", "b"]}    # TypeError: a list is unhashable
```

::: warning `{}` is not an empty set
`{}` is an empty **dictionary** (session 6). An empty set is `set()`:

```python run
print(type({}), type(set()))
```
:::

### Unique values: `SELECT DISTINCT`

`set()` makes a set from any sequence - the duplicates disappear:

```python run
l1 = [1, 2, 1, 3, 2, 5, 3]
l2 = list(set(l1))
print(l2)

products = ["consumer", "mortgage", "consumer", "overdraft", "mortgage"]
print(set(products))                 # SELECT DISTINCT product
print(len(set(products)))            # COUNT(DISTINCT product)
print(sorted(set(products)))         # SELECT DISTINCT ... ORDER BY
```

On the data - the distinct products and regions:

```python run
products = set()
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    for line in file:
        products.add(line.split(",")[2])
print(len(products), sorted(products))
```

::: warning The order of a set is not kept
A set does not remember the order in which values came. Print the same set of strings
in two runs of a program, and the order can be different. When the order matters -
in a report, in a test - use `sorted(the_set)`. (To remove duplicates **and** keep the
first order: `list(dict.fromkeys(items))`, session 6.)
:::

### Add and remove

```python run
my_set = {1, 2, 3}
my_set.add(4)
print(my_set)
my_set.add(2)               # already there: nothing changes
print(my_set)

my_set.remove(2)
print(my_set)
my_set.discard(5)           # discard: no error if it is not there
print(my_set)
my_set.remove(5)            # remove: KeyError if it is not there
```

`pop()` removes and returns some item (which one is not defined), `clear()` empties the
set. `len`, `in`, `min`, `max`, `sum` and `for` work as with lists.

### Sets and dictionaries

- Both are **mutable**, and both use **curly brackets**. A set has no order; a
  dictionary keeps the order in which the keys were added (session 6).
- A dictionary is a collection of `key: value` **pairs**; a set is a collection of
  **values** only - like the keys of a dictionary without the values.

Dictionaries are the topic of session 6.

### Sets are fast for `in`

A set is a **hash table** inside: Python calculates from the value where it must be,
and looks only there. A list is searched item by item, from the start. For `in` on a
large collection, a set is much faster; for going through all items, and for access
by index, a list is better.

```python run
import time

large_list = list(range(1_000_000))
large_set = set(large_list)

start = time.perf_counter()
found = 999_999 in large_list
list_time = time.perf_counter() - start

start = time.perf_counter()
found = 999_999 in large_set
set_time = time.perf_counter() - start

print(f"in a list: {list_time:.6f} s")
print(f"in a set:  {set_time:.6f} s")
```

So when you check many values against a long list of allowed codes - a nomenclature -
put the codes into a set first.

::: details Advanced: `frozenset`
A `frozenset` is an immutable set. Because it cannot change, it can be an item of a
set, or a key of a dictionary:

```python run
pairs = {frozenset({"EUR", "USD"}), frozenset({"EUR", "BGN"})}
print(frozenset({"USD", "EUR"}) in pairs)      # the order does not matter
```
:::

## 12. Set operations: `UNION`, `INTERSECT`, `EXCEPT`

### The four operations

![Four Venn diagrams of two sets a and b: union, intersection, difference and symmetric difference, with the Python operator, the method and the SQL keyword of each](/diagrams/set-operations.svg){.diagram}

| Operation | Operator | Method | Result | SQL |
|---|---|---|---|---|
| union | `a \| b` | `a.union(b)` | in `a` or in `b` | `UNION` |
| intersection | `a & b` | `a.intersection(b)` | in both | `INTERSECT` |
| difference | `a - b` | `a.difference(b)` | in `a`, not in `b` | `EXCEPT` (older Oracle: `MINUS`) |
| symmetric difference | `a ^ b` | `a.symmetric_difference(b)` | in one of them, not in both | - |

Each operation returns a **new** set.

```python run
set1 = {1, 2, 3, 4}
set2 = {5, 4}

print(set1 | set2, set1.union(set2))
print(set1 & set2, set1.intersection(set2))
print(set1 - set2, set1.difference(set2))
print(set1 ^ set2, set1.symmetric_difference(set2))
```

The methods accept any sequence, the operators only sets:

```python run
regions = {"Sofia", "Varna"}
print(regions.union(["Ruse", "Sofia"]))
print(regions | ["Ruse", "Sofia"])          # TypeError
```

::: warning `UNION` or `UNION ALL`?
SQL `UNION` removes duplicates - that is a set union, `a | b`. `UNION ALL` keeps every
row - that is joining two lists, `list_a + list_b` (section 4).
:::

### Example: the clients of two months

The client ids with a loan at the end of August and at the end of September:

```python run
august = {"C0001", "C0002", "C0003", "C0005", "C0008"}
september = {"C0002", "C0003", "C0005", "C0013", "C0021"}

print("new:     ", sorted(september - august))      # EXCEPT
print("closed:  ", sorted(august - september))
print("stayed:  ", sorted(august & september))      # INTERSECT
print("all:     ", len(august | september))         # UNION
print("changed: ", sorted(august ^ september))      # new or closed
```

### Example: what is missing from a credit file

```python run
required = {"id_card", "income_statement", "collateral_valuation", "insurance"}
submitted = {"id_card", "insurance", "bank_statement"}

print("Received:", ", ".join(sorted(required & submitted)))
print("Missing: ", ", ".join(sorted(required - submitted)))
print("Extra:   ", ", ".join(sorted(submitted - required)))
```

`", ".join(...)` makes one string of the items, with `", "` between them (session 7).

### Subsets and checks of the data

| Test | Operator | Method |
|---|---|---|
| every item of `a` is in `b` | `a <= b` | `a.issubset(b)` |
| `b` has every item of `a` | `b >= a` | `b.issuperset(a)` |
| no common items | - | `a.isdisjoint(b)` |

These are quick checks of the data, like the checks you write in SQL before a join:

```python run
allowed_currencies = {"EUR", "USD"}

currencies = set()
loan_clients = set()
with open("data/loans.csv", encoding="utf-8") as file:
    file.readline()
    for line in file:
        fields = line.split(",")
        loan_clients.add(fields[1])
        currencies.add(fields[3])

clients = set()
with open("data/clients.csv", encoding="utf-8") as file:
    file.readline()
    for line in file:
        clients.add(line.split(",")[0])

print("only allowed currencies:", currencies <= allowed_currencies)
print("every loan has a known client:", loan_clients <= clients)
print("loans of unknown clients:", loan_clients - clients)       # LEFT JOIN ... WHERE c.client_id IS NULL
```

## 13. Practice

Open your copy of the [Homework repository](https://github.com/ivapopova-courses/Python-Data-Analysts-UniCredit-Homework)
in VS Code (before the session: [get the new tasks](/how-to#get-the-new-tasks)) and run the tasks from the
terminal, in the repository root:

```bash
python 03-lists-tuples-sets/practice/task1-predict-sequences.py
```

| Task | File | What you do |
|------|------|-------------|
| 1 | `task1-predict-sequences.py` | Predict 14 indexes, slices and operations, then check |
| 2 | `task2-slices.py` | Parts of ids and dates; quarters of a year of monthly values |
| 3 | `task3-list-methods.py` | A watch list: add, insert, remove, sort, count |
| 4 | `task4-tuples.py` | Records as tuples: unpack, read, sum; a list of tuples |
| 5 | `task5-sets.py` | The clients of two months: new, closed, stayed; a credit file |
| 6 | `task6-from-file.py` | From `loans.csv` and `clients.csv`: distinct values, lists, set checks |

## Summary

| Topic | Remember |
|-------|----------|
| Sequences | `list`, `tuple`, `range`, `str`: ordered; `len`, `in`, `+`, `*`, `min`, `max`, `count`, `index` |
| Indexes | from **0**; `-1` is the last; a wrong index is an `IndexError` |
| Slices | `s[start:stop:step]`, the stop is not included; `s[:3]` the first 3, `s[-3:]` the last 3, `s[::-1]` reversed, `s[:]` a copy |
| Lists | `[...]`, mutable; `append`, `extend`, `insert`, `pop`, `remove`, `sort`; the methods return `None` |
| Sorting | `lst.sort()` changes the list; `sorted(x)` returns a new list |
| References | `b = a` is the same list with two names; a copy: `a[:]`, `a.copy()`, `list(a)` |
| Tuples | `(...)`, immutable, the comma makes it: `(99,)`; unpacking `a, b, *rest = t`; records |
| `range` | `range(start, stop, step)`, stop not included; small in memory |
| Sets | `{...}` / `set()`, unique, unordered; `add`, `discard`; fast `in`; print with `sorted()` |
| Set operations | `\|` `UNION`, `&` `INTERSECT`, `-` `EXCEPT`, `^` symmetric difference; `<=` subset |

## Homework

1. `03-lists-tuples-sets/homework.py` (in the homework repository): a **portfolio
   snapshot** from `loans.csv` - the loans as a list of tuples, the five largest
   exposures, the distinct products, and the clients that have loans in both
   currencies. Every check must print `OK`.
2. The practice tasks you did not finish in class.
3. Optional: `names.py` asks how many names the user will enter, reads them with
   `input()` in a loop into a list, and prints them sorted, without duplicates, and
   how many were duplicates.
4. Optional: a word is a *palindrome* if it reads the same forwards and backwards,
   ignoring case (`"Racecar"`). Check it with a slice, for words typed by the user.

## Read more

- Python tutorial: [Data structures](https://docs.python.org/3/tutorial/datastructures.html)
  (lists, `del`, tuples and sequences, sets)
- Reference: [Sequence types](https://docs.python.org/3/library/stdtypes.html#sequence-types-list-tuple-range),
  [Set types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset),
  [`copy`](https://docs.python.org/3/library/copy.html)
- Real Python: [Lists and tuples](https://realpython.com/python-lists-tuples/),
  [Sets](https://realpython.com/python-sets/)

**Next session:** functions - your own `def`, parameters and return values, and why a
function is the Python version of a SAS macro.
