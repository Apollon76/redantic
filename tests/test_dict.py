import pytest
from pydantic import BaseModel
from redis.client import Redis

from redantic.storage import RedisDict


@pytest.fixture()
def client():
    return Redis()


class KeyModel(BaseModel):
    data: str
    ind: int


class ValueModel(BaseModel):
    x: int
    y: float
    s: str


@pytest.mark.parametrize('key', [1, 5.1, 'kek', b'lol', KeyModel(data='kek', ind=1)])
@pytest.mark.parametrize(
    ('value', 't'),
    [
        (3, int),
        (1.3, float),
        ('lol', str),
        (b'kek', bytes),
        (ValueModel(x=1, y=1.3, s='kek'), ValueModel),
    ],
)
def test_get_set(key, value, t, client: Redis):
    d = RedisDict[t](client=client, name='test_collection', t=t)
    d[key] = value
    assert d[key] == value
