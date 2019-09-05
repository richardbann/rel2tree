import json

from rel2tree import F, groupkey


data = [
  {"name": "Jane", "city": "New York", "sales": 23},
  {"name": "Joe", "city": "New York", "sales": 11},
  {"name": "Jane", "city": "Chicago", "sales": 21},
  {"name": "Jane", "city": "New York", "sales": 4},
  {"name": "Joe", "city": "New York", "sales": 13},
  {"name": "Joe", "city": "Chicago", "sales": 31},
  {"name": "Jane", "city": "New York", "sales": 7},
]

f = F().groupby(lambda x: x["name"], F().dict({
    "name": groupkey(),
    "cities": F().groupby(lambda x: x["city"], F().dict({
        "city": groupkey(),
        "sales": F().map(lambda x: x["sales"]).t(sum)
    })),
    "sum": F().map(lambda x: x["sales"]).t(sum)
}))

print(json.dumps(f(data)))


data = [1, 2, 3, 4]
f = F().dict({
    "list": F(),
    "even": F().filter(lambda x: x % 2 == 0),
    "odd": F().filter(lambda x: x % 2 != 0),
})
print(json.dumps(f(data)))


data = range(10)
f = F().groupby(lambda x: x % 2)
print(json.dumps(f(data)))


data = range(10)
f = F().groupby(lambda x: x % 2, F().t(sum))
print(json.dumps(f(data)))
