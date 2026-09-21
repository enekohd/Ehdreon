import numpy as np

def calculate_metrics(equity, returns, position=None, trade=None, *, initial_capital):

    final_value = equity.iloc[-1]

    years = (
        equity.index[-1] - equity.index[0]
    ).days / 365.25

    initial_value = initial_capital

    cagr = (
        final_value / initial_value
    ) ** (1 / years) - 1

    daily_volatility = returns.std()

    annualized_volatility = (
        daily_volatility * np.sqrt(252)
    )

    annualized_return = returns.mean() * 252

    sharpe_ratio = (
        annualized_return / annualized_volatility
    )

    running_max = equity.cummax().clip(lower=initial_capital)

    drawdown = (
        equity - running_max
    ) / running_max

    max_drawdown = drawdown.min()

    max_drawdown_date = drawdown.idxmin()

    active_returns = returns[returns != 0]

    positive_days = (active_returns > 0).sum()
    negative_days = (active_returns < 0).sum()

    positive_day_ratio = positive_days / len(active_returns)

    average_positive_returns = returns[returns > 0].mean()
    average_negative_returns = returns[returns < 0].mean()

    exposure = position.mean() if position is not None else None

    number_of_orders = trade.sum() if trade is not None else None


    metrics = {
        "Initial Value": initial_value,
        "Final Value": final_value,
        "CAGR": cagr,
        "Annualized Return": annualized_return,
        "Annualized Volatility": annualized_volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown,
        "Max Drawdown Date": max_drawdown_date,
        "Positive Days": positive_days,
        "Negative Days": negative_days,
        "Positive Day Ratio": positive_day_ratio,
        "Average positive returns" : average_positive_returns,
        "Average negative returns" : average_negative_returns,
        "Exposure" : exposure,
        "Number of orders" : number_of_orders
    }

    return metrics
