import numpy as np
import pandas as pd


def validate_market_data(data: pd.DataFrame) -> None:
    """Comprueba la estructura y los valores de datos OHLCV diarios.

    Requiere una tabla no vacía con fechas únicas y ordenadas,
    columnas OHLCV numéricas, valores finitos, precios positivos,
    volumen no negativo y precios OHLC coherentes.

    No modifica los datos.

    Lanza TypeError o ValueError si alguna comprobación falla.
    """

    if data.empty:
        raise ValueError("The market data snapshot is empty.")

    required_columns = {"Open", "High", "Low", "Close", "Volume"}
    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if not isinstance(data.index, pd.DatetimeIndex):
        raise TypeError("The snapshot index must be a DatetimeIndex.")

    if data.index.isna().any():
        raise ValueError("The snapshot contains missing dates.")

    if not data.index.is_unique:
        raise ValueError("The snapshot contains duplicate dates.")

    if not data.index.is_monotonic_increasing:
        raise ValueError("The snapshot dates must be sorted chronologically.")

    price_columns = ["Open", "High" , "Low", "Close"]
    numeric_columns = price_columns + ["Volume"]
    numeric_data = data[numeric_columns]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(data[column]):
            raise TypeError(
                f"Column {column} must contain numeric values."
            )

    if not np.isfinite(numeric_data.to_numpy()).all():
        raise ValueError(
            "Prices and volume must not contain missing or infinite values."
        )

    if (data[price_columns] <= 0).any().any():
        raise ValueError("All prices must be greater than zero.")

    if (data["Volume"] < 0).any():
        raise ValueError("Volume must not be negative.")

    invalid_ohlc = (
        (data["High"] < data["Low"])
        | (data["Open"] < data["Low"])
        | (data["Open"] > data["High"])
        | (data["Close"] < data["Low"])
        | (data["Close"] > data["High"])
    )

    if invalid_ohlc.any():
        invalid_dates = data.index[invalid_ohlc]

        raise ValueError(
            "Inconsistent OHLC prices. "
            f"First affected dates: {invalid_dates[:5].tolist()}"
        )