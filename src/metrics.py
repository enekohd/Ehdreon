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

    #Solo calculamos el cociente si la volatilidad es finita y positiva
    if(
        np.isfinite(annualized_volatility) and annualized_volatility > 0
    ):
        sharpe_ratio = annualized_return / annualized_volatility
    else:
        sharpe_ratio = None

    running_max = equity.cummax().clip(lower=initial_capital)

    drawdown = (
        equity - running_max
    ) / running_max

    max_drawdown = drawdown.min()

    max_drawdown_date = (
        drawdown.idxmin()
        if max_drawdown < 0
        else None
    )

    active_returns = returns[returns != 0]
    positive_returns = returns[returns > 0]
    negative_returns = returns[returns < 0]

    positive_days = len(positive_returns)
    negative_days = len(negative_returns)

    # La proporción se calcula sobre días con retorno distinto de cero.
    positive_day_ratio = (
        positive_days / len(active_returns)
        if not active_returns.empty
        else None
    )

    average_positive_returns = (
        positive_returns.mean()
        if not positive_returns.empty
        else None
    )

    average_negative_returns = (
        negative_returns.mean()
        if not negative_returns.empty
        else None
    )

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
