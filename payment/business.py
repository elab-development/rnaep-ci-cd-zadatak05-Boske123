"""Čista poslovna logika za izračunavanje iznosa porudžbine (bez I/O)."""


def compute_order_financials(unit_price: float, quantity: int) -> dict[str, float]:
    """Vraća polja cena, naknada (fee) i ukupno za jednu stavku porudžbine."""
    fee = 0.2 * unit_price
    total = 1.2 * unit_price * quantity
    return {"price": unit_price, "fee": fee, "total": total}
