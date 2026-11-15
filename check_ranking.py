from src.research.ranking import split_rankable_scores
from copy import deepcopy
from src.research.ranking import rank_validation_scores
from src.research.ranking import build_validation_score

scores = [
    {"candidate_id": "A", "validation_sharpe": 0.8},
    {"candidate_id": "B", "validation_sharpe": None},
    {"candidate_id": "C", "validation_sharpe": -0.2},
    {"candidate_id": "D", "validation_sharpe": 0.0},
]

rankable, unavailable = split_rankable_scores(scores)

rankable_ids = [
    score["candidate_id"]
    for score in rankable
]

assert rankable_ids == ["A", "C", "D"], (
    "Rankable candidates do not match the expected identifiers."
)

unavailable_ids = [
    score["candidate_id"]
    for score in unavailable
]

assert unavailable_ids == ["B"], (
    "Unavailable candidates do not match the expected identifiers."
)

assert rankable[2]["candidate_id"] == "D" , (
    "The third rankable candidate must be D."
)

assert rankable[2]["validation_sharpe"] == 0.0 , (
    "A zero Sharpe must remain a valid rankable value."
)

print("Rankable and unavailable score separation checks passed.")

#Cada caso introduce un unico defecto.
invalid_cases = [
    (
        [{"candidate_id": "A", "validation_sharpe": float("nan")}],
        ValueError,
        "must be finite",
    ),
    (
        [{"candidate_id": "A", "validation_sharpe": float("inf")}],
        ValueError,
        "must be finite",
    ),
    (
        [{"candidate_id": "A", "validation_sharpe": float("-inf")}],
        ValueError,
        "must be finite",
    ),
    (
        [{"candidate_id": "A", "validation_sharpe": True}],
        TypeError,
        "must be a number or None",
    ),
    (
        [{"candidate_id": "A", "validation_sharpe": "0.8"}],
        TypeError,
        "must be a number or None",
    ),
    (
        [{"candidate_id": "", "validation_sharpe": 0.8}],
        ValueError,
        "candidate_id",
    ),
    (
        [
            {"candidate_id": "A", "validation_sharpe": 0.8},
            {"candidate_id": "A", "validation_sharpe": None},
        ],
        ValueError,
        "Duplicate candidate_id",
    ),
]

for invalid_scores, expected_error, expected_message in invalid_cases:
    try:
        split_rankable_scores(invalid_scores)
    except expected_error as error:
        assert expected_message in str(error), (
            f"Unexpected error: {error}"
        )
    else:
        raise AssertionError(
            f"Invalid scores were accepted: {invalid_scores}"
        )

print("Invalid ranking inputs correctly rejected.")

#Conservamos una referencia independiente del contenido original.
original_scores = deepcopy(scores)

rankable_copy, unavailable_copy = split_rankable_scores(scores)

#Ejecutar la funcion no debe modificar la entrada.
assert scores == original_scores, (
    "Score separation modified the input."
)

#Cambiar los resultados tampoco debe modificar los diccionarios originales.
rankable_copy[0]["validation_sharpe"] = 999.0
unavailable_copy[0]["candidate_id"] = "changed"

assert scores == original_scores, (
    "Returned records share mutable dictionaries with the input."
)

print("Score separation input preservation checks passed.")

ranking_scores = [
    {"candidate_id": "A", "validation_sharpe": 0.8},
    {"candidate_id": "B", "validation_sharpe": None},
    {"candidate_id": "C", "validation_sharpe": -0.2},
    {"candidate_id": "D", "validation_sharpe": 0.8},
    {"candidate_id": "E", "validation_sharpe": 0.0},
]

original_ranking_scores = deepcopy(ranking_scores)

ranking = rank_validation_scores(ranking_scores)

actual_ids = [
    score["candidate_id"]
    for score in ranking["ranked"]
]

actual_ranks = [
    score["rank"]
    for score in ranking["ranked"]
]

assert actual_ids == ["A", "D", "E", "C"], (
    "Candidates are not ordered by descending Sharpe."
)

assert actual_ranks == [1, 1, 3, 4], (
    "Exact ties must use competition ranking."
)

assert ranking["unavailable"] == [
    {"candidate_id": "B", "validation_sharpe": None},
], "Unavailable candidates must remain outside the ranking."

assert ranking_scores == original_ranking_scores, (
    "Ranking modified the input records."
)

print("Validation ranking order and tie checks passed.")

#Sin entradas, ambas listas deben estar vacias.
assert rank_validation_scores([]) == {
    "ranked": [],
    "unavailable": [],
}

#Si todos los Sharpe son None, conservamos los candidatos sin clasificarlos.
unavailable_scores = [
    {"candidate_id": "A", "validation_sharpe": None},
    {"candidate_id": "B", "validation_sharpe": None},
]

unavailable_ranking = rank_validation_scores(unavailable_scores)

assert unavailable_ranking["ranked"] == []
assert unavailable_ranking["unavailable"] == unavailable_scores

print("Empty and unavailable-only ranking checks passed.")

negative_scores = [
    {"candidate_id": "A", "validation_sharpe": -0.8},
    {"candidate_id": "B", "validation_sharpe": -0.2},
    {"candidate_id": "C", "validation_sharpe": -0.5},
]

negative_ranking = rank_validation_scores(negative_scores)

assert [
    score["candidate_id"]
    for score in negative_ranking["ranked"]
] == ["B", "C", "A"]

assert [
    score["rank"]
    for score in negative_ranking["ranked"]
] == [1,2,3]

print("Negative Sharpe ranking checks passed.")

finite_validation_result = {
    "strategy": {
        "metrics": {
            "Sharpe Ratio": {
                "value": 0.8,
                "status": "finite",
            },
        },
    },
}

unavailable_validation_result = {
    "strategy": {
        "metrics": {
            "Sharpe Ratio": {
                "value": None,
                "status": "unavailable",
            },
        },
    },
}

finite_score = build_validation_score(
    "A",
    finite_validation_result,
)

unavailable_score = build_validation_score(
    "B",
    unavailable_validation_result,
)

assert finite_score == {
    "candidate_id": "A",
    "validation_sharpe": 0.8,
}

assert unavailable_score == {
    "candidate_id": "B",
    "validation_sharpe": None,
}

# Comprobamos también que el adaptador y el clasificador encajan.
adapted_ranking = rank_validation_scores([
    finite_score,
    unavailable_score,
])

assert adapted_ranking["ranked"] == [
    {
        "candidate_id": "A",
        "validation_sharpe": 0.8,
        "rank": 1,
    },
]

assert adapted_ranking["unavailable"] == [unavailable_score]

print("Serialized validation score adapter checks passed.")

invalid_metric_cases = [
    (
        {"status": "finite", "value": None},
        TypeError,
        "must contain a number",
    ),
    (
        {"status": "finite", "value": True},
        TypeError,
        "must contain a number",
    ),
    (
        {"status": "finite", "value": float("nan")},
        ValueError,
        "must contain a finite value",
    ),
    (
        {"status": "finite", "value": float("inf")},
        ValueError,
        "must contain a finite value",
    ),
    (
        {"status": "unavailable", "value": 0.8},
        ValueError,
        "must have value",
    ),
    (
        {"status": "positive_infinity", "value": None},
        ValueError,
        "Unsupported validation Sharpe status",
    ),
    (
        {"status": "negative_infinity", "value": None},
        ValueError,
        "Unsupported validation Sharpe status",
    ),
    (
        {"status": "unknown", "value": 0.8},
        ValueError,
        "Unsupported validation Sharpe status",
    ),
]

for metric , expected_error, expected_message in invalid_metric_cases:
    invalid_result = {
        "strategy": {
            "metrics": {
                "Sharpe Ratio": metric,
            }
        }
    }

    try:
        build_validation_score("A", invalid_result)
    except expected_error as error:
        assert expected_message in str(error), (
            f"Unexpected error: {error}"
        )
    else:
        raise AssertionError(
            f"The adapter accepted an invalid metric: {metric}"
        )

print("Invalid serialized validation metrics correctly rejected.")

original_validation_result = deepcopy(finite_validation_result)

adapted_score = build_validation_score(
    "A",
    finite_validation_result,
)

assert finite_validation_result == original_validation_result, (
    "The adapter modified the validation result."
)

adapted_score["validation_sharpe"] = 999.0

assert finite_validation_result == original_validation_result, (
    "Changing the adapted score modified the validation result."
)


print("Validation score adapter input preservation checks passed.")