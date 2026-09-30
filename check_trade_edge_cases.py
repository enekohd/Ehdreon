import pandas as pd

from src.backtesting.backtester import run_backtest
from src.trades import build_trade_log, calculate_trade_metrics

dates = pd.date_range("2024-01-02", periods=3, freq="D")

scenarios = [
    ("No entries", [0,0,0], 0),
    ("Position remains open", [1,1,1], 1),
]

for name, signals, expected_orders in scenarios:
    data = pd.DataFrame(
        {
            "Open": [100.0, 110.0, 121.0],
            "Signal": signals,
        },
        index=dates,
    )

    results = run_backtest(
        data,
        initial_capital=1000.0,
        transaction_cost=0.001,
    )

    trade_log = build_trade_log(results)
    metrics = calculate_trade_metrics(trade_log)


    assert trade_log.empty, (
        f"{name}: no closed trades were expected."
    )

    assert "Net Return" in trade_log.columns, (
        f"{name}: the empty log must preserve its columns."
    )

    assert results["Trade"].sum() == expected_orders, (
        f"{name}: unexpected number of orders."
    )

    assert metrics["Number of Trades"] == 0

    for metric_name, value in metrics.items():
        if metric_name != "Number of Trades":
            assert value is None, (
                f"{name}: {metric_name} must be unavailable."
            )
    print(f"{name}: checks passed.")