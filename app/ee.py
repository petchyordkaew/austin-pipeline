"""
The actual "electrical engineering" logic lives here.

This file knows NOTHING about the web. It's just plain Python functions.
Keeping logic separate from the web layer is a habit worth having: it makes
the functions easy to test (see tests/test_ee.py) and easy to reuse.
"""

# Standard resistor color code: each color maps to a digit.
DIGITS = {
    "black": 0, "brown": 1, "red": 2, "orange": 3, "yellow": 4,
    "green": 5, "blue": 6, "violet": 7, "grey": 8, "gray": 8, "white": 9,
}

# The multiplier band: how many zeros to add (gold/silver divide instead).
MULTIPLIERS = {
    **{color: 10 ** digit for color, digit in DIGITS.items()},
    "gold": 0.1,
    "silver": 0.01,
}

# The tolerance band (last band on 4- and 5-band resistors), in percent.
TOLERANCES = {
    "brown": 1, "red": 2, "green": 0.5, "blue": 0.25,
    "violet": 0.1, "grey": 0.05, "gray": 0.05, "gold": 5, "silver": 10,
}


def resistor_from_bands(bands: list[str]) -> dict:
    """
    Decode a 4-band or 5-band resistor.

    4-band: digit, digit, multiplier, tolerance   e.g. yellow violet red gold = 4.7 kΩ ±5%
    5-band: digit, digit, digit, multiplier, tolerance
    """
    bands = [b.strip().lower() for b in bands]

    if len(bands) == 4:
        digit_bands, mult_band, tol_band = bands[:2], bands[2], bands[3]
    elif len(bands) == 5:
        digit_bands, mult_band, tol_band = bands[:3], bands[3], bands[4]
    else:
        raise ValueError("Give 4 or 5 bands.")

    try:
        digits = "".join(str(DIGITS[b]) for b in digit_bands)
        multiplier = MULTIPLIERS[mult_band]
        tolerance = TOLERANCES[tol_band]
    except KeyError as e:
        raise ValueError(f"Unknown or invalid color for that position: {e.args[0]}")

    ohms = round(int(digits) * multiplier, 4)
    return {"ohms": ohms, "pretty": pretty_ohms(ohms), "tolerance_percent": tolerance}


def pretty_ohms(ohms: float) -> str:
    """4700 -> '4.7 kΩ', 1000000 -> '1 MΩ'."""
    for limit, suffix in ((1e9, "GΩ"), (1e6, "MΩ"), (1e3, "kΩ")):
        if ohms >= limit:
            return f"{ohms / limit:g} {suffix}"
    return f"{ohms:g} Ω"


def ohms_law(v: float | None = None, i: float | None = None, r: float | None = None) -> dict:
    """V = I * R. Give any two, get the third."""
    given = [x is not None for x in (v, i, r)]
    if sum(given) != 2:
        raise ValueError("Give exactly two of v, i, r.")
    if v is None:
        v = i * r
    elif i is None:
        if r == 0:
            raise ValueError("r cannot be 0 when solving for i.")
        i = v / r
    else:
        if i == 0:
            raise ValueError("i cannot be 0 when solving for r.")
        r = v / i
    return {"v": v, "i": i, "r": r, "p": v * i}


def voltage_divider(vin: float, r1: float, r2: float) -> dict:
    """Vout = Vin * R2 / (R1 + R2)."""
    if r1 + r2 == 0:
        raise ValueError("r1 + r2 cannot be 0.")
    return {"vout": vin * r2 / (r1 + r2)}
