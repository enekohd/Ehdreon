from copy import deepcopy
from src.research.ranking import (
    build_score_from_development_record,
    rank_validation_scores,
)

def build_comparison_context(record: dict) -> dict:
    """Extrae las condiciones comunes del estudio de ventanas SMA.
    Excluye unicamente las ventanas de la confifuracion.
    No incluye identidad de ejecucion ni metricas."""

    evaluation = record["conventions"]["evaluation"]

    if (
        evaluation["mode"] != "development"
        or evaluation["periods"] != ["train", "validation"]
        or set(record["results"]) != {"train", "validation"}
    ):
        raise ValueError(
            "Comparison requires TRAIN/VALIDATION development records."
        )

    shared_config = deepcopy(record["config"])

    if shared_config["strategy_name"] != "sma_trend":
        raise ValueError("Comparison requires the SMA strategy.")

    #Estos son los unicos parametros que permite variar este estudio.
    del shared_config["fast_window"]
    del shared_config["slow_window"]


    return {
        "config": shared_config,
        "dataset": deepcopy(record["dataset"]),
        "conventions": deepcopy(record["conventions"]),
        "code": deepcopy(record["code"]),
        "environment": deepcopy(record["environment"]),
        "periods": {
            name: deepcopy(record["results"][name]["period"])
            for name in ("train", "validation")
        },
    }

def compare_development_records(
    records_by_candidate: dict[str, dict],
) -> dict:
    """Clasifica registros de desarrollo con condiciones comunes."""

    if not records_by_candidate:
        raise ValueError("Comparison requires at least one candidate.")

    reference_context = None
    scores = []

    for candidate_id, record in records_by_candidate.items():
        context = build_comparison_context(record)

        if reference_context is None:
            reference_context = context
        elif context != reference_context:
            raise ValueError(
                f"Incompatible comparison context for candidate "
                f"{candidate_id!r}."
            )

        score = build_score_from_development_record(
            candidate_id,
            record,
        )
        scores.append(score)

    return rank_validation_scores(scores)