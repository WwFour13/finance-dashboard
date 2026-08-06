from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import date
import models
import currency

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-if-deployed"  # fine for a resume project; swap for an env var if you deploy

models.init_db()
currency.fetch_live_rates()


@app.route("/")
def dashboard():
    breakdown = models.get_category_breakdown()
    trend = models.get_monthly_trend(months_back=6)
    recent = models.get_recent(limit=8)
    all_time_total = models.get_all_time_total()

    this_month = date.today().strftime("%Y-%m")
    year, month = date.today().year, date.today().month
    prev_month_num = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    last_month = f"{prev_year}-{prev_month_num:02d}"

    this_month_total = models.get_month_total(this_month)
    last_month_total = models.get_month_total(last_month)

    if last_month_total > 0:
        delta_pct = ((this_month_total - last_month_total) / last_month_total) * 100
    else:
        delta_pct = None

    return render_template(
        "dashboard.html",
        breakdown=breakdown,
        trend=trend,
        recent=recent,
        all_time_total=all_time_total,
        this_month_total=this_month_total,
        last_month_total=last_month_total,
        delta_pct=delta_pct,
    )


@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "Other")
        currency_code = request.form.get("currency", "GBP")
        amount_str = request.form.get("amount", "").strip()
        date_str = request.form.get("date", "").strip()

        error = None
        if not description:
            error = "Description can't be empty."
        else:
            try:
                amount = float(amount_str)
            except ValueError:
                error = "Invalid input. Please enter numbers only."

        if not error:
            try:
                iso_date = models.convert_date(date_str)
            except ValueError as e:
                error = str(e)

        if not error:
            try:
                gbp_val = currency.to_gbp(amount, currency_code)
            except ValueError as e:
                error = str(e)

        if error:
            flash(error, "error")
            return render_template(
                "add.html",
                categories=models.CATEGORIES,
                currencies=currency.SUPPORTED_CURRENCIES,
                today=date.today().strftime("%d/%m/%Y"),
                form=request.form,
            )

        models.add_expense(iso_date, description, category, amount, currency_code, gbp_val)
        flash(f"Saved: {description} — £{gbp_val:.2f}", "success")
        return redirect(url_for("add_expense"))

    return render_template(
        "add.html",
        categories=models.CATEGORIES,
        currencies=currency.SUPPORTED_CURRENCIES,
        today=date.today().strftime("%d/%m/%Y"),
        form={},
    )


@app.route("/api/convert", methods=["POST"])
def api_convert():
    """AJAX endpoint used by the 'Preview conversion' button on the add-expense form."""
    data = request.get_json(force=True)
    try:
        amount = float(data.get("amount"))
        currency_code = data.get("currency", "GBP")
        gbp = currency.to_gbp(amount, currency_code)
        return jsonify({"ok": True, "gbp": round(gbp, 2)})
    except (TypeError, ValueError) as e:
        return jsonify({"ok": False, "error": str(e) or "Invalid amount."}), 400


@app.route("/expenses")
def view_expenses():
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    category = request.args.get("category", "All")

    rows = models.get_expenses(start=start or None, end=end or None, category=category)
    total = sum(r["gbp"] for r in rows)

    return render_template(
        "expenses.html",
        rows=rows,
        total=total,
        categories=["All"] + models.CATEGORIES + ["Uncategorized"],
        start=start,
        end=end,
        selected_category=category,
    )


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    models.delete_expense(expense_id)
    flash("Entry deleted.", "success")
    # send the user back to wherever they clicked delete from
    return redirect(request.referrer or url_for("view_expenses"))


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
