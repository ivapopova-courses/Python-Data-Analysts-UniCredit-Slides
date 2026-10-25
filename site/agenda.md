---
title: Agenda
outline: [2, 3]
---

# Agenda

**16 sessions of 4 academic hours**, 64 academic hours in total, on Mondays and
Wednesdays, 10:00 - 13:00 (two 10-minute breaks).

**Goal:** a smooth move to Python as the main tool for the same daily work with
data that you now do in SQL and SAS: reporting, modelling and ad-hoc analysis.

**How we work:** a lot of practice. Every topic is connected
to what you already know from SQL and SAS. All examples and tasks use made-up
data in the shape of the data you work with (a loan portfolio: clients, loans,
a rating scale) - never real data.

## Sessions

The dates are planned and may change.

|  | Date | Topic |
|---|---|---|
| 1 | Mon 26.10 | [Introduction, syntax, data types and variables](/lectures/01-intro-syntax-types) |
| 2 | Wed 28.10 | [Conditional statements and loops](/lectures/02-conditions-and-loops) |
| 3 | Mon 02.11 | [Lists (basics), tuples and sets](/lectures/03-lists-tuples-sets) |
| 4 | Wed 04.11 | [Functions](/lectures/04-functions) |
| 5 | Mon 09.11 | [Lists (advanced)](/lectures/05-lists-advanced) |
| 6 | Wed 11.11 | [Dictionaries](/lectures/06-dictionaries) |
| 7 | Mon 16.11 | [Text processing](/lectures/07-text-processing) |
| 8 | Wed 18.11 | [Regular expressions](/lectures/08-regular-expressions) |
| 9 | Mon 23.11 | [Error handling and file handling](/lectures/09-errors-and-files) |
| 10 | Wed 25.11 | [Modules, packages, Git and GitHub](/lectures/10-modules-and-git) |
| 11 | Mon 30.11 | [OOP: first steps, classes and objects](/lectures/11-oop-classes) |
| 12 | Wed 02.12 | [OOP in practice: nomenclatures](/lectures/12-oop-nomenclatures) |
| 13 | Mon 07.12 | [Working with databases](/lectures/13-databases) |
| 14 | Wed 09.12 | [NumPy and introduction to pandas](/lectures/14-numpy-pandas-intro) |
| 15 | Mon 14.12 | [pandas: selection, aggregation, joins](/lectures/15-pandas-select-aggregate-join) |
| 16 | Wed 16.12 | [pandas: reports](/lectures/16-pandas-reports-project) and the [final project](/project) |

## Session details

### 1. Introduction, syntax, data types and variables

- Python next to SQL and SAS: what each one is used for.
- Working with VS Code and Jupyter notebooks.
- `int`, `float`, `str`, `bool`, `None`; converting between types; operators.
- f-strings; `Decimal` for money values.

### 2. Conditional statements and loops

- `if` / `elif` / `else`, logical operators, `match`.
- `for`, `range`, `while`, `break` / `continue`.
- The Python version of `CASE WHEN` and of the loops in a DATA step.
- Tasks: sorting clients into risk classes.

### 3. Lists (basics), tuples and sets

- Creating lists, indexing, slicing, the methods of `list`.
- Tuples as records that cannot change.
- Sets for unique values, and set operations like `UNION` / `INTERSECT` / `EXCEPT`.

### 4. Functions

- `def`, parameters and default values, `*args` / `**kwargs`, `return`.
- Scope of variables, docstrings, type hints, `lambda`.
- Functions instead of SAS macros.

### 5. Lists (advanced)

- List comprehensions; `sorted` with `key`; `min` / `max`.
- `zip`, `enumerate`, `map`, `filter`.
- Nested lists: a table as a list of rows; copies and references.

### 6. Dictionaries

- Working with `dict`, looping over it, nested dictionaries, dict comprehensions.
- `defaultdict`, `Counter`.
- Grouping and aggregating by hand (`GROUP BY` without pandas).
- Lookup tables and nomenclatures.

### 7. Text processing

- The methods of `str`: `split` / `join`, `strip`, `replace`, formatting.
- Cleaning text data: names, codes, identifiers.
- Dates from text with `datetime`.

### 8. Regular expressions

- The `re` module: patterns, groups, `search` / `findall` / `sub` / `split`.
- Validating IBANs, company ids (EIK), e-mails and dates; extracting values from
  free text.
- The Python version of `PRXMATCH` (SAS) and `LIKE` / `REGEXP` (SQL).

### 9. Error handling and file handling

- `try` / `except` / `else` / `finally`, kinds of exceptions, `raise`, your own
  exceptions.
- `pathlib`, `with open`; text, CSV, JSON and Excel files.
- Handling bad records while loading data.

### 10. Modules, packages, Git and GitHub

- `import`, your own modules, the standard library (`datetime`, `collections`,
  `statistics`, `os`).
- `pip` and virtual environments; the structure of a project.
- Git: `commit`, `branch`, `merge`, `.gitignore`. GitHub: `clone`, `push`, `pull`,
  pull requests.

### 11. OOP: first steps, classes and objects

- Class and object, `__init__`, attributes, methods, `self`.
- `__str__` / `__repr__`; class attributes; `property`; dataclasses.

### 12. OOP in practice: nomenclatures

- A nomenclature as a class: data, metadata, validation rules and processing
  methods.
- `classmethod` and `staticmethod`; inheritance and composition.
- Applying one nomenclature the same way to different datasets.

### 13. Working with databases

- DB-API and `sqlite3`: connection, cursor, parameterised queries, transactions.
- SQLAlchemy engine; the result of a query straight into a DataFrame.
- Drivers for Oracle / MS SQL / PostgreSQL (overview).

### 14. NumPy and introduction to pandas

- `ndarray`, vector operations, broadcasting, aggregates, `np.where`.
- `Series` and `DataFrame`; reading CSV and Excel files.
- `head`, `info`, `describe`, the types of the columns.

### 15. pandas: selection, aggregation, joins

- `loc` / `iloc`, boolean masks, `query`, new columns.
- `groupby` / `agg` (like `GROUP BY` and `PROC MEANS`).
- `merge` / `concat` (like `JOIN` and `MERGE` in a DATA step); missing values.

### 16. pandas: reports and final project

- `pivot_table`, `melt`, dates and time series, export to Excel with several
  sheets.
- [Final project](/project): load data from a file and a database, nomenclatures
  as classes, cleaning, aggregation and a finished report.
