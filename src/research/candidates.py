from dataclasses import replace

from src.config import ExperimentConfig

def build_sma_candidates(
    base_config: ExperimentConfig,
) -> list[ExperimentConfig]:
    """Construye cuatro configuraciones SMA sin ejecutar experimentos."""

    if base_config.strategy_name != "sma_trend":
        raise ValueError(
            "SMA candidates require strategy_name = 'sma_trend'."
        )

    window_pairs = (
        (20, 100),
        (50, 100),
        (20, 200),
        (50, 200),
    )

    candidates = []

    for fast_window, slow_window in window_pairs:
        candidate = replace(
            base_config,
            fast_window=fast_window,
            slow_window=slow_window,
        )

        candidates.append(candidate)

    return candidates