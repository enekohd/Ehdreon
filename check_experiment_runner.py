import numpy as np
import pandas as pd
from dataclasses import replace

from src.config import ExperimentConfig
from src.experiments.runner import run_experiment

from unittest.mock import patch

from src.strategies.registry import get_strategy_definition

#Datos sinteticos validos y faciles de calcular a mano.
dates = pd.date_range("2024-01-01", periods=9, freq="D")

prices = [
    100.0, 110.0, 120.0,
    130.0, 140.0, 150.0,
    160.0, 170.0, 180.0,
]

data = pd.DataFrame(
    {
        "Open": prices,
        "High": prices,
        "Low": prices,
        "Close": prices,
        "Volume": [1000] * len(dates),
    },
    index=dates,
)

original_data = data.copy(deep=True)

config = ExperimentConfig(
    initial_capital=1000.0,
    transaction_cost=0.0,
    validation_start="2024-01-05",
    test_start="2024-01-08",
    fast_window=2,
    slow_window=3,
)

result = run_experiment(data, config)

train = result["train"]
validation = result["validation"]
test = result["test"]

assert set(result) == {"train", "validation", "test"}

#1. Cada resultado contiene unicamente las fechas de su periodo.
assert train["backtest"].index.equals(dates[1:4])
assert validation["backtest"].index.equals(dates[4:7])
assert test["backtest"].index.equals(dates[7:])

#Al unir los resultados recuperamos todas las fechas preparadas,
#en orden y sin filas de contexto adicionales.
combined_index = (
    train["backtest"].index
    .append(validation["backtest"].index)
    .append(test["backtest"].index)
)

assert combined_index.equals(dates[1:])

#2. TRAIN genera la primera señal al cierre de su ultimo dia.
#Todavia no puede ejecutarla dentro de TRAIN.
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

#3. VALIDATION y TEST compran en su primera apertura.
# No heredan capital ni ganancias del periodo anterior.

for period, period_prices in (
    (validation, [140.0, 150.0, 160.0]),
    (test, [170.0, 180.0]),
):
    expected_trades = [1.0] + [0.0] * (len(period_prices) - 1)

    np.testing.assert_array_equal(
        period["backtest"]["Trade"].to_numpy(),
        expected_trades,
    )

    expected_equity = (
        1000.0
        * np.array(period_prices)
        / period_prices[0]
    )

    np.testing.assert_allclose(
        period["backtest"]["StrategyEquity"].to_numpy(),
        expected_equity,
        rtol=0,
        atol=1e-10,
    )

#4. Cada benchmark comienza en la primera apertura de su periodo.
for period, period_prices in (
    (train, [110.0, 120.0, 130.0]),
    (validation, [140.0, 150.0, 160.0]),
    (test, [170.0, 180.0]),
):
    expected_equity = (
        1000.0
        * np.array(period_prices)
        / period_prices[0]
    )

    for benchmark in period["benchmarks"].values():
        np.testing.assert_allclose(
            benchmark["equity"].to_numpy(),
            expected_equity,
            rtol=0,
            atol=1e-10,
        )

#5. No forzamos el cierre de las posiciones al terminar.
for period in result.values():
    assert period["trade_log"].empty

assert validation["backtest"]["Quantity"].iloc[-1] > 0
assert test["backtest"]["Quantity"].iloc[-1] > 0

#6. El runner conserva intactos los datos recibidos.
pd.testing.assert_frame_equal(data, original_data)

print("Three-period experiment runner checks passed.")

#Conservamos la configuracion valida y cambiamos unicamente el nombre.
unknown_strategy_config = replace(
    config,
    strategy_name = "unknown_strategy",
)

try:
    run_experiment(data, unknown_strategy_config)
except ValueError as error:
    assert "Unknown strategy" in str(error), (
        f"Unexpected error: {error}"
    )
else:
    raise AssertionError(
        "The runner accepted an unknown strategy."
    )

print("Experiment runner unknown strategy rejection checks passed.")

#1. Desarrollo devuelve unicamente TRAIN y VALIDATION
development_result = run_experiment(
    data,
    config,
    mode="development",
)

assert set(development_result) == {"train", "validation"}

def assert_period_results_equal(actual, expected):
    """Compara todos los componentes de dos evaluaciones"""

    pd.testing.assert_frame_equal(
        actual["backtest"],
        expected["backtest"],
    )

    pd.testing.assert_frame_equal(
        actual["trade_log"],
        expected["trade_log"],
    )

    assert actual["strategy_metrics"] == expected["strategy_metrics"]
    assert actual["trade_metrics"] == expected["trade_metrics"]

    assert set(actual["benchmarks"]) == set(expected["benchmarks"])

    for name in expected["benchmarks"]:
        actual_benchmark = actual["benchmarks"][name]
        expected_benchmark = expected["benchmarks"][name]

        pd.testing.assert_series_equal(
            actual_benchmark["returns"],
            expected_benchmark["returns"],
        )

        pd.testing.assert_series_equal(
            actual_benchmark["equity"],
            expected_benchmark["equity"],
        )

        assert(
            actual_benchmark["metrics"]
            == expected_benchmark["metrics"]
        )

#2. Los periodos comunes conservan sus resultados.
for name in ("train", "validation"):
    assert_period_results_equal(
        development_result[name],
        result[name],
    )

print("Development evaluation equivalence checks passed.")

#3. Modificar precios de TEST no cambia el desarrollo.
changed_data = data.copy(deep=True)

test_rows = changed_data.index >= config.test_start
price_columns = ["Open", "High", "Low", "Close"]

changed_data.loc[test_rows, price_columns] *= 10.0

changed_development_result = run_experiment(
    changed_data,
    config,
    mode= "development",
)

for name in ("train", "validation"):
    assert_period_results_equal(
        changed_development_result[name],
        development_result[name],
    )

#Conseramos tambien el contrato de no modificar la entrada.
pd.testing.assert_frame_equal(data, original_data)

print("Development evaluation TEST-price isolation checks passed.")

#4. Una errata en el modo no debe activar otro comportamiento.
try:
    run_experiment(data, config, mode="developmnt")
except ValueError as error:
    assert "mode must be" in str(error), (
        f"Unexpected error: {error}"
    )
else:
    raise AssertionError("The runner accepted an unkown mode.")

print("Invalid experiment mode correctly rejected.")

#Obtenemos la implementacion real antes de sustituir la consulta.
strategy_definition = get_strategy_definition(config.strategy_name)
real_strategy_function = strategy_definition["function"]

received_indexes = []

def check_strategy(strategy_data, **parameters):
    """Comprueba las fechas recibidas y ejecuta la estrategia real."""

    received_indexes.append(strategy_data.index.copy())

    assert(
        strategy_data.index < pd.Timestamp(config.test_start)
    ).all(), "Development strategy received TEST observations."

    return real_strategy_function(strategy_data, **parameters)

#Modificamos una copia de la definicion, solo para esta prueba.
checked_defintion = strategy_definition.copy()
checked_defintion["function"] = check_strategy

#Sustituimos temporalmente la consulta que utiliza el runner.
with patch(
    "src.experiments.runner.get_strategy_definition",
    return_value = checked_defintion,
):
    checked_result = run_experiment(
        data,
        config,
        mode="development",
    )

assert len(received_indexes) == 1, (
    "The strategy must be called exaclty once."
)

assert set(checked_result) == {"train", "validation"}

print("Development strategy input boundary checks passed.")