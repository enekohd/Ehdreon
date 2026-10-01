from src.config import ExperimentConfig
from dataclasses import FrozenInstanceError

config = ExperimentConfig()

alternative_config = ExperimentConfig(fast_window=20)

assert config.initial_capital == 10000.0
assert config.fast_window == 50
assert config.slow_window == 200

assert alternative_config.fast_window == 20
assert alternative_config.slow_window == 200

#Crear una configuracion alternativa no cambia la original.
assert config.fast_window == 50

print(config)
print(alternative_config)
print("Configuration defaults and overrides checks passed.")

#Una configuracion creada no debe permitir reasignar parametros.
try:
    config.fast_window = 10
except FrozenInstanceError:
    print("Configuration mutation correctly rejected.")
else:
    raise AssertionError("Configuration allowed a parameter change.")

#Cada escenario introduce un unico defecto.
invalid_cases = [
    ({"initial_capital": 0}, ValueError, "initial_capital"),
    ({"transaction_cost": float("nan")}, ValueError, "transaction_cost"),
    ({"transaction_cost": 1.0}, ValueError, "transaction_cost"),
    ({"fast_window": 2.5}, TypeError, "fast_window"),
    ({"fast_window": True}, TypeError, "fast_window"),
    ({"fast_window": 200}, ValueError, "fast_window"),
    ({"split_date": "2024-02-30"}, ValueError, "split_date"),
    ({"dataset_id": ""}, ValueError, "dataset_id"),
    ({"dataset_id": "../another_dataset"}, ValueError, "dataset_id"),
    ({"dataset_id": 123}, TypeError, "dataset_id"),
]

for overrides, expected_error, expected_message in invalid_cases:
    try:
        ExperimentConfig(**overrides)
    except expected_error as error:
        assert expected_message in str(error), (
            f"Unexpected error message: {error}"
        )
    else:
        raise AssertionError(
            f"Invalid configuration was accepted: {overrides}"
        )
print("Configuration validation checks passed.")
