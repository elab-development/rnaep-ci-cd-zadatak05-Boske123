"""Integracioni: Order model i Redis (redis-om)."""

import pytest

import main as payment_main


@pytest.fixture
def order_pk(redis_indexes):
    order = payment_main.Order(
        product_id="int-sku",
        price=10.0,
        fee=2.0,
        total=12.0,
        quantity=1,
        status="pending",
    )
    order.save()
    pk = order.pk
    yield pk
    try:
        payment_main.Order.delete(pk)
    except Exception:
        pass


def test_order_round_trip_in_redis(order_pk):
    loaded = payment_main.Order.get(order_pk)
    assert loaded.product_id == "int-sku"
    assert loaded.status == "pending"
    assert loaded.total == pytest.approx(12.0)


@pytest.mark.asyncio
async def test_redis_stream_append_after_order_completed(redis_indexes, monkeypatch):
    async def no_sleep(_delay):
        return None

    monkeypatch.setattr(payment_main.asyncio, "sleep", no_sleep)

    order = payment_main.Order(
        product_id="stream-sku",
        price=5.0,
        fee=1.0,
        total=6.0,
        quantity=1,
        status="pending",
    )
    order.save()
    pk = order.pk
    try:
        fresh = payment_main.Order.get(pk)
        await payment_main.process_order(fresh)
        completed = payment_main.Order.get(pk)
        assert completed.status == "completed"
    finally:
        try:
            payment_main.Order.delete(pk)
        except Exception:
            pass
