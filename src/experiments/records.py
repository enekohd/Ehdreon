import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from dataclasses import asdict
from copy import deepcopy

def build_experiment_record(
    config,
    *,
    dataset_sha256: str,
    code_info: dict,
    environment_info: dict,
    conventions: dict,
)-> dict:
    """Construye los metadatos iniciales de una ejecución."""

    # 1. Generar identificador y fecha UTC.
    experiment_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    # 2. Convertir config a diccionario.
    config_data = asdict(config)

    # 3. Construir y devolver el registro.
    experiment_record = {
        "experiment_id": experiment_id,
        "created_at": created_at,
        "schema_version": 2,
        "config": config_data,
        "dataset": {
                "dataset_id": config.dataset_id,
                "sha256": dataset_sha256,
            },
        "code": deepcopy(code_info),
        "environment": deepcopy(environment_info),
        "conventions": deepcopy(conventions),
    }
    return experiment_record

def save_experiment_record(record: dict, path: Path) -> None:
    """Guarda un registro como JSON sin sobreescribir archivos existentes"""

    record_json = json.dumps(
        record,
        indent=2,
        allow_nan=False,
    )

    with path.open("x", encoding="utf-8") as file:
        file.write(record_json)

def attach_experiment_results(
        record: dict,
        results: dict,
) -> dict:
    """Devuelve una copia del registro con sus resultados."""

    if "results" in record:
        raise ValueError("The experiment record already contains results.")

    completed_record = deepcopy(record)
    completed_record["results"] = deepcopy(results)

    return completed_record