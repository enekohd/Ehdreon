import numpy as np
import pandas as pd

from src.backtesting.benchmarks import calculate_buy_hold


dates = pd.to_datetime([
    "2024-01-02",
    "2024-01-03",
    "2024-01-04",
])

open_prices = pd.Series(
    [100.0, 110.0, 99.0],
    index=dates,
)

# Conservamos los precios para comprobar que la función no los modifica.
original_prices = open_prices.copy()

#LLamadas a calculate_buy_hold

gross_returns, gross_equity = calculate_buy_hold(
    open_prices,
    initial_capital=1000.0
)

net_returns, net_equity = calculate_buy_hold(
    open_prices,
    initial_capital=1000.0,
    entry_cost=0.001,
)

np.testing.assert_allclose(
    gross_returns.to_numpy(),
    [0.0, 0.10, -0.10],
    rtol=0,
    atol=1e-12,
)

np.testing.assert_allclose(
    net_returns.to_numpy(),
    [-0.001, 0.10, -0.10],
    rtol=0,
    atol=1e-12,
)

np.testing.assert_allclose(
    gross_equity.to_numpy(),
    [1000.0, 1100.0, 990.0],
    rtol=0,
    atol=1e-8,
)

np.testing.assert_allclose(
    net_equity.to_numpy(),
    [999.0, 1098.90, 989.01],
    rtol=0,
    atol=1e-8,
)

pd.testing.assert_series_equal(open_prices, original_prices)

print("Buy & Hold benchmark checks passed.")