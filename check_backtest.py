import pandas as pd
import numpy as np

from src.backtesting.backtester import run_backtest
from src.trades import build_trade_log

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

example_trade_log = build_trade_log(example_results)

print("\n--- SYNTHETIC TRADE LOG ---")
print(example_trade_log.to_string(index=False))

# Este escenario debe generar exactamente una operación cerrada.
assert len(example_trade_log) == 1, (
    "The example must produce exactly one closed trade."
)

# Solo después de comprobarlo recuperamos esa operación.
closed_trade = example_trade_log.iloc[0]

# Sin posiciones abiertas, todo el patrimonio final es efectivo.
assert example_results["Quantity"].iloc[-1] == 0.0

portfolio_pnl = example_results["Cash"].iloc[-1] - 1000.0

np.testing.assert_allclose(
    closed_trade["Net PnL"],
    portfolio_pnl,
    rtol=0,
    atol=1e-10,
    err_msg="Trade PnL must match the portfolio cash change.",
)

# Las comisiones del registro deben coincidir con las del backtester.
np.testing.assert_allclose(
    closed_trade["Entry Fee"] + closed_trade["Exit Fee"],
    example_results["Fee"].sum(),
    rtol=0,
    atol=1e-10,
    err_msg="Trade fees must match recorded execution fees.",
)

# El retorno de esta operación se mide sobre los 1000 utilizados.
np.testing.assert_allclose(
    closed_trade["Net Return"],
    portfolio_pnl / 1000.0,
    rtol=0,
    atol=1e-12,
    err_msg="Trade return must match net PnL divided by entry outlay.",
)

print("Trade and portfolio reconciliation checks passed.")

# Resultados calculados a mano, independientes del backtester.
expected_positions = [0.0, 1.0, 1.0, 0.0]
expected_trades = [0.0, 1.0, 0.0, 1.0]

# Resultados derivados a mano para este escenario concreto.
expected_returns = np.array([
    0.0,                       # Estamos fuera del mercado.
    1.0 / (1.0 + 0.001) - 1.0, # Compramos y pagamos la entrada.
    121.0 / 110.0 - 1.0,       # Mantenemos las unidades.
    (108.9 / 121.0) * (1.0 - 0.001) - 1.0,  # Vendemos.
])
expected_equity = np.array([
    1000.0,
    999.000999000999,
    1098.901098901099,
    988.021978021978,
])

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
    atol=1e-12
)

#Reconstruimos el valor de la cartera desde sus componentes.
reconstructed_equity = (
    example_results["Cash"]
    + example_results["Quantity"] * example_results["Open"]
)

np.testing.assert_allclose(
    example_results["StrategyEquity"].to_numpy(),
    reconstructed_equity.to_numpy(),
    rtol=0,
    atol=1e-10,
    err_msg="Equity mist equal cash plus the market value of holdings.",
)

#Reconstruimos la trayectoria desde los retornos del backtester.
equity_from_returns = (
    1000.0
    * (1.0 + example_results["StrategyReturn"]).cumprod()
)

np.testing.assert_allclose(
    example_results["StrategyEquity"].to_numpy(),
    equity_from_returns.to_numpy(),
    rtol=0,
    atol=1e-10,
    err_msg="Compounded strategy returns must reconstruct equity."
)
print("Backtest accounting identities passed.")
print("\nBacktest timing and cost checks passed.")