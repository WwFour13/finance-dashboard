"""
Currency conversion helpers.
Ported from the original Tkinter expense tracker — same live-rate fetch
with an offline backup table in case the API is unavailable.
"""
import math

import requests

SUPPORTED_CURRENCIES = ["GBP", "USD", "EUR", "INR", "JPY", "CAD", "AUD", "CHF"]

# Backup exchange rates (1 unit of currency -> GBP), used if the live API call fails
rates_to_gbp = {
    "GBP": 1.0,
    "USD": 1 / 1.323,
    "EUR": 1 / 1.142,
    "INR": 1 / 118.25,
    "JPY": 1 / 173.50,
    "CAD": 1 / 1.71,
    "AUD": 1 / 1.90,
    "CHF": 1 / 1.17,
}


def fetch_live_rates():
    """Refresh rates_to_gbp from the USD-based live API, retaining the
    offline backup table if the request fails or returns invalid data."""
    global rates_to_gbp
    try:
        url = "https://v6.exchangerate-api.com/v6/7bafa13868250342b55efe5a/latest/USD"
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        conversion_rates = data["conversion_rates"]
        gbp_rate = conversion_rates["GBP"]
        if not isinstance(gbp_rate, (int, float)) or not math.isfinite(gbp_rate) or gbp_rate <= 0:
            raise ValueError("Invalid GBP rate in API response.")

        new_rates = {
            code: gbp_rate / rate
            for code, rate in conversion_rates.items()
            if isinstance(rate, (int, float)) and math.isfinite(rate) and rate > 0
        }
        rates_to_gbp = new_rates
        print("Live currency rates updated.")
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        print(f"Could not fetch live rates ({exc}). Using offline backup.")


def to_gbp(amount, currency):
    currency = currency.upper().strip()
    if currency not in rates_to_gbp:
        raise ValueError("Sorry, exchange rate not available.")
    return amount * rates_to_gbp[currency]
