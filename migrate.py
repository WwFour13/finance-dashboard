"""
One-time migration: reads the old expenses.txt (pipe-delimited, from the
Tkinter version) and imports every valid row into the new SQLite database.
Old rows have no category, so they're imported as 'Uncategorized' — you
can re-edit them later once there's an edit route, or just start fresh
in the new app and keep this file as a historical import.

Usage:
    python migrate.py [path/to/expenses.txt]

Safe to re-run: it will just insert duplicate rows if run twice, so only
run it once against a fresh expenses.db.
"""
import sys
from datetime import datetime
import models

DEFAULT_SOURCE = "expenses.txt"


def parse_line(line):
    parts = line.strip().split("|")
    if len(parts) != 5:
        return None
    date_val, description, amount, currency, gbp = parts
    try:
        amount_val = float(amount)
        gbp_val = float(gbp)
    except ValueError:
        return None
    return {
        "date": date_val,
        "description": description,
        "amount": amount_val,
        "currency": currency,
        "gbp": gbp_val,
    }


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SOURCE
    models.init_db()

    imported = 0
    skipped = 0

    try:
        with open(source, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                parsed = parse_line(line)
                if parsed is None:
                    print(f"  Skipping malformed line {line_num}: {line.strip()!r}")
                    skipped += 1
                    continue
                # old dates were already stored as ISO (YYYY-MM-DD) by convert_date()
                models.add_expense(
                    iso_date=parsed["date"],
                    description=parsed["description"],
                    category="Uncategorized",
                    amount=parsed["amount"],
                    currency=parsed["currency"],
                    gbp=parsed["gbp"],
                )
                imported += 1
    except FileNotFoundError:
        print(f"No file found at '{source}'. Nothing to migrate — starting with an empty database.")
        return

    print(f"\nDone. Imported {imported} expenses, skipped {skipped} malformed lines.")
    print(f"Migrated at {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
