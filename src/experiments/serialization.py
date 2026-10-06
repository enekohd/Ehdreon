import math
import numpy as np
from datetime import datetime
import pandas as pd

def serialize_numeric_metric(value) -> dict:
    """Representa una métrica numérica como datos JSON estrictos."""

    if value is None:
        return {"value": None, "status": "unavailable"}

    # Normalizamos escalares NumPy a tipos nativos de Python.
    if isinstance(value, (np.integer, np.floating)):
        value = value.item()

    # bool hereda de int, pero no es una métrica numérica admitida.
    if isinstance(value, bool) or not isinstance(value, (int,float)):
        raise TypeError("Metric must be an integer, float or None")

    #Los enteros son finitos; conservamos su precision y su tipo
    if isinstance(value, int):
        return {"value": value, "status": "finite"}

    if math.isnan(value):
        raise ValueError("Unexpected NaN metric; investigate its origin.")

    if math.isinf(value):
        status = (
            "positive_infinity"
            if value > 0
            else "negative_infinity"
        )
        return {"value": None, "status": status}

    return {"value": value, "status": "finite"}

def serialize_metric_datetime(value) -> str | None:
    """Convierte una fecha de una métrica a ISO sin alterar su zona."""
    if value is None:
        return None

    if value is pd.NaT:
        raise ValueError("Unexpected NaT metric; investigate origin.")

    if not isinstance(value, (datetime, pd.Timestamp)):
        raise TypeError(
            "Metric datetime must be a datetime, pandas Timestamp or None."
        )

    return value.isoformat()

def serialize_metrics(metrics: dict) -> dict:
    """Prepara el diccionario actual de metricas para JSON estricto."""

    serialized = {}

    for name, value in metrics.items():
        try:
            if name == "Max Drawdown Date":
                serialized[name] = serialize_metric_datetime(value)
            else:
                serialized[name] = serialize_numeric_metric(value)
        except (TypeError, ValueError) as error:
            raise type(error)(
                f"Metric {name!r}: {error}"
            ) from error
    return serialized