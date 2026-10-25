# Final project

In the last two sessions (15 and 16) you build one complete process, of the kind
you now do in SAS or SQL: **the monthly portfolio report**. It runs for any month end
of the history, from the raw data to one Excel file, and it can be run again next
month without changes.

1. **Load** the data from files (CSV, Excel) and from a database (SQLite).
2. **Validate** it with nomenclatures written as classes (session 12): codes that
   do not exist, values out of range, missing values.
3. **Clean and transform** it with pandas: types, dates, new columns.
4. **Aggregate**: groups, pivot tables, joins.
5. **Report**: an Excel file with several sheets, and a chart.
6. **Keep the code in Git**, as a script that can be run again on new data.

Each lecture adds a part that the project reuses: functions (4), dictionaries as
lookup tables (6), text cleaning and regular expressions (7, 8), reading files
and handling bad records (9), modules and Git (10), classes (11, 12), databases
(13) and pandas (14 - 16). The homework of session 16 is the first part of the
project.

## The task

Write `report.py`. Run as

```bash
python report.py 2026-09-30
```

it writes `out/portfolio_report_2026-09-30.xlsx` and `out/portfolio_2026-09-30.png`,
and prints a short summary with the checks. With `2026-08-31` (or any month end from
2025-10-31 to 2026-09-30) it makes the report of that month.

## The data

All in `data/` of the homework repository ([the sample data](./sample-data)):

| Source | What you take from it |
|---|---|
| `portfolio.db` (SQLite) | the tables `clients`, `loans` (the client of each loan, product, currency, dates), `rating_scale`, `ratings_history` - with SQL and parameters (session 13) |
| `balances_monthly.csv` | the outstanding and the days past due of each loan at each month end |
| `client_register.csv` | the names, EIKs, IBANs and cities of the clients (messy text - sessions 7, 8) |
| `fx_rates.xlsx` | the EUR exchange rates of each working day, one sheet per month (sessions 9, 14) |
| `regions_bg.csv` | the region codes and names (cp1251 - session 7) |

## The steps

### 1. Load

- From the database: the clients, the loans, the rating scale, and the ratings of
  the report date **and** of the previous month end - the date as a **parameter** of
  the query, never pasted into the SQL text.
- From `balances_monthly.csv`: the rows of the report date (and all months up to it,
  for the trend).
- From `fx_rates.xlsx`: the EUR / USD rate of the last working day on or before the
  report date (all sheets; `n/a` if the month is not in the file).
- From `client_register.csv`: the register, for the data quality checks.

### 2. Validate

Use your module `homework_nomenclature.py` of session 12 (copy it next to
`report.py`). At least:

- **codes**: product, segment, region and rating - every value must be in its
  nomenclature;
- **values out of range**: outstanding below 0 or above the amount, days past due
  below 0, an interest rate outside 0 - 30, a maturity date before the start date;
- **missing values**: a loan without a client or a client without a rating at the
  report date;
- **the register** (sessions 7, 8): ids that are not in the clients table after
  cleaning, EIKs and IBANs with a wrong shape.

Every failed check is one row of a **rejects** table: the dataset, the id, the
column, the value, the reason. A row that fails is reported, never dropped
silently. The report says how many rows were rejected; the loans that pass go on.

The sample data is mostly clean, so most checks find nothing. Test each check: make
a copy of a table, break it on purpose (a product `leasing`, a negative balance, a
client id `C9999`) and see that the row appears in the rejects.

### 3. Transform

One DataFrame with a row per loan at the report date: the loan, its balance and days
past due, the client's segment and region, the rating and grade, the PD (the middle
of the band), the EL (PD x LGD x outstanding, LGD 0.45 - a parameter), the DPD
bucket (`current`, `1-30`, `31-90`, `90+`), and the age of the loan in months.

### 4. Aggregate

The tables of the report:

| Sheet | Content |
|---|---|
| `summary` | report date, number of loans and clients, outstanding, EL, EL / outstanding, the share of 90+, the EUR / USD rate, the number of rejected rows |
| `segment x dpd` | outstanding by segment and DPD bucket, with totals |
| `segment x grade` | outstanding by segment and grade, the grades in the order of the scale |
| `migration` | the rating migration matrix: previous month end -> report date, all ratings |
| `trend` | loans and outstanding for every month end up to the report date, with the change from the previous month |
| `top clients` | the 10 largest clients: id, name (from the register), segment, grade, outstanding, share of the portfolio |
| `rejects` | the table of step 2 |
| `data quality` | per dataset and column: rows, missing values, rejected values |

### 5. Report

- One Excel file with the sheets above (`pd.ExcelWriter`, session 16): readable
  widths, a number format for the amounts, a title row on the summary.
- One chart (PNG): the monthly outstanding (trend), or the outstanding by segment
  and DPD bucket.
- The script prints the checks (next section) at the end.

### 6. Git

The project lives in a folder `project/` of your copy of the homework repository
(session 10): `report.py`, `homework_nomenclature.py`, any other module of yours, a
`README.md` (what the report does, how to run it, what each sheet means). `out/` is
not committed. Commit after each step that works - the history should show the
steps.

## The checks your report must pass

For the report date **2026-09-30** (the numbers of sessions 4, 6, 13 and 15):

- 400 loans, 143 clients with loans, outstanding **131,370,708.60**;
- EL with LGD 0.45: **1,140,106.56**;
- outstanding by segment: corporate 93,087,049.89, retail 6,837,600.42, sme
  31,446,058.29;
- the migration matrix August -> September: 150 clients, 10 downgrades;
- the totals of every table = the total of the data (no rows lost or doubled in a
  join).

For **2026-08-31**: outstanding 133,492,549.54 and EL 1,093,088.84.

## Checklist

- [ ] `python report.py 2026-09-30` runs from a fresh terminal, in the virtual
      environment, without errors.
- [ ] Another month end works without a change in the code.
- [ ] No date, path or LGD is written inside the functions: they are parameters (or
      constants at the top of the file).
- [ ] The SQL uses parameters (`?` or `:name`).
- [ ] The nomenclatures are objects of your classes of session 12.
- [ ] Every rejected row is in the `rejects` sheet, with its reason.
- [ ] The checks above are printed and agree.
- [ ] Every function has a docstring; the steps are functions (load, validate,
      transform, aggregate, write) called from `main()`.
- [ ] `README.md` explains how to run it.
- [ ] The history in Git shows the steps (several commits, clear messages).

## Ideas for more

- The rejects and the data quality sheet with colours (Self-study of session 16).
- The check digits of the EIKs and the IBANs (Self-study of session 8).
- The report of all month ends in one run (a loop over `pd.date_range(freq="ME")`),
  and one sheet that compares them.
- The loans in USD shown in EUR with the rate of the report date (take the
  amounts of the sample data as amounts in the loan's currency).
- A command-line option for the LGD (`argparse`, Self-study of session 10).
