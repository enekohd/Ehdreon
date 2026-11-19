from copy import deepcopy
from dataclasses import asdict

from src.config import ExperimentConfig
from src.experiments.conventions import build_experiment_conventions
from src.research.comparison import build_comparison_context

from src.research.comparison import compare_development_records

config = ExperimentConfig()

# Registro sintético con los campos que utiliza esta función.
# No representa una ejecución real ni necesita métricas.
record_a = {
    "config": asdict(config),
    "dataset": {
        "dataset_id": config.dataset_id,
        "sha256": "synthetic-test-hash",
    },
    "conventions": build_experiment_conventions(
        config,
        mode="development",
    ),
    "code": {
        "commit": "synthetic-test-commit",
        "working_tree_dirty": False,
    },
    "environment": {
        "python_version": "synthetic-test-version",
        "dependencies": {},
    },
    "results": {
        "train": {
            "period": {
                "start": "2020-01-03T00:00:00",
                "end": "2022-12-30T00:00:00",
                "rows": 755,
            },
        },
        "validation": {
            "period": {
                "start": "2023-01-03T00:00:00",
                "end": "2023-12-29T00:00:00",
                "rows": 250,
            },
        },
    },
}

original_record_a = deepcopy(record_a)

record_b = deepcopy(record_a)
record_b["config"]["fast_window"] = 20
record_b["config"]["slow_window"] = 100

context_a = build_comparison_context(record_a)
context_b = build_comparison_context(record_b)

assert context_a == context_b, (
    "Changing only the SMA wondows must preserve comparison conditions."
)

assert record_a == original_record_a, (
    "Building the comparison context modified the source record."
)

assert "fast_window" in record_a["config"]
assert "slow_window" in record_a["config"]

print("SMA comparison context checks passed.")

record_c = deepcopy(record_a)

# Modificamos únicamente la comisión de la copia.
record_c["config"]["transaction_cost"] = 0.002

context_c = build_comparison_context(record_c)

assert context_c != context_a, (
    "The context does not detect the changed transaction cost."
)

print("Changed transaction cost correctly detected.")

# Cada caso modifica una única condición del experimento.
changed_hash = deepcopy(record_a)
changed_hash["dataset"]["sha256"] = "different-hash"

changed_commit = deepcopy(record_a)
changed_commit["code"]["commit"] = "different-commit"

changed_environment = deepcopy(record_a)
changed_environment["environment"]["pythob_version"] = "different-version"

changed_execution = deepcopy(record_a)
changed_execution["conventions"]["execution"]["exacution_time"] = (
    "same_session_close"
)

changed_period = deepcopy(record_a)
changed_period["results"]["validation"]["period"]["rows"] = 249

different_context_cases = [
    ("dataset hash", changed_hash),
    ("code commit", changed_commit),
    ("environment", changed_environment),
    ("execution convention", changed_execution),
    ("evaluated period", changed_period),
]

for case_name, changed_record in different_context_cases:
    changed_context = build_comparison_context(changed_record)

    assert changed_context != context_a, (
        f"The comparison context ignored a change in {case_name}."
    )

print("Comparison condition changes correctly detected.")

isolated_context = build_comparison_context(record_a)

isolated_context["dataset"]["sha256"] = "changed-after-building"
isolated_context["conventions"]["execution"]["commission_sides"].append(
    "unexpected"
)

assert record_a == original_record_a, (
    "Changing the comparison context modified the source record."
)

print("Comparison context isolation checks passed.")

comparison_a = deepcopy(record_a)
comparison_b = deepcopy(record_b)

comparison_a["results"]["validation"]["strategy"] = {
    "metrics": {
        "Sharpe Ratio": {
            "status": "finite",
            "value": 0.2,
        }
    }
}

comparison_b["results"]["validation"]["strategy"] = {
    "metrics": {
        "Sharpe Ratio": {
            "status": "finite",
            "value": 0.8,
        },
    },
}

comparison = compare_development_records({
    "A": comparison_a,
    "B": comparison_b,
})

assert [
    score["candidate_id"]
    for score in comparison["ranked"]
] == ["B", "A"]

print("Compatible development records ranked correctly.")

incompatible_b = deepcopy(comparison_b)
incompatible_b["config"]["transaction_cost"] = 0.002

try:
    compare_development_records({
        "A": comparison_a,
        "B": incompatible_b,
    })
except ValueError as error:
    assert "Incompatible comparison context" in str(error), (
        f"Unexpected error: {error}"
    )
else: raise AssertionError(
    "The comparison ranked records with different transaction costs."
)

print("Incompatible development comparison correctly rejected.")

try:
    compare_development_records({})
except ValueError as error:
    assert "at least one candidate" in str(error), (
        f"Unexpected error: {error}"
    )
else:
    raise AssertionError("An empty comparison was accepted.")

print("Empty development comparison correctly rejected.")


input_records = {
    "A": deepcopy(comparison_a),
    "B": deepcopy(comparison_b),
}

original_input_records = deepcopy(input_records)

comparison_results = compare_development_records(input_records)

assert input_records == original_input_records, (
    "Comparison modified the inpur experiment records."
)

#Tampoco debe compartir los diccionarios de resultados con la entrada.
comparison_results["ranked"][0]["validation_sharpe"] = 999.0

assert input_records == original_input_records, (
    "Changing the ranking modified an input experiment record."
)

print("Development comparison input preservation checks passed.")
