from src.config import ExperimentConfig
from src.research.candidates import build_sma_candidates
from dataclasses import asdict

base_config = ExperimentConfig()
candidates = build_sma_candidates(base_config)

# 1. Hay exactamente cuatro candidatos.
assert len(candidates) == 4, (
    "Candidates must be exactly 4."
)

# 2. Las ventanas coinciden con las previstas, en el mismo orden.
actual_pairs = [
    (candidate.fast_window, candidate.slow_window)
    for candidate in candidates
]

expected_pairs = [
    (20, 100),
    (50, 100),
    (20, 200),
    (50, 200),
]

assert actual_pairs == expected_pairs, (
    "Candidate window pairs do not match the expected order."
)

# 3. Todos conservan la comisión de la configuración original.
for candidate in candidates:
    assert candidate.transaction_cost == base_config.transaction_cost, (
        "A candidate changed the base transaction cost."
    )

# 4. Construir candidatos no modifica las ventanas originales.
assert base_config.fast_window == 50, (
    "The base fast_window changed."
)

assert base_config.slow_window == 200, (
    "The base slow_window changed."
)

print("SMA candidate construction checks passed.")

#Usamos valores diferentes de los predeterminados para detectar
#si la funcion reconstruye accidentalmente una configuracion por defecto
custom_config = ExperimentConfig(
    initial_capital=2500.0,
    transaction_cost=0.002,
    validation_start="2022-01-01",
    test_start="2023-01-01",
    fast_window=10,
    slow_window=80,
    dataset_id="synthetic_candidate_test",
)

original_config_data = asdict(custom_config)
custom_candidates = build_sma_candidates(custom_config)

assert len(custom_candidates) == len(expected_pairs)

for candidate, (expected_fast, expected_slow) in zip(
    custom_candidates,
    expected_pairs,
):
    #Construimos las configuracion completa que esperamos.
    expected_config_data = original_config_data.copy()
    expected_config_data["fast_window"] = expected_fast
    expected_config_data["slow_window"] = expected_slow

    assert asdict(candidate) == expected_config_data, (
        "A candidate changed fields other than the SMA windows."
    )

#La configuracion recibida tampoco debe cambiar
assert asdict(custom_config) == original_config_data, (
    "Candidate construction modified the input configuration."
)

print("SMA candidate configuration preservation checks passed.")

unsupported_config = ExperimentConfig(
    strategy_name="another_strategy",
)

try:
    build_sma_candidates(unsupported_config)
except ValueError as error:
    assert "SMA candidates require" in str(error), (
        f"Unexpected error: {error}"
    )
else:
    raise AssertionError(
        "SMA candidates construction accepted another strategy."
    )

print("Non-SMA candidate construction correctly rejected.")