import re
from chat_helper import chat_loop

# Each unit: (kind, how many BASE units it holds). Bases: metre, gram, millilitre.
UNITS = {
    "km": ("length", 1000), "m": ("length", 1), "cm": ("length", 0.01),
    "mile": ("length", 1609.344), "foot": ("length", 0.3048), "inch": ("length", 0.0254),
    "kg": ("weight", 1000), "g": ("weight", 1),
    "pound": ("weight", 453.59237), "ounce": ("weight", 28.349523125),
    "litre": ("volume", 1000), "ml": ("volume", 1),
}

TEMPERATURES = {"c", "f", "k"}

ALIASES = {
    "kilometer": "km", "kilometers": "km", "kilometre": "km", "kilometres": "km",
    "meter": "m", "meters": "m", "metre": "m", "metres": "m",
    "miles": "mile", "feet": "foot", "ft": "foot", "inches": "inch",
    "kilogram": "kg", "kilograms": "kg", "grams": "g",
    "pounds": "pound", "lb": "pound", "lbs": "pound", "ounces": "ounce", "oz": "ounce",
    "litres": "litre", "liter": "litre", "liters": "litre", "l": "litre",
    "celsius": "c", "fahrenheit": "f", "kelvin": "k",
}

# SAMPLE exchange rates: how many rupees one unit costs. NOT real, live rates.
SAMPLE_RATES_INR = {"INR": 1.0, "USD": 83.0, "EUR": 90.0, "GBP": 105.0, "JPY": 0.55}

def canonical(name):
    name = name.lower()
    return ALIASES.get(name, name)

def pretty(number):
    return f"{number:,.4f}".rstrip("0").rstrip(".")

def convert_units(value, from_unit, to_unit):
    a, b = canonical(from_unit), canonical(to_unit)

    if a in TEMPERATURES and b in TEMPERATURES:
        celsius = {"c": value, "f": (value - 32) * 5 / 9, "k": value - 273.15}[a]
        result = {"c": celsius, "f": celsius * 9 / 5 + 32, "k": celsius + 273.15}[b]
        return f"{pretty(value)} {a.upper()} = {pretty(result)} {b.upper()}"

    if a not in UNITS or b not in UNITS:
        raise ValueError(f"I do not know the unit '{from_unit if a not in UNITS else to_unit}'")

    kind_a, size_a = UNITS[a]
    kind_b, size_b = UNITS[b]
    if kind_a != kind_b:
        raise ValueError(f"Cannot convert {kind_a} to {kind_b}")

    result = value * size_a / size_b          # go through the base unit
    return f"{pretty(value)} {a} = {pretty(result)} {b}"

def convert_currency(amount, from_code, to_code):
    a, b = from_code.upper(), to_code.upper()
    if a not in SAMPLE_RATES_INR or b not in SAMPLE_RATES_INR:
        raise ValueError(f"I have no sample rate for {a} or {b}")
    result = amount * SAMPLE_RATES_INR[a] / SAMPLE_RATES_INR[b]
    return f"{pretty(amount)} {a} = {pretty(result)} {b} (sample rates)"

TOOLS = {"convert_units": convert_units, "convert_currency": convert_currency}

HELP = "Try: 'convert 5 km to miles', '100 c to f', '2 kg in pounds', '50 usd to inr'"

def converter_brain(goal, history):
    if history:
        return {"action": "finish", "answer": history[-1]["result"]}

    match = re.match(r"(?:convert\s+)?(-?\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(?:to|in)\s+([a-zA-Z]+)\s*$",
                     goal.strip(), re.IGNORECASE)
    if not match:
        return {"action": "finish", "answer": HELP}

    value, from_unit, to_unit = float(match.group(1)), match.group(2), match.group(3)

    if from_unit.upper() in SAMPLE_RATES_INR and to_unit.upper() in SAMPLE_RATES_INR:
        return {"action": "convert_currency",
                "input": {"amount": value, "from_code": from_unit, "to_code": to_unit}}

    return {"action": "convert_units",
            "input": {"value": value, "from_unit": from_unit, "to_unit": to_unit}}

if __name__ == "__main__":
    chat_loop(converter_brain, TOOLS, "Unit and currency converter agent")
