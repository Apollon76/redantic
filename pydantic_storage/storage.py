from typing import Generic, TypeVar, Type, Any, Union

from pydantic import BaseModel
from redis import Redis


def serialize(entity) -> bytes:
    if isinstance(entity, BaseModel):
        return entity.json().encode('utf-8')
    if isinstance(entity, str):
        return entity.encode('utf-8')
    if isinstance(entity, bytes):
        return entity
    if isinstance(entity, int):
        return bytes(entity)
    return entity


def deserialize(entity: bytes, t: Type[Any]):
    if issubclass(t, bytes):
        return t(entity)
    if issubclass(t, str):
        return t(entity.decode('utf-8'))
    if issubclass(t, int):
        return t(entity)
    if issubclass(t, BaseModel):
        return t.parse_raw(entity)
    raise TypeError()


Serializable = Union[bytes, str, int, float, BaseModel]

ValueType = TypeVar('ValueType')


class RedisDict(Generic[ValueType]):
    def __init__(self, client: Redis, t: Type[ValueType]):
        self._client = client
        self._t = t

    def __getitem__(self, item: Serializable) -> ValueType:
        data = self._client.get(serialize(item))
        if data is None:
            raise KeyError()
        return deserialize(data, self._t)

    def __setitem__(self, key: Serializable, value: ValueType):
        self._client.set(serialize(key), serialize(value))


class A(BaseModel):
    x: int
    y: str


def main():
    # print(RedisDict[A].__args__)
    # return
    d = RedisDict[A](Redis(), A)
    d['asdf'] = A(x=1, y='kek')
    print(d['asdf'])
    print(d['lol'])

if __name__ == '__main__':
    main()
