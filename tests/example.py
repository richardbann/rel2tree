import json

from rel2tree import f


data = [
    {"name": "Jane", "city": "New York", "sales": 23},
    {"name": "Joe", "city": "New York", "sales": 11},
    {"name": "Jane", "city": "Chicago", "sales": 21},
    {"name": "Jane", "city": "New York", "sales": 4},
    {"name": "Joe", "city": "New York", "sales": 13},
    {"name": "Joe", "city": "Chicago", "sales": 31},
    {"name": "Jane", "city": "New York", "sales": 7},
]

summary = {}
for record in data:
    this_person = summary.setdefault(record["name"], {
        "name": record["name"],
        "cities": {},
        "sum": 0,
    })
    this_person_cities = this_person["cities"].setdefault(record["city"], {
        "city": record["city"],
        "sum": 0,
    })
    this_person_cities["sum"] += record["sales"]
    this_person["sum"] += record["sales"]
summary = list(summary.values())
for person in summary:
    person["cities"] = list(person["cities"].values())

print(json.dumps(summary))

#

summary = f.groupby(lambda x: x["name"], f.dict({
    "name": f.groupkey(),
    "cities": f.groupby(lambda x: x["city"], f.dict({
        "city": f.groupkey(),
        "sum": f.map(lambda x: x["sales"]).t(sum)
    })),
    "sum": f.map(lambda x: x["sales"]).t(sum)
}))

print(json.dumps(summary(data)))

#

numbers = range(15)
summary = f.dict({
    "even": f.filter(lambda x: (x % 2 == 0)),
    "odd": f.filter(lambda x: (x % 2 == 1)),
})

print(json.dumps(summary(numbers)))

#

summary = f.groupby(lambda x: x % 3)

print(json.dumps(summary(numbers)))

#

summary = f.groupby(lambda x: x % 3, f.dict({
  "remainder": f.groupkey(),
  "numbers": f
}))

print(json.dumps(summary(numbers)))
