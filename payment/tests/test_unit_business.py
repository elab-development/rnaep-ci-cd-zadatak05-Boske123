"""Unit: izolovana poslovna logika bez I/O."""

import pytest

from business import compute_order_financials


@pytest.mark.parametrize(
    "unit_price,quantity,expected_fee,expected_total",
    [
        (100.0, 1, 20.0, 120.0),
        (50.0, 2, 10.0, 120.0),
        (0.0, 5, 0.0, 0.0),
    ],
)
def test_compute_order_financials(unit_price, quantity, expected_fee, expected_total):
    result = compute_order_financials(unit_price, quantity)
    assert result["price"] == unit_price
    assert result["fee"] == pytest.approx(expected_fee)
    assert result["total"] == pytest.approx(expected_total)
