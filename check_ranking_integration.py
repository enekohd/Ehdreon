from src.research.ranking import (
    build_score_from_development_record,
    rank_validation_scores,
)
from copy import deepcopy

def make_synthetic_record(train_sharpe, validation_sharpe):
    """Construye solo los campos necesarios para esta prueba."""

    return {
        "conventions": {
            "evaluation": {
                "mode": "development",
                "periods": ["train", "validation"],
            },
        },
        "results": {
            "train": {
                "strategy": {
                    "metrics": {
                        "Sharpe Ratio": {
                            "status": "finite",
                            "value": train_sharpe,
                        },
                    },
                },
            },
            "validation": {
                "strategy": {
                    "metrics": {
                        "Sharpe Ratio": {
                            "status": "finite",
                            "value": validation_sharpe,
                        },
                    },
                },
            },
        },
    }

record_a = make_synthetic_record(
    train_sharpe=5.0,
    validation_sharpe=0.2,
)

record_b = make_synthetic_record(
    train_sharpe=-1.0,
    validation_sharpe=0.8,
)

scores = [
    build_score_from_development_record("A", record_a),
    build_score_from_development_record("B", record_b),
]

ranking = rank_validation_scores(scores)

assert [
    score["candidate_id"]
    for score in ranking["ranked"]
] == ["B", "A"], "Ranking mmust follow VALIDATION, not TRAIN."

assert [
    score["validation_sharpe"]
    for score in ranking["ranked"]
] == [0.8,0.2], "Scores must come from VALIDATION."


print("Development record VALIDATION selection checks passed.")


#Cada caso parte de una copia independiente de un registro valido.
wrong_mode = deepcopy(record_a)
wrong_mode["conventions"]["evaluation"]["mode"] = "full"

wrong_periods = deepcopy(record_a)
wrong_periods["conventions"]["evaluation"]["periods"] = [
    "train",
    "validation",
    "test",
]

unexpected_test = deepcopy(record_a)
unexpected_test["results"]["test"] = deepcopy(
    record_a["results"]["validation"]
)

missing_validation = deepcopy(record_a)
del missing_validation["results"]["validation"]

invalid_records = [
    (wrong_mode, "requires a development record"),
    (wrong_periods, "must declare TRAIN and VALIDATION"),
    (unexpected_test, "must contain only TRAIN and VALIDATION"),
    (missing_validation, "must contain only TRAIN and VALIDATION"),
]

for invalid_record, expected_message in invalid_records:
    try:
        build_score_from_development_record("A", invalid_record)
    except ValueError as error:
        assert expected_message in str(error), (
            f"Unexpected error: {error}"
        )
    else:
        raise AssertionError(
            "An incompatible development record was accepted."
        )

print("Incompatible development records correctly rejected.")

original_record = deepcopy(record_a)

extracted_score = build_score_from_development_record(
    "A",
    record_a,
)

assert record_a == original_record, (
    "Score extraction modified the experiment record."
)

extracted_score["validation_sharpe"] == 999.0

assert record_a == original_record, (
    "Changing the score modified the experiment record."
)

print("Development record extraction preservation checks passed.")