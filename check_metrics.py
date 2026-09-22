import pandas as pd

from src.metrics import calculate_metrics

#convierte las cadenas en fechas
dates = pd.to_datetime([
    "2024-01-02",
    "2024-01-03",
    "2024-01-04",
])

#construye una columna de valores asociada a un indice
equity = pd.Series(
    [990.0,980.0,1020.0],
    index = dates
)

returns = pd.Series(
    [
        990.0/1000.0-1,
        980.0/1000.0-1,
        1020.0/1000.0-1,
    ],
    index = dates
)

metrics = calculate_metrics(
    equity,
    returns,
    initial_capital=1000.0,
)

#Comprobamos los resultados esperados
assert metrics["Initial Value"] == 1000.0
assert metrics["Final Value"] == 1020.0

assert abs(metrics["Max Drawdown"] - (-0.02)) < 1e-12

assert metrics["Max Drawdown Date"] == dates[1]

print("Capital and drawdown checks passed.")