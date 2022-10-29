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
    def __init__(self, client: Redis, name: str, t: Type[ValueType]):  # type: ignore
        self._client = client
        self._name = name
        self._t = t

    def __getitem__(self, item: Serializable) -> ValueType:
        data = self._client.hget(self._name, serialize(item))
        if data is None:
            raise KeyError()
        return deserialize(data, self._t)

    def __setitem__(self, key: Serializable, value: ValueType) -> None:
        self._client.hset(self._name, serialize(key), serialize(value))

    def __len__(self) -> int:
        return self._client.hlen(self._name)

    def __delitem__(self, key: Serializable) -> None:
        self._client.hdel(self._name, serialize(key))

    def clear(self):
        self._client.delete(self._name)

    # def update(self, *args, **kwargs):
    #     return self.__dict__.update(*args, **kwargs)

    # def keys(self):
    #     return self._client.hkeys(self._name)

    def values(self) -> list[ValueType]:
        return self._client.hgetall(self._name)

    # def items(self):
    #     return self.__dict__.items()

    # def pop(self, *args):
    #     return self.__dict__.pop(*args)

    def __contains__(self, item: Serializable) -> bool:
        return self._client.hexists(self._name, serialize(item))

    # def __iter__(self):
    #     return iter(self.__dict__)
