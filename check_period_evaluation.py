import numpy as np
import pandas as pd

from src.config import ExperimentConfig
from src.experiments.runner import evaluate_period

dates = pd.date_range("2024-01-01", periods=3, freq="D")

data = pd.DataFrame(
    {
        "Open": [100.0, 110.0, 121.0],
        "Signal": [1, 1, 1],
    },
    index=dates,
)

original_data = data.copy(deep=True)

result = evaluate_period(
    data,
    evaluation_index=dates[1:],
    config=ExperimentConfig(
        initial_capital=1000.0,
        transaction_cost=0.0,
    ),
)

assert result["backtest"].index.equals(dates[1:])

# 1. Compramos a 110: no ganamos la subida desde el contexto.
np.testing.assert_allclose(
    result["backtest"]["StrategyEquity"].to_numpy(),
    [1000.0, 1100.0],
    rtol=0,
    atol=1e-10,
)

np.testing.assert_allclose(
    result["benchmarks"]["buy_hold_open_gross"]["equity"].to_numpy(),
    [1000.0, 1100.0],
    rtol=0,
    atol=1e-10,
)

assert result["backtest"]["Trade"].sum() == 1
assert result["trade_log"].empty
assert result["trade_metrics"]["Number of Trades"] == 0

pd.testing.assert_frame_equal(data, original_data)

print("Period evaluation context and input preservation checks passed.")

# 2. Con contexto y comision: entrada en 110, valoracion posterior en 121.
cost = 0.001

net_result = evaluate_period(
    data,
    evaluation_index=dates[1:],
    config=ExperimentConfig(
        initial_capital=1000.0,
        transaction_cost=cost,
    ),
)

#Se reserva la comision dentro del capital disponible.
expected_entry_equity = 1000.0 / (1.0 + cost)
expected_final_equity = expected_entry_equity * 121.0 / 110.0

np.testing.assert_allclose(
    net_result["backtest"]["StrategyEquity"].to_numpy(),
    [expected_entry_equity, expected_final_equity],
    rtol=0,
    atol=1e-10,
)

#Aqui estrategia y benchamrk compran en la misma apertura
# y mantienen la posicion, pagando la misma comision de entrada.
np.testing.assert_allclose(
    net_result["benchmarks"]["buy_hold_open_entry_cost"]["equity"].to_numpy(),
    net_result["backtest"]["StrategyEquity"].to_numpy(),
    rtol=0,
    atol=1e-10,
)

print("Period evaluation entry cost checks passed.")

#3. Sin contexto: la estrategia empieza en efectivo.
full_result = evaluate_period(
    data,
    evaluation_index=dates,
    config=ExperimentConfig(
        initial_capital=1000.0,
        transaction_cost=0.0,
    )
)

np.testing.assert_allclose(
    full_result["backtest"]["StrategyEquity"].to_numpy(),
    [1000.0,1000.0,1100.0],
    rtol=0,
    atol=1e-10,
)

print("Period evaluation without context checks passed.")

#4. Selecciones temporales que incumplen el contrato.
invalid_indices = [
    ("Empty period", dates[:0]),
    ("Single observation", dates[:1]),
    ("Internal gap", dates[[0, 2]]),
    ("Truncated end", dates[:2]),
    ("Unsorted dates", dates[::-1]),
]

for name, index in invalid_indices:
    try:
        evaluate_period(
            data,
            evaluation_index=index,
            config=ExperimentConfig(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            f"{name}: invalid evaluation period was accepted."
        )

#Comprobamos que ninguna de las llamadas modifico la entrada.
pd.testing.assert_frame_equal(data, original_data)

print("Invalid period selection checks passed.")