def run_backtest(data, 
                 initial_capital=10000, 
                 transaction_cost=0.001
    ):

    data = data.copy()

    #Return between consecutive market opens
    data["OpenReturn"] = (
        data["Open"].pct_change().fillna(0)
    )

    # Signal generated at today's close
    # becomes position at next session's open
    data["Position"] = (
        data["Signal"].shift(1).fillna(0)
    )

    # Detect entries and exits
    data["Trade"] = (
        data["Position"].diff().abs().fillna(0)
    )

    # Return earned from Open(t-1) -> Open(t)
    data["StrategyReturn"] = (
        data["Position"].shift(1).fillna(0) * data["OpenReturn"]
        - data["Trade"] * transaction_cost
    )

    data["StrategyEquity"] = (
        initial_capital 
        * (1 + data["StrategyReturn"]).cumprod()
    )

    return data