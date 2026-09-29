from src.backtesting.execution import execute_buy_all_cash, execute_sell_all

initial_cash = 1000.0
entry_price = 110.0
intermediate_price = 121.0
exit_price = 108.90
commission_rate = 0.001

buy_result = execute_buy_all_cash(
    cash=initial_cash,
    price=entry_price,
    commission_rate=commission_rate,
)

quantity = buy_result["quantity"]
entry_notional = buy_result["notional"]
entry_fee = buy_result["fee"]
cash_after_entry = buy_result["cash_after"]

equity_at_121 =  cash_after_entry + quantity * intermediate_price

sell_result = execute_sell_all(
    quantity=quantity,
    price=exit_price,
    commission_rate=commission_rate,
)

exit_notional = sell_result["notional"]
exit_fee = sell_result["fee"]
final_cash = cash_after_entry + sell_result["cash_received"]
quantity_after_exit = sell_result["quantity_after"]

net_pnl = final_cash - initial_cash

print("Quantity: ", quantity)
print("Entry notional: ", entry_notional)
print("Entry fee: ", entry_fee)
print("Cash after entry: ", cash_after_entry)
print("Equity at 121: ", equity_at_121)
print("Exit notional: ", exit_notional)
print("Exit fee: ", exit_fee)
print("Final cash : ", final_cash)
print("Net PnL: ", net_pnl)

gross_pnl = exit_notional - entry_notional
net_pnl_from_trade = gross_pnl - entry_fee - exit_fee

tolerance = 1e-8

# La compra y su comisión consumen el capital disponible.
assert abs(
    entry_notional + entry_fee - initial_cash
) < tolerance, (
    "Entry notional and fee do not match the available cash"
)

# El saldo restante debe ser prácticamente cero.
assert abs(cash_after_entry) < tolerance, (
    "Unexpected cash balance after entry"
)

# Resultado esperado calculado previamente a mano.
assert abs(final_cash - 988.021978021978) < tolerance, (
    "Final cash does not match the reference calculation"
)

# El resultado por operación debe coincidir con el cambio de capital.
assert abs(net_pnl_from_trade - net_pnl) < tolerance, (
    "Trade PnL does not reconcile with the change in cash"
)

assert quantity_after_exit == 0.0, (
    "A full sale must leave no remaining quantity"
)

final_equity = final_cash + quantity_after_exit * exit_price

assert abs(final_equity - final_cash) < tolerance, (
    "Equity must equal cash when no asset is held"
)

print("Execution accounting checks passed.")

buy_without_fee = execute_buy_all_cash(
    cash=1000.0,
    price=100.0,
    commission_rate=0.0,
)

assert abs(buy_without_fee["quantity"] - 10.0) < tolerance
assert abs(buy_without_fee["notional"] - 1000.0) < tolerance
assert abs(buy_without_fee["fee"]) < tolerance
assert abs(buy_without_fee["cash_after"]) < tolerance

print("Buy without commission checks passed.")

try:
    execute_buy_all_cash (
        cash=1000.0,
        price=0.0,
        commission_rate=0.001,
    )

except ValueError as error:
    assert "Price must be finite and greater than zero" in str(error), (
        f"Unexpected validation error: {error}"
    )
    print("Zero price correctly rejected.")

else:
    raise AssertionError(
        "The buy function accepted a zero price."
    )

sell_without_fee = execute_sell_all(
    quantity=10.0,
    price=110.0,
    commission_rate=0.0,
)

assert sell_without_fee["notional"] - 1100.0 < tolerance
assert sell_without_fee["fee"] == 0.0
assert sell_without_fee["cash_received"] - 1100.0 < tolerance
assert sell_without_fee["quantity_after"] == 0.0

print("Sell without commission checks passed.")

try:
    execute_sell_all (
        quantity=0.0,
        price=110.0,
        commission_rate=0.001,
    )

except ValueError as error:
    assert "Quantity must be finite and greater than zero" in str(error), (
        f"Unexpected validation error: {error}"
    )
    print("Zero quantity correctly rejected.")

else:
    raise AssertionError(
        "The sell function accepted a zero quantity."
    )