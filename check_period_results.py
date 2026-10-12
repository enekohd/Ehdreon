from copy import deepcopy
import json

import pandas as pd

from src.experiments.results import build_period_results

dates = pd.to_datetime(["2024-01-02", "2024-01-03"])

#Valores sinteticos deliberadamente distintos para detectar mezclas
strategy_metrics = {"Final Value": 1010.0}
closed_trade_metrics = {
    "Number of Trades": 0,
    "Trade Win Rate": None,
}
benchmark_metrics = {
    "buy_hold_open_gross": {"Final Value": 1020.0},
    "buy_hold_open_entry_cost": {"Final Value": 1019.0},
}

original_inputs = deepcopy(
    (strategy_metrics, closed_trade_metrics, benchmark_metrics)
)

def build_for(index):
    return build_period_results(
        evaluation_index=index,
        strategy_metrics=strategy_metrics,
        closed_trade_metrics=closed_trade_metrics,
        benchmark_metrics=benchmark_metrics,
    )

result = build_for(dates)

assert result["period"] == {
    "start": "2024-01-02T00:00:00",
    "end": "2024-01-03T00:00:00",
    "rows": 2,
}

assert result["strategy"]["metrics"]["Final Value"] == {
    "value": 1010.0,
    "status": "finite",
}

assert result["strategy"]["closed_trade_metrics"]["Trade Win Rate"] == {
    "value": None,
    "status": "unavailable",
}

for name, expected in [
    ("buy_hold_open_gross", 1020.0),
    ("buy_hold_open_entry_cost", 1019.0),
]:
    assert result["benchmarks"][name]["metrics"]["Final Value"] == {
        "value": expected,
        "status": "finite",
    }

assert (
    strategy_metrics,
    closed_trade_metrics,
    benchmark_metrics,
) == original_inputs

assert json.loads(json.dumps(result, allow_nan=False)) == result

print("Period result structure checks passed.")

invalid_indices = [
    ("Wrong type", [1, 2], TypeError),
    ("Empty", pd.DatetimeIndex([]), ValueError),
    ("Missing date", pd.DatetimeIndex([dates[0], pd.NaT]), ValueError),
    ("Duplicate dates", pd.DatetimeIndex([dates[0], dates[0]]), ValueError),
    ("Unsorted dates", dates[::-1], ValueError),
]

for name, index, expected_error in invalid_indices:
    try:
        build_for(index)
    except expected_error:
        pass
    else:
        raise AssertionError(f"{name}: invalid index was accepted.")

print("Invalid evaluation period checks passed.")