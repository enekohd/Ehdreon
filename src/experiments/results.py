import pandas as pd

from src.experiments.serialization import (
    serialize_metric_datetime,
    serialize_metrics,
)

def build_period_results(
        *,
    evaluation_index: pd.DatetimeIndex,
    strategy_metrics: dict,
    closed_trade_metrics: dict,
    benchmark_metrics: dict,
) -> dict:
    """Organiza resultados ya calculados para un periodo evaluado."""

    #1. Validamos las fechas utilizadas para describir el periodo.
    if not isinstance(evaluation_index, pd.DatetimeIndex):
        raise TypeError("evaluation_index must be a DatetimeIndex.")

    if evaluation_index.empty:
        raise ValueError("The evaluaton period must not be empty.")

    if evaluation_index.isna().any():
        raise ValueError("The evaluation period contains missing dates.")

    if not evaluation_index.is_unique:
        raise ValueError("The evaluation period contains duplicate dates.")

    if not evaluation_index.is_monotonic_increasing:
        raise ValueError("The evaluation period must be chronological.")

    #2. Serializamos cada benchmark conservando su nombre.
    benchmarks = {}

    for name, metrics in benchmark_metrics.items():
        benchmarks[name] = {
            "metrics": serialize_metrics(metrics)
        }

    #3. Construimos una estructura nueva para el periodo.
    return {
        "period": {
            "start": serialize_metric_datetime(evaluation_index[0]),
            "end": serialize_metric_datetime(evaluation_index[-1]),
            "rows": len(evaluation_index)
        },
        "strategy": {
            "metrics": serialize_metrics(strategy_metrics),
            "closed_trade_metrics": serialize_metrics(closed_trade_metrics),
        },
        "benchmarks": benchmarks,
    }