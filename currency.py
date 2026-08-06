"""
Currency conversion helpers.
Ported from the original Tkinter expense tracker — same live-rate fetch
with an offline backup table in case the API is unavailable.
"""
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
    """Refresh rates_to_gbp from a live API. Silently falls back to the
    offline backup table above if the request fails for any reason."""
    global rates_to_gbp
    try:
        url = "https://v6.exchangerate-api.com/v6/7bafa13868250342b55efe5a/latest/USD"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            new_rates = data["rates"]
            for currency, rate in new_rates.items():
                if rate != 0:
                    rates_to_gbp[currency] = 1.0 / rate
            print("Live currency rates updated.")
    except Exception:
        print("Could not fetch live rates. Using offline backup.")


def to_gbp(amount, currency):
    currency = currency.upper().strip()
    if currency not in rates_to_gbp:
        raise ValueError("Sorry, exchange rate not available.")
    return amount * rates_to_gbp[currency]
