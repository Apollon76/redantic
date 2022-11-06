import struct
from typing import Iterator, MutableMapping, Type, TypeVar, Union

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


KeyType = TypeVar('KeyType', bound=Serializable)
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


class RedisDict(MutableMapping[KeyType, ValueType]):
    def __init__(self, client: Redis, name: str, key_type: Type[KeyType], value_type: Type[ValueType]):  # type: ignore
        self._client = client
        self._name = name
        self._key_type = key_type
        self._t = value_type

    def __getitem__(self, item: Serializable) -> ValueType:
        data = self._client.hget(self._name, serialize(item))
        if data is None:
            raise KeyError()
        return deserialize(data, self._t)

    def __setitem__(self, key: Serializable, value: ValueType) -> None:
        self._client.hset(self._name, serialize(key), serialize(value))

    def __len__(self) -> int:
        return self._client.hlen(self._name)

    def __iter__(self) -> Iterator[KeyType]:
        return (deserialize(e, t=self._key_type) for e, _ in self._client.hscan_iter(name=self._name))

    def __delitem__(self, key: Serializable) -> None:
        self._client.hdel(self._name, serialize(key))

    def clear(self) -> None:
        self._client.delete(self._name)

    def __contains__(self, o: object) -> bool:
        if not isinstance(o, (bytes, str, int, float, BaseModel)):
            return False
        return self._client.hexists(self._name, serialize(o))
