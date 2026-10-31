def build_experiment_conventions() -> dict:
    """Describe las reglas del experimento SMA actual."""

    return{
        "conventions_version": 2,
        "strategy": {
            "name": "sma_trend",
            "family": "trend_following",
            "price_field": "Close",
            "signal_rule": "fast_sma > slow_sma",
            "otherwise_signal": 0,
            "warmup_signal": 0,
            "parameter_source": "config",
        },
        "execution": {
            "signal_time": "session_close",
            "execution_time": "next_session_open",
            "execution_price_field": "Open",
            "position_policy": "long_or_cash",
            "entry_sizing": "all_cash_including_entry_fee",
            "fractional_units": True,
            "commission_basis": "traded_notional",
            "commission_sides": ["entry", "exit"],
            "commission_rate_source": "config.transaction_cost",
            "slippage_model": "not_modeled",
            "spread_model": "not_modeled",
            "liquidity_constraints": "not_modeled",
        },
        "valuation": {
            "price_field": "Open",
            "timing": "after_execution",
            "equity_rule": "cash + quantity * price",
            "liquidate_at_period_end": False,
        },
        "evaluation": {
            "capital_policy": "independent_initial_capital_per_period",
            "test_context_in_metrics": False,
            "trade_metrics_scope": "closed_trades_only",
            "test_usage": "previously_observed_during_development",
            "untouched_final_holdout": False,
            "periods": ["train", "validation", "test"],
            "validation_usage": "development_and_candidate_selection",
            "context_in_metrics": False,
        },
        "benchmarks": {
            "buy_hold_open_gross": {
                "entry": "first_evaluated_open",
                "entry_commission": "none",
                "liquidate_at_period_end": False,
            },
            "buy_hold_open_entry_cost": {
                "entry": "first_evaluated_open",
                "entry_commission": "config.transaction_cost_on_notional",
                "liquidate_at_period_end": False,
            },
        },
    }