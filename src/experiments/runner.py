import pandas as pd

from src.config import ExperimentConfig
from src.backtesting.backtester import run_backtest
from src.backtesting.benchmarks import calculate_buy_hold
from src.metrics import calculate_metrics
from src.trades import build_trade_log, calculate_trade_metrics
from src.strategies.sma_strategies import apply_sma_strategies
from src.research.splits import split_temporal_data


def evaluate_period(
    backtest_data: pd.DataFrame,
    evaluation_index: pd.DatetimeIndex,
    config: ExperimentConfig,
) -> dict:
    """Evalua un periodo con cero o una fila previa de contexto.
    Requiere precios y señales validos, ya preparados.
    No carga archivos, imprime resultados ni modifica la entrada."""

    #1. Comprobamos la estructura temporal admitida
    if not isinstance(backtest_data.index, pd.DatetimeIndex):
        raise TypeError("Backtetst data must have a DatetimeIndex.")

    if not isinstance(evaluation_index, pd.DatetimeIndex):
        raise TypeError("evaluation_index must be a DatetimeIndex.")

    for index in(backtest_data.index, evaluation_index):
        if index.isna().any():
            raise ValueError("Dates must not be missing.")
        if not index.is_unique:
            raise ValueError("Dates must be unique.")
        if not index.is_monotonic_increasing:
            raise ValueError("Dates must be chronological.")

    if len(evaluation_index) < 2:
        raise ValueError("Evaluation requires at least two dates.")

    if(evaluation_index[-1] - evaluation_index[0]).days <= 0:
        raise ValueError("Evaluation requires a positive day span.")

    full_period = evaluation_index.equals(backtest_data.index)
    one_context_row = evaluation_index.equals(backtest_data.index[1:])

    if not (full_period or one_context_row):
        raise ValueError(
            "Evaluate all rows or exclude exactly one initial context row."
        )

    #2. Ejecutamos incluyendo el contexto, si existe.
    full_results = run_backtest(
        backtest_data,
        initial_capital=config.initial_capital,
        transaction_cost=config.transaction_cost,
    )

    #Solo estas filas pertenecen a la evaluacion.
    evaluated_results = full_results.loc[evaluation_index].copy()

    strategy_metrics = calculate_metrics(
        evaluated_results["StrategyEquity"],
        evaluated_results["StrategyReturn"],
        evaluated_results["Position"],
        evaluated_results["Trade"],
        initial_capital=config.initial_capital,
    )

    #3. Conservamos el contexto para reconocer la primera entrada.
    trade_log = build_trade_log(full_results)
    trade_metrics = calculate_trade_metrics(trade_log)

    #4. Los benchmarks empiezan en la primera apertura evaluada.
    benchmark_prices = evaluated_results["Open"]
    benchmarks = {}

    benchamrk_costs = {
        "buy_hold_open_gross": 0.0,
        "buy_hold_open_entry_cost": config.transaction_cost,
    }

    for name, entry_cost in benchamrk_costs.items():
        returns, equity = calculate_buy_hold(
            benchmark_prices,
            initial_capital=config.initial_capital,
            entry_cost=entry_cost,
        )

        benchmarks[name] = {
            "returns": returns,
            "equity": equity,
            "metrics": calculate_metrics(
                equity,
                returns,
                initial_capital=config.initial_capital,
            ),
        }

    #5. Devolvemos datos de calculo, todavia no serializamos.
    return{
        "backtest": evaluated_results,
        "strategy_metrics": strategy_metrics,
        "trade_log": trade_log,
        "trade_metrics": trade_metrics,
        "benchmarks": benchmarks,
    }

def run_experiment(
    data: pd.DataFrame,
    config: ExperimentConfig,
) -> dict:
    """Ejecuta el experimento SMA sobre datos OHLCV ya validados.
    Recibe el snapshot sin la preparacion especifica de main.
    No modifica la entrada ni realiza operaciones de entrada/salida."""

    #1.Conservamos la preparacion del experimento original.
    prepared_data = data.copy(deep=True)

    prepared_data["Return"] = prepared_data["Close"].pct_change()
    prepared_data = prepared_data.dropna()

    if prepared_data.empty:
        raise ValueError("No observations remain after data preparation.")

    #Columna historica conservada para mantener la saldia actual.
    #No susutituye los benchamarks independientes de TRAIN y TEST.
    prepared_data["BuyHold"] = (
        config.initial_capital
        * prepared_data["Close"]
        / prepared_data["Close"].iloc[0]
    )

    #2. Las medias utilizan el cierre actual y los anteriores.
    strategy_data = apply_sma_strategies(
        prepared_data,
        fast_window=config.fast_window,
        slow_window=config.slow_window,
    )

    #3. Dividimos los datos con las fronteras de la configuracion.
    periods = split_temporal_data(
        strategy_data,
        validation_start=config.validation_start,
        test_start=config.test_start,
    )

    sma_columns = [
        f"SMA_{config.fast_window}",
        f"SMA_{config.slow_window}",
    ]

    results = {}

    #4. Evaluamos cada periodo con capital independiente.
    for name, period_data in periods.items():
        if name == "train":
            #TRAIN comienza sin una señal previa de contexto.
            backtest_data = period_data

        else:
            #Conservamos la exigencia de disponer de medias al comenzar
            #los periodos posteriores a TRAIN.
            if not period_data.iloc[0][sma_columns].notna().all():
                raise ValueError(
                    f"The first {name.upper()} row must have valid SMA features."
                )

            #Localizamos los extremos del periodo en los datos completos.
            first_position = strategy_data.index.get_loc(
                period_data.index[0]
            )
            last_position = strategy_data.index.get_loc(
                period_data.index[-1]
            )

            #Añadimos exactamente una fila anterior.
            #El limite final de iloc es exclusivo.
            backtest_data = strategy_data.iloc[
                first_position - 1:last_position + 1
            ].copy()

        results[name] = evaluate_period(
            backtest_data,
            evaluation_index=period_data.index,
            config=config,
        )
    return results