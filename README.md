# Personal Finance Analytics Dashboard

A full-stack Flask expense tracker with a SQLite backend, multi-currency support,
and category/trend analytics — evolved from an earlier Tkinter desktop prototype.

## Features
- Add expenses in currencies with live exchange-rate conversion to GBP (falls back to
  offline backup rates if the API is unreachable)
- SQLite-backed storage (replaces the original flat-file storage)
- Dashboard with category breakdown (doughnut chart) and 6-month spending trend (line chart)
- Month-over-month spend comparison
- Filterable transaction ledger (by date range and category)

## Setup

```bash
pip install -r requirements.txt
python migrate.py          # optional: imports data from an old expenses.txt, if you have one
python app.py
```

Then open http://127.0.0.1:5000

## Migrating old data
If you have an `expenses.txt` from the original Tkinter version, run:

```bash
python migrate.py path/to/expenses.txt
```

Old entries are imported with `category = "Uncategorized"` since the original app didn't
track categories.

## Project structure
```
app.py          - Flask routes
models.py       - SQLite schema + queries
currency.py     - live exchange rate fetching + conversion (ported from the original app)
migrate.py      - one-time importer for old expenses.txt data
templates/      - Jinja2 templates
static/css/     - stylesheet
```

## Notes for talking about this in an interview
- **Why SQLite over the original flat text file:** structured queries (category totals,
  monthly aggregation via `strftime`) instead of loading everything into memory and
  filtering in Python.
- **Why Flask over Tkinter:** it's deployable (Render/Railway free tier) and shareable via
  a link, which a desktop app isn't.
- **Data integrity carried over:** the malformed-line handling from the original app
  (skip corrupted rows, don't crash) is preserved in `migrate.py`.
- **Currency conversion:** live API call with a hardcoded offline fallback table, so the
  app degrades gracefully instead of failing if the exchange-rate API is down or rate-limited.
