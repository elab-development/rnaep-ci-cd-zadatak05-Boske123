"""Unit: kreiranje porudžbine sa mock-ovanim HTTP klijentom (bez Redis upisa)."""

from unittest.mock import MagicMock

import pytest

import main as payment_main
from fastapi import BackgroundTasks


@pytest.mark.asyncio
async def test_create_order_uses_inventory_and_computes_amounts(monkeypatch):
    class FakeResponse:
        status_code = 200

        def json(self):
            return {"price": 40.0}

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, url):
            assert "/products/sku-1" in url
            return FakeResponse()

    monkeypatch.setattr(
        payment_main.httpx,
        "AsyncClient",
        lambda *args, **kwargs: FakeAsyncClient(),
    )

    saved = []

    def fake_save(self):
        saved.append(self)

    monkeypatch.setattr(payment_main.Order, "save", fake_save)

    tasks = BackgroundTasks()
    monkeypatch.setattr(tasks, "add_task", MagicMock())

    order = await payment_main.create_order({"id": "sku-1", "quantity": 4}, tasks)

    assert order.product_id == "sku-1"
    assert order.quantity == 4
    assert order.fee == pytest.approx(8.0)
    assert order.total == pytest.approx(1.2 * 40.0 * 4)
    assert saved == [order]
    tasks.add_task.assert_called_once()
