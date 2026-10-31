from datetime import date

import pandas as pd

def split_temporal_data(
        data: pd.DataFrame,
        *,
        validation_start: str,
        test_start: str,
) -> dict[str,pd.DataFrame]:

    """Divide datos diarios en TRAIN, VALIDATION y TEST.
    No añade contexto ni modifica la enrada.
    Requiere tres particiones no vacias.
    """

    if not isinstance(data.index, pd.DatetimeIndex):
        raise TypeError("Data must have a DatetimeIndex.")

    if data.empty:
        raise ValueError("Data must not be empty.")

    if data.index.tz is not None:
        raise ValueError("this splitter requires timezone-naive dates.")

    if data.index.isna().any():
        raise ValueError("Dates must not be missing")

    if not data.index.is_unique:
        raise ValueError("Dates must be unique.")

    if not data.index.is_monotonic_increasing:
        raise ValueError("Dates must be chronological.")

    #Interpretamos y validamos los dos limites.
    boundaries = {}

    for name, value in (
        ("validation_start", validation_start),
        ("test_start", test_start),
    ):
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string.")

        try:
            parsed_date = date.fromisoformat(value)
        except ValueError as error:
            raise ValueError(
                f"{name} must be a valid YYYY-MM-DD date."
            ) from error

        if parsed_date.isoformat() != value:
            raise ValueError(f"{name} must use YYYY-MM-DD format.")

        boundaries[name] = pd.Timestamp(parsed_date)

    validation_boundary = boundaries["validation_start"]
    test_boundary = boundaries["test_start"]

    if validation_boundary >= test_boundary:
        raise ValueError("validation_start must precede test_start.")

    #Cada observacion pertenece a exactamente un intervalo.
    partitions = {
        "train": data.loc[
            data.index < validation_boundary
        ].copy(),
        "validation": data.loc[
            (data.index >= validation_boundary)
            & (data.index < test_boundary)
        ].copy(),
        "test": data.loc[
            data.index >= test_boundary
        ].copy(),
    }

    for name, partition in partitions.items():
        if partition.empty:
            raise ValueError(f"The {name} partition is empty.")

    return partitions