from src.backtesting.execution import(
    execute_sell_all,
    execute_buy_all_cash
)

initial_capital = 1000.0
commission_rate = 0.001

open_prices = [100.0, 110.0, 121.0, 108.9]
target_positions = [0, 1, 1, 0]

# Estado inicial: todo el capital está en efectivo.
cash = initial_capital
quantity = 0.0

# Guardaremos el valor de la cartera después de cada apertura.
equity_history = []

for price, target_position in zip(
    open_prices, target_positions, strict=True
):
    if target_position == 1 and quantity == 0.0:
        # Queremos invertir y todavía no tenemos unidades.
        # Calculamos el resultado de ejecutar la compra.
        buy_result = execute_buy_all_cash(
            cash=cash,
            price=price,
            commission_rate=commission_rate,
        )
        # Actualizamos el estado de la cartera con ese resultado.
        cash = buy_result["cash_after"]
        quantity = buy_result["quantity"]

    elif target_position == 0 and quantity > 0:
        # Queremos salir y todavía tenemos unidades.
        # Calculamos el resultado de ejecutar la venta.
        sell_result = execute_sell_all(
            quantity= quantity,
            price=price,
            commission_rate=commission_rate,
        )
        # Actualizamos el estado de la cartera con ese resultado.
        cash = cash + sell_result["cash_received"]
        quantity = sell_result["quantity_after"]

    # Si ninguna condición se cumple, mantenemos la cartera.
    equity = cash + quantity * price
    equity_history.append(equity)

    print(
        f"Price: {price:.2f} | "
        f"Target: {target_position} | "
        f"Cash: {cash:.6f} | "
        f"Quantity: {quantity:.6f} | "
        f"Equity: {equity:.6f}"
    )

# Valores esperados para este ejemplo, calculados independientemente.
expected_equity = [
    1000.0,
    999.000999000999,
    1098.901098901099,
    988.021978021978,
]

tolerance = 1e-8

assert len(equity_history) == len(expected_equity), (
    "The simulation must produce one equity value per opening."
)

for step, (actual, expected) in enumerate(
    zip(equity_history,expected_equity,strict=True),
    start=1
):
    assert abs(actual - expected) < tolerance, (
        f"Unexpected equity at step {step}: "
        f"expected {expected}, got {actual}."
    )

assert quantity == 0.0, (
    "The portfolio must hold no units after the final sale."
)

assert abs(cash - expected_equity[-1]) < tolerance, (
    "Final cash does not match the expected sale proceeds."
)

print("Portfolio accounting checks passed.")