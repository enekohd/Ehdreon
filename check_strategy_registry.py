from src.strategies.registry import get_sma_definition
from src.strategies.sma_strategies import apply_sma_strategies
from src.strategies.registry import get_strategy_definition
import pandas as pd
from src.config import ExperimentConfig

definition = get_sma_definition()

assert definition["name"] == "sma_trend", (
    "The name of the strategy is incorrect."
)

assert definition["parameter_names"] == (
    "fast_window",
    "slow_window",
), "The strategy parameter names are incorrect."

assert definition["function"] is apply_sma_strategies, (
    "The registry must reference the SMA implementation."
)

print("SMA strategy definition checks passed.")

#Una consulta valida devuelve la implementacion solicitada.
registered_definition = get_strategy_definition("sma_trend")

assert registered_definition["name"] == "sma_trend"
assert registered_definition["function"] is apply_sma_strategies

#Un nombre desconocido debe crear un error explicito.
try:
    get_strategy_definition("unknown_strategy")
except ValueError as error:
    assert "Unknown strategy" in str(error), (
        f"Unexpected error : {error}"
    )
else:
    raise AssertionError("The registry accepted an unknown strategy.")

#Cada consulta devuelve un diccionario independiente.
registered_definition["description"] = "Changed by the caller."

fresh_definition = get_strategy_definition("sma_trend")

assert fresh_definition["description"] != "Changed by the caller.", (
    "Changing one definition affected a later lookup."
)

print("Strategy lookup and isolation checks passed.")

# Datos pequeños y deterministas: no necesitamos descargar precios.
prices = pd.DataFrame(
    {"Close": [100.0, 110.0, 120.0, 90.0, 80.0]},
    index=pd.date_range("2024-01-01", periods=5, freq="D"),
)

orginal_prices = prices.copy(deep=True)

#1. Ejecutamos directamenta la implementacion conocida.
direct_result = apply_sma_strategies(
    prices,
    fast_window=2,
    slow_window=3,
)

#2. Obtenemos la funcion a trave del registro y la ejecutamos.
definition = get_strategy_definition("sma_trend")
strategy_function = definition["function"]

registry_result = strategy_function(
    prices,
    fast_window=2,
    slow_window=3,
)

#3. Cambiar como encontramos la funcion no cambia el resultado.
pd.testing.assert_frame_equal(
    registry_result,
    direct_result,
)

#4. Las llamadas tampoco deben modificar los datos originales.
pd.testing.assert_frame_equal(
    prices,
    orginal_prices,
)

print("Registered strategy execution equivalence checks passed.")

#La seleccion procede de la configuracion, no de un literal en la consulta.
config = ExperimentConfig()

configured_definition = get_strategy_definition(
    config.strategy_name
)

assert configured_definition["name"] == config.strategy_name
assert configured_definition["function"] is apply_sma_strategies

#Un nombre con formato valido puede no estar registrado.
unknown_config = ExperimentConfig(
    strategy_name="unknown_strategy"
)

try:
    get_strategy_definition(unknown_config.strategy_name)
except ValueError as error:
    assert "Unknown strategy" in str(error), (
        f"Unexpected error: {error}"
    )
else:
    raise AssertionError(
        "The registry accepted an unknown configured strategy."
    )

print("Configured strategy lookup checks passed.")