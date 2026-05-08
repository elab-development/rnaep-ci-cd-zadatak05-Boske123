"""Funkcionalni: HTTP API nad celim servisom (FastAPI TestClient + Redis)."""

import asyncio

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

import main as payment_main


@pytest.fixture
def client(redis_indexes):
    return TestClient(payment_main.app)


@pytest.fixture
def fast_payment(monkeypatch):
    async def no_sleep(_delay):
        return None

    monkeypatch.setattr(asyncio, "sleep", no_sleep)


@respx.mock
def test_get_order_404(client):
    r = client.get("/orders/nonexistent-id-12345")
    assert r.status_code == 404


@respx.mock
def test_create_order_happy_path(client, fast_payment):
    respx.get("http://localhost:8000/products/api-sku").mock(
        return_value=httpx.Response(200, json={"price": 100.0, "name": "Test"})
    )

    r = client.post("/orders", json={"id": "api-sku", "quantity": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["product_id"] == "api-sku"
    assert body["quantity"] == 2
    assert body["status"] == "pending"
    assert body["fee"] == pytest.approx(20.0)
    assert body["total"] == pytest.approx(240.0)

    pk = body["pk"]
    try:
        loaded = payment_main.Order.get(pk)
        assert loaded.status == "completed"
    finally:
        try:
            payment_main.Order.delete(pk)
        except Exception:
            pass


@respx.mock
def test_create_order_inventory_not_found(client):
    respx.get("http://localhost:8000/products/missing").mock(
        return_value=httpx.Response(404)
    )

    r = client.post("/orders", json={"id": "missing", "quantity": 1})
    assert r.status_code == 400
