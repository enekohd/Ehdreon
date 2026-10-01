from dataclasses import dataclass

import math
from datetime import date

@dataclass(frozen=True)
class ExperimentConfig:
    """Parametros del experimento SMA actual."""

    initial_capital: float = 10000.0
    transaction_cost: float = 0.001
    split_date: str = "2024-01-01"
    fast_window: int = 50
    slow_window: int = 200
    dataset_id: str = "SPY_2020-01-01_2026-01-01_snapshot"

    def __post_init__(self):
        #1. Capital y comision: comprobar tipos y despues valores
        for name in ("initial_capital", "transaction_cost"):
            value = getattr(self, name)

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number.")

            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite.")

        if self.initial_capital <= 0:
            raise ValueError("initial_capital must be greater than zero.")

        if not 0 <= self.transaction_cost < 1:
            raise ValueError("transaction_cost must be in (0,1)")

        #2. Ventanas: enteros positivos y orden coherente.
        for name in( "fast_window", "slow_window"):
            value = getattr(self,name)

            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer.")

            if value <= 0:
                raise ValueError(f"{name} must be greater than zero.")

        if self.fast_window >= self.slow_window:
            raise ValueError("fast_window must be smaller than slow_window.")

        #3. Fecha: texto, fecha existente y formato canonico.
        if not isinstance(self.split_date, str):
            raise TypeError("split_date must be a string.")

        try:
            parsed_date = date.fromisoformat(self.split_date)
        except ValueError as error:
            raise ValueError(
                "split_date must be a valid date in YYYY-MM-DD format."
            ) from error
        if parsed_date.isoformat() != self.split_date:
            raise ValueError("split_date must use YYYY-MM-DD format.")

        #4. Identificador simple, no una ruta de archivos.
        if not isinstance(self.dataset_id, str):
            raise TypeError("dataset_id must be a string.")

        allowed_characters = (
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789_-"
        )

        if (
            not self.dataset_id
            or any(character not in allowed_characters for character in self.dataset_id)
        ):
            raise ValueError(
                "dataset_id must contain only letters, digits, underscores or hyphens."
            )