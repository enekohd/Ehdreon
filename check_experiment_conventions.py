import json

from src.experiments.conventions import build_experiment_conventions

conventions = build_experiment_conventions()

assert conventions["conventions_version"] == 2

assert conventions["evaluation"]["periods"] == [
    "train",
    "validation",
    "test",
]

assert conventions["evaluation"]["context_in_metrics"] is False

assert(
    conventions["evaluation"]["validation_usage"]
    == "development_and_candidate_selection"
)

assert conventions["strategy"]["signal_rule"] == "fast_sma > slow_sma"
assert conventions["strategy"]["otherwise_signal"] == 0
assert conventions["strategy"]["warmup_signal"] == 0

assert conventions["execution"]["commission_basis"] == "traded_notional"
assert conventions["execution"]["commission_sides"] == ["entry", "exit"]
assert conventions["execution"]["execution_time"] == "next_session_open"

assert conventions["valuation"]["liquidate_at_period_end"] is False

assert conventions["evaluation"]["untouched_final_holdout"] is False
assert conventions["evaluation"]["test_context_in_metrics"] is False

#La estructura completa debe ser compatible con JSON estricto.
encoded = json.dumps(conventions, allow_nan=False)
assert json.loads(encoded) == conventions

#Modificar una llamada no debe alterar las siguientes.
conventions["execution"]["commission_sides"].append("unexpected")

fresh_conventions = build_experiment_conventions()

assert fresh_conventions["execution"]["commission_sides"] == [
    "entry",
    "exit",
], "Convention builders must not share mutable state."

assert (
    conventions["execution"]["commission_rate_source"]
    == "config.transaction_cost"
)

assert conventions["valuation"]["price_field"] == "Open"

assert (
    conventions["evaluation"]["capital_policy"]
    == "independent_initial_capital_per_period"
)

assert (
    conventions["evaluation"]["trade_metrics_scope"]
    == "closed_trades_only"
)

expected_entry_commissions = {
    "buy_hold_open_gross": "none",
    "buy_hold_open_entry_cost": "config.transaction_cost_on_notional",
}

for benchmark_name, expected in expected_entry_commissions.items():
    assert (
        conventions["benchmarks"][benchmark_name]["entry_commission"]
        == expected
    ), f"{benchmark_name}: incorrect entry commission convention."


print("Experiment convention structure checks passed.")
