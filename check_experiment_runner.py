import numpy as np
import pandas as pd

from src.config import ExperimentConfig
from src.experiments.runner import run_experiment

#Datos sinteticos validos y faciles de calcular a mano.
dates = pd.date_range("2024-01-01", periods=7, freq="D")
prices = [100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0]

data = pd.DataFrame(
    {
        "Open": prices,
        "High": prices,
        "Low": prices,
        "Close": prices,
        "Volume": [1000] * 7,
    },
    index=dates,
)

original_data = data.copy(deep=True)

config = ExperimentConfig(
    initial_capital=1000.0,
    transaction_cost=0.0,
    split_date="2024-01-05",
    fast_window=2,
    slow_window=3,
)

result = run_experiment(data, config)

train = result["train"]
test = result["test"]

assert set(result) == {"train", "test"}

#La primera fila original se elimina durante la preparacion.
assert train["backtest"].index.equals(dates[1:4])
assert test["backtest"].index.equals(dates[4:])

assert train["backtest"].index.intersection(
    test["backtest"].index
).empty

#La señal aparece a cierre del ultimo dia de TRAIN.
#Todavia no existe una apertura posterior dentro de TRAIN para ejecutarla.
np.testing.assert_array_equal(
    train["backtest"]["Position"].to_numpy(),
    [0.0, 0.0, 0.0],
)

np.testing.assert_allclose(
    train["backtest"]["StrategyEquity"].to_numpy(),
    [1000.0, 1000.0, 1000.0],
    rtol=0,
    atol=1e-10,
)

#TEST compra a 140 utilizando la señal anterior.
#No gana la subida desde 130 a 140.
np.testing.assert_array_equal(
    test["backtest"]["Trade"].to_numpy(),
    [1.0, 0.0, 0.0],
)

np.testing.assert_allclose(
    test["backtest"]["StrategyEquity"].to_numpy(),
    [
        1000.0,
        1000.0 * 150.0 / 140.0,
        1000.0 * 160.0 / 140.0,
    ],
    rtol=0,
    atol=1e-10,
)

#Cada benchmark compra en la primera apertura de su propio periodo.
for period, expected_prices in (
    (train, [110.0, 120.0, 130.0]),
    (test, [140.0, 150.0, 160.0]),
):
    expected_equity = (
        1000.0
        * np.array(expected_prices)
        / expected_prices[0]
    )

    for benchmark in period["benchmarks"].values():
        np.testing.assert_allclose(
            benchmark["equity"].to_numpy(),
            expected_equity,
            rtol=0,
            atol=1e-10,
        )

#No hay ninguna operacion cerrada: TEST mantiene su posicion.
assert train["trade_log"].empty
assert test["trade_log"].empty
assert test["backtest"]["Quantity"].iloc[-1] > 0

pd.testing.assert_frame_equal(data, original_data)

print("Experiment runner preparation and temproal boundary checks passed.")