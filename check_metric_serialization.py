import json
import numpy as np

from src.experiments.serialization import serialize_numeric_metric

from datetime import datetime

import pandas as pd

from src.experiments.serialization import serialize_metric_datetime

#1. Entradas validas y resultados esperados independientes
valid_cases = [
    ("Zero", 0.0, {"value": 0.0, "status": "finite"}),
    ("Integer", 3, {"value": 3, "status": "finite"}),
    ("Negative return", -0.025, {"value": -0.025, "status": "finite"}),
    ("Unavailable", None, {"value": None, "status": "unavailable"}),
    (
        "Positive infinity",
        float("inf"),
        {"value": None, "status": "positive_infinity"},
    ),
    (
        "Negative infinity",
        float("-inf"),
        {"value": None, "status": "negative_infinity"},
    ),
    ("NumPy integer", np.int64(3), {"value": 3, "status": "finite"}),
    ("NumPy float", np.float64(0.25), {"value": 0.25, "status": "finite"}),
]

for name, value, expected in valid_cases:
    actual = serialize_numeric_metric(value)

    assert actual == expected, (
        f"{name}: expected {expected}, got {actual}"
    )

    #El resultado debe poder escribirse como JSON estandar.
    encoded = json.dumps(actual, allow_nan=False)
    decoded = json.loads(encoded)

    assert decoded == expected, (
        f"{name}: the JSON round trip changed the result."
    )

print("Valid metric serialization checks passed.")

#2. Los contadores NumPy deben convertirse en enteros de python.
integer_result = serialize_numeric_metric(np.int64(3))

assert type(integer_result["value"]) is int, (
    "A NumPy integer must become a Python integer."
)

#3. Entradas que deben rechazarse.
invalid_cases = [
    ("Python NaN", float("nan"), ValueError),
    ("NumPy NaN", np.float64("nan"), ValueError),
    ("Boolean True", True, TypeError),
    ("Boolean False", False, TypeError),
    ("NumPy boolean", np.bool_(True), TypeError),
    ("Numeric string", "0.25", TypeError),
    ("List", [0.25], TypeError),
    ("Dictionary", {"value": 0.25}, TypeError),
]

for name, value, expected_error in invalid_cases:
    try:
        serialize_numeric_metric(value)
    except expected_error:
        pass
    else:
        raise AssertionError(
            f"{name}: expected {expected_error.__name__}"
        )
print("Invalid metric rejection checks passed.")

#4. Fechas validas: conserver fecha, hora y zona cuando exista.
valid_datetime_cases = [
    (
        "Naive pandas timestamp",
        pd.Timestamp("2025-04-07"),
        "2025-04-07T00:00:00",
    ),
    (
        "UTC pandas timestamp",
        pd.Timestamp("2025-04-07", tz="UTC"),
        "2025-04-07T00:00:00+00:00",
    ),
    (
        "Python datetime",
        datetime(2025, 4, 7, 12, 30),
        "2025-04-07T12:30:00",
    ),
    ("Unavailable date", None, None),
]

for name, value, expected in valid_datetime_cases:
    actual = serialize_metric_datetime(value)

    assert actual == expected, (
        f"{name}: expected {expected}, got {actual}."
    )

    #El texto o None deben sobrevivir a la conversion JSON.
    encoded = json.dumps(actual, allow_nan=False)

    assert json.loads(encoded) == expected, (
        f"{name}: the JSON round trip changed the result."
    )
print("Valid metric datetime serialization checks passed.")

#5. Fechas ausentes inesperadas y tipos no admitidos.
invalid_datetime_cases = [
    ("Missing timestamp", pd.NaT, ValueError),
    ("Date string", "2025-04-07", TypeError),
    ("Number", 123, TypeError),
]

for name, value, expected_error in invalid_datetime_cases:
    try:
        serialize_metric_datetime(value)
    except expected_error:
        pass
    else:
        raise AssertionError(
            f"{name}: expected {expected_error.__name__}."
        )
print("Invalid metric datetime rejection checks passed.")
