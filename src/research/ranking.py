import math

def split_rankable_scores(scores: list[dict]) -> tuple[list[dict], list[dict]]:
    """Separa resultados con su Sharpe finito de resultados no disponibles.
    Recibe registros con candidate_id y validation_sharpe.
    No modifica los diccionarios recibidos."""

    rankable = []
    unavailable = []
    seen_ids = set()

    for score in scores:
        candidate_id = score["candidate_id"]
        sharpe = score["validation_sharpe"]

        #Cada candidato debe quedar identificado sin ambiguedad.
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ValueError("candidate_id must be a non-empty string.")

        if candidate_id in seen_ids:
            raise ValueError(f"Duplicate candidate_id: {candidate_id!r}")

        seen_ids.add(candidate_id)

        #Una metrica no disponible no es un cero
        if sharpe is None:
            unavailable.append(score.copy())
            continue

        #bool se rechaza explicitamente porque en Python es subtipo de int.
        if isinstance(sharpe, bool) or not isinstance(sharpe, (int,float)):
            raise TypeError("validation_sharpe must be a number or None.")

        if not math.isfinite(sharpe):
            raise ValueError("validation_sharpe must be finite.")

        rankable.append(score.copy())
    return rankable, unavailable

def rank_validation_scores(scores: list[dict]) -> dict:
    """Ordena por Sharpe descendente y conserva los no disponibles.
    Los empates exactos comparten posicion mediante ranking
    de competicion: 1,1,3...
    No modifica los registros recibidos."""

    rankable, unavailble = split_rankable_scores(scores)

    ordered_scores = sorted(
        rankable,
        key=lambda score: score["validation_sharpe"],
        reverse=True,
    )

    ranked = []
    previous_sharpe = None
    current_rank = None

    for position, score in enumerate(ordered_scores, start=1):
        sharpe = score["validation_sharpe"]

        #Un valor diferente comienza en una nueva posicion.
        #un empate conserva la posicion del candidato anterior.
        if position == 1 or sharpe != previous_sharpe:
            current_rank = position

        ranked_score = score.copy()
        ranked_score["rank"] = current_rank
        ranked.append(ranked_score)

        previous_sharpe = sharpe

    return {
        "ranked": ranked,
        "unavailable": unavailble,
    }

def build_validation_score(
        candidate_id: str,
        validation_result: dict,
) -> dict:
    """Extrae el Sharpe serializado de un resultado de VALIDATION."""

    metric = validation_result["strategy"]["metrics"]["Sharpe Ratio"]

    status = metric["status"]
    value = metric["value"]

    if status == "unavailable":
        if value is not None:
            raise ValueError(
                "Unavailable calidation Sharpe must have value= None."
            )
    elif status == "finite":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(
                "Finite validation Sharpe must contain a number."
            )

        if not math.isfinite(value):
            raise ValueError(
                "Finite validation Sharpe must contain a finite value."
            )
    else:
        raise ValueError(
            f"Unsupported validation Sharpe status: {status!r}"
        )

    score = {
        "candidate_id": candidate_id,
        "validation_sharpe": value,
    }

    #Reutilizamos la validacion del identificador del valor.
    split_rankable_scores([score])

    return score