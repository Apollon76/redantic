import struct
from typing import Generic, Type, TypeVar, Union

from pydantic import BaseModel
from redis import Redis

Serializable = Union[bytes, str, int, float, BaseModel]


def serialize(entity: Serializable) -> bytes:
    if isinstance(entity, BaseModel):
        return entity.json().encode('utf-8')
    if isinstance(entity, str):
        return entity.encode('utf-8')
    if isinstance(entity, bytes):
        return entity
    if isinstance(entity, int):
        return str(entity).encode('utf-8')
    if isinstance(entity, float):
        return struct.pack("d", entity)
    raise ValueError('Unknown type')


ValueType = TypeVar('ValueType', bound=Serializable)


def deserialize(entity: bytes, t: Type[ValueType]) -> ValueType:
    if issubclass(t, bytes):
        return t(entity)  # type: ignore
    if issubclass(t, str):
        return t(entity.decode('utf-8'))  # type: ignore
    if issubclass(t, int):
        return t(entity.decode('utf-8'))  # type: ignore
    if issubclass(t, BaseModel):
        return t.parse_raw(entity)  # type: ignore
    if issubclass(t, float):
        return struct.unpack('d', entity)[0]  # type: ignore
    raise TypeError()


class RedisDict(Generic[ValueType]):
    def __init__(self, client: Redis, t: Type[ValueType]):  # type: ignore
        self._client = client
        self._t = t

    def __getitem__(self, item: Serializable) -> ValueType:
        data = self._client.get(serialize(item))
        if data is None:
            raise KeyError()
        return deserialize(data, self._t)

    def __setitem__(self, key: Serializable, value: ValueType) -> None:
        self._client.set(serialize(key), serialize(value))
