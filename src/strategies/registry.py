from src.strategies.sma_strategies import apply_sma_strategies

def get_sma_definition() -> dict:
    """Devuelve la descripcion y la funcion ejecutable de SMA."""

    return {
        "name": "sma_trend",
        "version": "1",
        "family": "trend_following",
        "description": (
            "Mantiene una señal long cuando la media movil simple"
            " rapida supera a la lenta; en caso contrario, permanece"
            " con señal de efectivo."
        ),
        "parameter_names": ("fast_window", "slow_window"),
        "function": apply_sma_strategies,
    }

def get_strategy_definition(name: str) -> dict:
    """Devuelve una definicion nueva de la estrategia solicitada."""

    definition_builders = {
        "sma_trend" : get_sma_definition,
    }

    if name not in definition_builders:
        raise ValueError(f"Unknown strategy: {name!r}")

    builder = definition_builders[name]

    return builder()
