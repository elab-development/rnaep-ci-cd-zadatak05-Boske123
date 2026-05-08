import os

import pytest

# Mora pre uvoza modula koji koriste database.py
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")


@pytest.fixture(scope="module")
def redis_indexes():
    """RediSearch indeksi (redis-om); zahteva Redis Stack ili ekvivalent."""
    from redis_om import Migrator

    Migrator().run()
