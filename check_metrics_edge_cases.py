import pandas as pd

from src.backtesting.backtester import run_backtest
from src.metrics import calculate_metrics

#El mercado cambia, pero nuestra estrategia permanece fuera.
dates = pd.date_range("2024-01-02", periods=3, freq="D")

data = pd.DataFrame({
    "Open": [100.0, 110.0, 99.0],
    "Signal": [0,0,0],
    },
    index= dates
)

results = run_backtest(
    data,
    initial_capital=1000.0,
    transaction_cost=0.001,
)

metrics = calculate_metrics(
    results["StrategyEquity"],
    results["StrategyReturn"],
    results["Position"],
    results["Trade"],
    initial_capital=1000.0,
)

assert metrics["Initial Value"] == 1000.0
assert metrics["Final Value"] == 1000.0

zero_metrics = [
    "CAGR",
    "Annualized Return",
    "Annualized Volatility",
    "Max Drawdown",
    "Positive Days",
    "Negative Days",
    "Exposure",
    "Number of orders",
]

for name in zero_metrics:
    assert metrics[name] == 0,(
        f"{name}: expevted zero, got {metrics[name]}"
    )

unavailable_metrics = [
    "Sharpe Ratio",
    "Max Drawdown Date",
    "Positive Day Ratio",
    "Average positive returns",
    "Average negative returns",
]

for name in unavailable_metrics:
    assert metrics[name] is None,(
        f"{name}: expected None, got {metrics[name]}."
    )

print("Cash-only portfolio metrics checks passed.")

scenarios = [
    (
        "Only negative active returns",
        [0.0, -0.01, -0.02],
        0.0,
        None,
        -0.015,
    ),
    (
        "Only positive active returns",
        [0.0, 0.01, 0.02],
        1.0,
        0.015,
        None,
    ),
]

for (
    name,
    return_values,
    expected_positive_ratio,
    expected_average_positive,
    expected_average_negative,
) in scenarios:
    scenario_returns = pd.Series(return_values, index=dates)

    scenario_equity = (
        1000.0 * (1.0 + scenario_returns).cumprod()
    )
    scenario_metrics = calculate_metrics(
        scenario_equity,
        scenario_returns,
        initial_capital=1000.0,
    )

    assert(
        scenario_metrics["Positive Day Ratio"] == expected_positive_ratio
    ), f"{name}: incorrect positive-day ratio."

    expected_averages = {
        "Average positive returns": expected_average_positive,
        "Average negative returns": expected_average_negative,
    }

    for metric_name, expected in expected_averages.items():
        actual = scenario_metrics[metric_name]

        if expected is None:
            assert actual is None, (
                f"{name}: {metric_name} must be unavailable."
            )
        else:
            assert actual is not None, (
                f"{name}: {metric_name} must be available."
            )
            assert abs(actual - expected) < 1e-12, (
                f"{name}: unexpected {metric_name}: {actual}."
            )
    print(f"{name}: checks passed.")