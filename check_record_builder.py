from src.config import ExperimentConfig
from src.experiments.records import build_experiment_record, attach_experiment_results
from datetime import datetime, timedelta
from uuid import UUID
from copy import deepcopy


custom_config = ExperimentConfig(fast_window=20)

code_info = {
    "commit": "test-commit",
    "working_tree_dirty": False,
}

environment_info = {
    "python_version": "test-version",
    "dependencies": {},
}

conventions = {
    "conventions_version": 1,
    "execution": {
        "execution_time": "next_session_open",
    },
}

built_record = build_experiment_record(
    custom_config,
    dataset_sha256="test-hash",
    code_info=code_info,
    environment_info=environment_info,
    conventions=conventions,
)

#Compruebo que la ventana guardada es 20
assert built_record["config"]["fast_window"] == 20,(
    "The recorded window is not the expected."
)

#Compruebo que el id coincide
assert built_record["dataset"]["dataset_id"] == custom_config.dataset_id, (
    "The id does not match."
)

#Compruebo qeu el hash guardado es "test-hash"
assert built_record["dataset"]["sha256"] == "test-hash", (
    "The recorded hash must match the supplied hash."

)

#Compruebo que los dict de code y environment son iguales que los que le pase
assert built_record["code"] == code_info,(
    "The code dict changed."
)
assert built_record["environment"] == environment_info,(
    "The environment dict changed."
)

#Compruebo que las conventions son iguales que las que le paso
assert built_record["conventions"] == conventions, (
    "The record must preserve the supplied conventions."
)

#Compruebo que el schema_version == 2
assert built_record["schema_version"] == 2, (
    "New experiment records must use schema version 2."
)

parsed_id = UUID(built_record["experiment_id"])
parsed_created_at = datetime.fromisoformat(built_record["created_at"])

#Compruebo que el uuid tiene la version 4
assert parsed_id.version == 4, (
    "The experiment id version of the UUID should be 4."
)

#Compruebo que la fecha tiene desplazamiento UTC igual a timedelta(0).
assert parsed_created_at.utcoffset() == timedelta(0), (
    "The timezone utc is incorrect."
)

#Compruebo que una segunda llamada al constructor con los mismos datos genera
# ids diferentes
built_record_2 = build_experiment_record(
    custom_config,
    dataset_sha256="test-hash",
    code_info=code_info,
    environment_info=environment_info,
    conventions=conventions
)

assert built_record["experiment_id"] != built_record_2["experiment_id"],(
    "Separate records must have different experiment IDs."
)

assert built_record["config"] == built_record_2["config"], (
    "The configuration information of the two calls should be equal."
)
print("Experiment record identity checks passed.")

code_info["commit"] = "changed-after-building"
environment_info["dependencies"]["test-library"] = "0.0.0"

#Compruebo que el commit del registro no ha cambiado
assert built_record["code"]["commit"] == "test-commit", (
    "Changing input code metadata must not alter the built record."
)

#Compruebo que las conventions no cambian despues de haberlas construido.
conventions["execution"]["execution_time"] = "changed-after-building"

assert (
    built_record["conventions"]["execution"]["execution_time"]
    == "next_session_open"
), "Changing input conventions must not alter the built record."

#Compruebo que no se ha añadido test-library a las dependencias
assert "test-library" not in built_record["environment"]["dependencies"], (
    "Changing input code metadata must not alter the built record."
)

print("Experiment record input isolation checks passed.")

print("Experiment record builder checks passed.")

sample_results = {
    "train": {
        "strategy": {
            "metrics": {
                "Final Value": {
                    "value": 1010.0,
                    "status": "finite",
                },
            },
        },
    },
}

completed_record = attach_experiment_results(
    built_record,
    sample_results,
)

assert "results" not in built_record, (
    "The experiment record may not receive results."
)

assert completed_record["experiment_id"] == built_record["experiment_id"],(
    "The id does not match."
)

assert completed_record["results"] == sample_results, (
    "The incorporated results are not the same as sample_results."
)

sample_results["train"]["strategy"]["metrics"]["Final Value"]["value"] = 999.0

assert completed_record["results"]["train"]["strategy"]["metrics"]["Final Value"]["value"] == 1010.0, (
    "Attaching results must not modify the original record."
)

#Conservamos una copia para comprobar que el rechazo no modifica nada.
before_attempt = deepcopy(completed_record)

try:
    attach_experiment_results(completed_record, sample_results)
except ValueError as error:
    assert "already contains results" in str(error), (
        f"Unexpected error: {error}"
    )
else:
    raise AssertionError(
        "A record qith existing results was accepted."
    )

assert completed_record == before_attempt, (
    "A rejected attachment must not modify the existing record."
)

print("Experiment result attachment checks passed.")