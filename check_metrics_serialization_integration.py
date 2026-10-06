from copy import deepcopy
import json

import pandas as pd

from src.metrics import calculate_metrics
from src.experiments.serialization import serialize_metrics

#Trayectoria sencilla calulable a mano:
# 1000 -> 1100 -> 990
dates = pd.date_range("2024-01-02", periods=3, freq="D")
returns = pd.Series([0.0, 0.10, -0.10], index=dates)
equity = 1000.0 * (1.0 + returns).cumprod()

metrics = calculate_metrics(
    equity,
    returns,
    initial_capital=1000.0,
)

original_metrics = deepcopy(metrics)
serialized = serialize_metrics(metrics)

#No debemos modificar los resultados del calculo.
assert metrics == original_metrics, (
    "Serialization must not modify the original metrics."
)

#Maximo anterior: 1100. Valor final: 990.
#Drawdown = (990 - 1100) / 1100 = -0.10.
drawdown = serialized["Max Drawdown"]

assert drawdown["status"] == "finite"
assert abs(drawdown["value"] - (-0.10)) < 1e-12

assert serialized["Max Drawdown Date"] == "2024-01-04T00:00:00"

#No proporcinamos posiciones: exposicion no disponible, no cero.
assert serialized["Exposure"] == {
    "value": None,
    "status": "unavailable",
}

#Todo el diccionario debe ser compatible con JSON estricto.
encoded = json.dumps(serialized, allow_nan=False)
assert json.loads(encoded) == serialized

print("Calculated metrics serialization checks passed.")

#Un error debe identificar la metrica que lo causa.
try:
    serialize_metrics({"Sharpe Ratio": float("nan")})
except ValueError as error:
    assert "Sharpe Ratio" in str(error), (
        "The error must identify the invalid metric."
    )
else:
    raise AssertionError("Unexpected NaN was accepted.")

print("Metric error context passed.")