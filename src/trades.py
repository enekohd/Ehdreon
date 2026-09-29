import pandas as pd

def build_trade_log(data):

    trades = []

    in_position = False

    entry_date = None
    entry_price = None


    for i in range(1, len(data)):

        previous_position = data["Position"].iloc[i-1]
        current_position = data["Position"].iloc[i]

        current_date = data.index[i]
        current_price = data["Open"].iloc[i]

        #Entry 0 -> 1
        if previous_position == 0 and current_position == 1:

            in_position = True

            # 1. Identificamos cuándo y a qué precio hemos comprado.
            entry_date = current_date
            entry_price = current_price

            # 2. Recuperamos las unidades y la comisión de la ejecución.
            entry_quantity = data["Quantity"].iloc[i]
            entry_fee = data["Fee"].iloc[i]

            # 3. Calculamos los importes usando los valores anteriores.
            entry_notional = entry_quantity * entry_price
            entry_outlay = entry_notional + entry_fee


        #Exit 1 -> 0
        if previous_position == 1 and current_position == 0:

            if in_position:

                exit_date = current_date
                exit_price = current_price

                gross_return = (
                    exit_price - entry_price
                ) / entry_price

                # En este modelo no hay compras adicionales ni ventas parciales:
                # vendemos todas las unidades adquiridas en la entrada.
                exit_notional = entry_quantity * exit_price
                exit_fee = data["Fee"].iloc[i]

                gross_pnl = exit_notional - entry_notional
                net_pnl = gross_pnl - entry_fee - exit_fee

                trade_return = net_pnl / entry_outlay

                holding_days = (
                    exit_date - entry_date
                ).days

                trades.append({
                    "Entry Date" : entry_date,
                    "Entry Price" : entry_price,
                    "Exit Date" : exit_date,
                    "Exit Price" : exit_price,
                    "Gross Return" : gross_return,
                    "Net Return" : trade_return,
                    "Holding days" : holding_days,
                    "Quantity": entry_quantity,
                    "Entry Fee": entry_fee,
                    "Exit Fee": exit_fee,
                    "Gross PnL": gross_pnl,
                    "Net PnL": net_pnl,
                })

                in_position = False

    trade_log  = pd.DataFrame(trades)

    return trade_log

def calculate_trade_metrics(trade_log):

    number_of_trades = len(trade_log)

    winning_trades = trade_log[trade_log["Net Return"] > 0]
    losing_trades = trade_log[trade_log["Net Return"] < 0]
    trade_win_rate = (
        len(winning_trades) / number_of_trades
    )

    average_win = (
        winning_trades["Net Return"].mean()
        if len(winning_trades) > 0
        else 0.0
    )
    average_loss = (
        losing_trades["Net Return"].mean()
        if len(losing_trades) > 0
        else 0.0
    )

    gross_profit = winning_trades["Net Return"].sum()
    gross_loss = abs(losing_trades["Net Return"].sum())

    if gross_loss > 0:
        profit_factor = (
            gross_profit / gross_loss
        )
    else:
        profit_factor = float("inf")

    expectancy = trade_log["Net Return"].mean()

    avg_holding_days = trade_log["Holding days"].mean()

    metrics = {
        "Number of Trades" : number_of_trades,
        "Trade Win Rate" : trade_win_rate,
        "Average Win" : average_win,
        "Average Loss" : average_loss,
        "Profit Factor" : profit_factor,
        "Expectancy" : expectancy,
        "Average Holding Days" : avg_holding_days
    }
    return metrics

            
