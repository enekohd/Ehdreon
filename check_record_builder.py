from src.config import ExperimentConfig
from src.experiments.records import build_experiment_record
from datetime import datetime, timedelta
from uuid import UUID


custom_config = ExperimentConfig(fast_window=20)

code_info = {
    "commit": "test-commit",
    "working_tree_dirty": False,
}

environment_info = {
    "python_version": "test-version",
    "dependencies": {},
}

built_record = build_experiment_record(
    custom_config,
    dataset_sha256="test-hash",
    code_info=code_info,
    environment_info=environment_info,
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

#Compruebo que el schema_version == 1
assert built_record["schema_version"] == 1, (
    "Schema version is not equal to one."
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

#Compruebo que una segunda llamada al constructor con los mismos dartos genera
# ids diferentes
built_record_2 = build_experiment_record(
    custom_config,
    dataset_sha256="test-hash",
    code_info=code_info,
    environment_info=environment_info,
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

#Compruebo que el commir del registro no ha cambiado
assert built_record["code"]["commit"] == "test-commit", (
    "Changing input code metadata must not alter the built record."
)

#Compruebo que no se ha añadido test-library a las dependencias
assert "test-library" not in built_record["environment"]["dependencies"], (
    "Changing input code metadata must not alter the built record."
)

print("Experiment record input isolation checks passed.")

print("Experiment record builder checks passed.")