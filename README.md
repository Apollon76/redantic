# redantic
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Simple redis storage for pydantic objects with an interface of the MutableMapping.

## Examples

```python
from redantic import RedisDict
from pydantic import BaseModel
from redis import Redis

class Car(BaseModel):
    price: float
    model: str

CarId = int

client = Redis()
d = RedisDict[CarId, Car](client=client, name='car_collection', key_type=CarId, value_type=Car)
d[1] = Car(price=100.5, model='a')
d[2] = Car(price=200, model='b')

print(len(d))
for i in d:
    print(d[i])
```

You can also use pydantic object as a key.

```python
class CarId(BaseModel):
    id: int
    type: str

d[CarId(id=1, type='some_type')] = Car(price=100.5, model='a')
```