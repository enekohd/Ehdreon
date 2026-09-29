import math

def execute_buy_all_cash(
        cash: float,
        price: float,
        commission_rate: float,
) -> dict[str,float]:
    """Simula una compra usando todo el efectivo disponible.

    Permite cantidades fraccionarias y cobra una comisión
    proporcional al importe comprado.
    """

    if not math.isfinite(cash) or cash <= 0:
        raise ValueError("Cash must be finite and greater than zero.")
    
    if not math.isfinite(price) or price <= 0:
        raise ValueError("Price must be finite and greater than zero.")

    if(
        not math.isfinite(commission_rate) 
        or not 0 <= commission_rate < 1
    ):
        raise ValueError(
            "Commission rate must be finite and between 0 and 1, excluding 1"
        )

    quantity = cash / (price * (1 + commission_rate))
    notional = quantity * price
    fee = notional * commission_rate
    cash_after = cash - notional - fee

    return {
        "quantity": quantity,
        "notional": notional,
        "fee": fee,
        "cash_after": cash_after
    }

def execute_sell_all(
        quantity: float,
        price: float,
        commission_rate,
) -> dict[str,float]:
    """Simula la venta completa de una cantidad del activo.

    Cobra una comisión proporcional al importe vendido.
    Devuelve el efectivo recibido y la cantidad restante.
    """

    if not math.isfinite(quantity) or quantity <= 0:
        raise ValueError("Quantity must be finite and greater than zero.")

    if not math.isfinite(price) or price <= 0:
        raise ValueError("Price must be finite and greater than zero.")

    if (
        not math.isfinite(commission_rate)
        or not 0 <= commission_rate < 1
    ):
        raise ValueError(
            "Commission rate must be finite and between 0 and 1, excluding 1"
        )

    notional = quantity * price
    fee = notional * commission_rate
    cash_received = notional - fee

    return {
        "quantity_sold": quantity,
        "notional": notional,
        "fee": fee,
        "cash_received": cash_received,
        "quantity_after": 0.0,
    }
    
