from pathlib import Path

import pandas as pd

from src.data.validation import validate_market_data
from src.data.integrity import verify_snapshot_integrity


def load_market_data(path: Path, metadata_path: Path) -> pd.DataFrame:
    """Carga una instantánea OHLCV y verifica su integridad y validez.

    Comprueba la huella SHA-256 registrada en los metadatos,
    reconstruye Date como índice temporal y valida los datos.
    """

    if not path.is_file():
        raise FileNotFoundError(
        f"Market data snapshot not found: {path}"
    )

    verify_snapshot_integrity(path, metadata_path)

    data = pd.read_csv(
        path,
        index_col="Date",
        parse_dates=["Date"],
    )

    validate_market_data(data)

    return data