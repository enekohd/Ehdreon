from src.backtesting.execution import (
    execute_buy_all_cash,
    execute_sell_all,
)

def run_backtest(data, 
                 initial_capital=10000, 
                 transaction_cost=0.001
    ):

    #1. Trabajamos sobre una copia para no modificar los datos originales.
    data = data.copy()

    #Conservamos el retorno del mercado como una columna de diagnostico.
    data["OpenReturn"] = (
        data["Open"].pct_change().fillna(0)
    )

    #2. La señal del cierre anterior detrmina el objetivo en esta apertura.
    data["TargetPosition"] = data["Signal"].shift(1).fillna(0)

    #3. Estado inicial de la cartera
    cash = initial_capital
    quantity = 0.0
    previous_equity = initial_capital

    #Aqui guardaremos el estado y los resultados de cada apertura
    records = []

    #4. Recorremos precios y objetivos en orden cronologico
    for price, target_position in zip(
        data["Open"],
        data["TargetPosition"],
        strict=True,
    ):
        #Estos valores se reinician cada dia
        #Si no operamos, no hay orden ni comision
        trade = 0.0
        fee = 0.0

        if target_position == 1 and quantity == 0.0:
            buy_result = execute_buy_all_cash(
                cash=cash,
                price=price,
                commission_rate=transaction_cost,
            )

            cash = buy_result["cash_after"]
            quantity = buy_result["quantity"]
            fee = buy_result["fee"]
            trade = 1.0

        elif target_position == 0 and quantity > 0.0:
            sell_results = execute_sell_all(
                quantity=quantity,
                price=price,
                commission_rate=transaction_cost,
            )

            cash = cash + sell_results["cash_received"]
            quantity = sell_results["quantity_after"]
            fee = sell_results["fee"]
            trade = 1.0

        #5. Valoramos la cartera despues de la posible ejecucion.
        equity = cash + quantity * price

        # La posicion indica si tenemos unidades , no cuantas.
        position = 1.0 if quantity > 0.0 else 0.0

        #El retorno incluye la variacion de precio y las comisiones
        #que ya estan reflejadas en el efectivo
        strategy_return = equity / previous_equity - 1

        records.append({
            "Cash": cash,
            "Quantity": quantity,
            "Position": position,
            "Trade": trade,
            "Fee": fee,
            "StrategyEquity": equity,
            "StrategyReturn": strategy_return,
        })

        #La equity actual sera la referencia de la siguiente apertura.
        previous_equity = equity

    #6. Incorporamos los resultados de la siguiente apertura.
    result_columns = [
        "Cash",
        "Quantity",
        "Position",
        "Trade",
        "Fee",
        "StrategyEquity",
        "StrategyReturn",
    ]

    for column in result_columns:
        data[column] = [record[column] for record in records]

    return data