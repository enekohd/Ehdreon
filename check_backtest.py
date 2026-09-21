import pandas as pd
import numpy as np

from src.backtesting.backtester import run_backtest

# Fechas de las cuatro sesiones de nuestro ejemplo.
dates = pd.to_datetime([
    "2024-01-02",
    "2024-01-03",
    "2024-01-04",
    "2024-01-05",
])

# Proporcionamos directamente precios y señales.
# Así comprobamos el backtester sin depender de la estrategia SMA.
example_data = pd.DataFrame(
    {
      "Open": [100.0, 110.0, 121.0, 108.90],
        "Signal": [1, 1, 0, 0],  
    },
    index=dates,
)

#Hacemos el backtest
example_results = run_backtest(
    example_data,
    initial_capital=1000, 
    transaction_cost=0.001
)

print(example_results.to_string())

# Resultados calculados a mano, independientes del backtester.
expected_positions = [0.0, 1.0, 1.0, 0.0]
expected_trades = [0.0, 1.0, 0.0, 1.0]

expected_returns = [0.0, -0.001, 0.10, -0.101]
expected_equity = [1000.0, 999.0, 1098.90, 987.9111]

np.testing.assert_equal(
    example_results["Position"].to_numpy(),
    expected_positions
)

np.testing.assert_equal(
    example_results["Trade"].to_numpy(),
    expected_trades
)

np.testing.assert_allclose(
    example_results["StrategyReturn"].to_numpy(),
    expected_returns,
    rtol=0,
    atol=1e-12
)

np.testing.assert_allclose(
    example_results["StrategyEquity"].to_numpy(),
    expected_equity,
    rtol=0,
    atol=1e-8
)

print("\nBacktest timing and cost checks passed.")