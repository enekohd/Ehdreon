def calculate_buy_hold(
        open_prices,
        initial_capital,
        entry_cost = 0.0,
):

    """Calcula retornos y equity de Buy & Hold entre aperturas.

    Compra en la primera apertura, descuenta el coste de entrada
    y mantiene la posición abierta hasta el final del periodo.

    Requiere una serie no vacía de precios positivos, sin valores
    ausentes y ordenada cronológicamente.

    Devuelve:
    Una pareja (returns, equity).
    """

    # 1. Calcular los retornos entre aperturas.
    # La primera fila debe comenzar con retorno cero.
    returns = (
       open_prices.pct_change().fillna(0)
    )

    # 2. Incorporar el coste de entrada en la primera fila.
    returns.iloc[0] = -entry_cost

    # 3. Construir la equity mediante capitalización compuesta.
    equity = initial_capital * (1 + returns).cumprod()

    return returns, equity