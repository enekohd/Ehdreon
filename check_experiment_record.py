from src.config import ExperimentConfig
import json
from pathlib import Path

from src.data.integrity import (
    calculate_sha256,
    verify_snapshot_integrity,
)

from tempfile import TemporaryDirectory
from src.experiments.records import (
    build_experiment_record,
    save_experiment_record,
)

from src.experiments.provenance import (
    collect_code_info,
    collect_environment_info,
)

from src.experiments.conventions import build_experiment_conventions

config = ExperimentConfig()

project_root = Path(__file__).resolve().parent

snapshot_path = (
    project_root
    / "data"
    / "raw"
    / f"{config.dataset_id}.csv"
)

metadata_path = (
    project_root
    / "data"
    / "metadata"
    / f"{config.dataset_id}.json"
)

verify_snapshot_integrity(snapshot_path,metadata_path)
print("Matching snapshot accepted.")

calculated_sha256 = calculate_sha256(snapshot_path)

code_info = collect_code_info(project_root)

environment_info = collect_environment_info()

assert set(environment_info) == {
    "python_version",
    "dependencies",
}, "Unexpected environment metadata fields."

assert isinstance(environment_info["python_version"], str)
assert environment_info["python_version"], (
    "Python version must not be empty."
)

dependencies = environment_info["dependencies"]

assert isinstance(dependencies, dict)
assert set(dependencies) == {"numpy", "pandas"}, (
    "Unexpected dependencies in the minimal environment record."
)

for package_name, package_version in dependencies.items():
    assert isinstance(package_version, str), (
        f"{package_name}: version must be a string."
    )
    assert package_version, (
        f"{package_name}: version must not be empty."
    )

print("Environment metadata contract checks passed.")

experiment_record = build_experiment_record(
    config,
    dataset_sha256=calculated_sha256,
    code_info=code_info,
    environment_info=environment_info,
    conventions=build_experiment_conventions(config),
)

record_json = json.dumps(
    experiment_record,
    indent=2,
    allow_nan=False,
)

print(record_json)

#Interpretamos el texto JSON y recuperamos un diccionario.
restored_json = json.loads(record_json)

#Comparamos todo el contenido con el regisro original.
assert experiment_record == restored_json , (
    "The two dictionaries must be equal."
)

# Comprobamos que el indicador de cambios locales conserva el tipo booleano.
assert isinstance(restored_json["code"]["working_tree_dirty"], bool), (
    "The working tree dirty must remain boolean."
)

assert (restored_json["code"]["working_tree_dirty"]
        == experiment_record["code"]["working_tree_dirty"]
), "working_tree_dirty changed during the JSON round trip."

#Recuperamos datos, no una instancia de ExperimentConfig.
assert isinstance(restored_json["config"], dict), (
    "The config section must be a dictionary."
)

print("Experiment record JSON round-trip checks passed.")

with TemporaryDirectory() as temporary_directory:
    temporary_path = Path(temporary_directory)

    experiment_path = temporary_path / "experiment.json"

    save_experiment_record(experiment_record,experiment_path)

    with experiment_path.open("r", encoding="utf-8") as file:
        loaded_record = json.load(file)

    assert experiment_record == loaded_record, (
        "The two dictionaries must be equal."
    )

    try:
        with experiment_path.open("x", encoding="utf-8") as file:
            save_experiment_record(
                {"unexpected": "replacement"},
                experiment_path,
            )

    except FileExistsError:
        print("Existing experiment record correctly protected.")

    else:
        raise AssertionError(
            "The exclusive creation allowed an existing file to be opened."
        )

    # Consultamos el estado del archivo después del intento.
    with experiment_path.open("r", encoding="utf-8") as file:
        record_after_atempt = json.load(file)

    assert experiment_record == record_after_atempt, (
        "The existing record changed after the overwrite attempt."
    )

    invalid_path = temporary_path / "invalid_experiment.json"
    invalid_record = {"metric": float("nan")}

    # Precondición: el escenario comienza sin archivo.
    assert not invalid_path.exists(), (
        "The test destination must not exist before saving."
    )

    try:
        save_experiment_record(invalid_record,invalid_path)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "An invalid record has been accepted."
        )

   # Postcondición: el fallo no debe dejar un archivo creado.
    assert not invalid_path.exists(), (
        "Serialization failure must not create a file."
    )
    print("Invalid record rejected without creating a file.")

print("Experiment record file round-trip checks passed.")