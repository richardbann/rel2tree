# rel2tree

Convert your list of data into `JSON` serializable structure.

## Motivation

Let's suppose you have a set of data given as a list of dicts:

```py
import json

[
  {"name": "Jane", "city": "New York", "sales": 23},
  {"name": "Joe", "city": "New York", "sales": 11},
  {"name": "Jane", "city": "Chicago", "sales": 21},
  {"name": "Jane", "city": "New York", "sales": 4},
  {"name": "Joe", "city": "New York", "sales": 13},
  {"name": "Joe", "city": "Chicago", "sales": 31},
  {"name": "Jane", "city": "New York", "sales": 7},
]
```

You may want a nice summary, something like this:

```json
[
  {
    "name": "Jane",
    "cities": [
      {
        "city": "New York",
        "sales": 34
      },
      {
        "city": "Chicago",
        "sales": 21
      }
    ],
    "sum": 55
  },
  {
    "name": "Joe",
    "cities": [
      {
        "city": "New York",
        "sales": 24
      },
      {
        "city": "Chicago",
        "sales": 31
      }
    ],
    "sum": 55
  }
]
```

This can be done relatively easily by iterating over the data
set and building the final structure.

```py
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
    this_person["sum"] += record["sum"]
summary = list(summary.values())
for person in summary:
    person["cities"] = list(person["cities"].values())

print(json.dumps(summary))
```

Although the above code works well, but it has some problems.

- Not declarative: by looking at the code it is not trivial to tell the final data
  structure.
- Error-prone.
- The complexity grows with more complex business logic
  or by adding an additional level.
- Not reusable.

Let's see how you do it with `rel2tree`:

```py
from rel2tree import f  # NOQA

summary = f.groupby(lambda x: x["name"], f.dict({
    "name": f.groupkey(),
    "cities": f.groupby(lambda x: x["city"], f.dict({
        "city": f.groupkey(),
        "sum": f.map(lambda x: x["sales"]).t(sum)
    })),
    "sum": f.map(lambda x: x["sales"]).t(sum)
}))

print(json.dumps(summary(data)))
```

## Tutorial

### `map`, `sort`, `filter`, `distinct`

The only object one can import from `rel2tree` is `f`, which is of type `F`
so we will call it an `F` object.
`f` is callable, but - on it's own does nothing:

```py
print(f(2))
# 2
```

Let's say we have a list of numbers (`numbers`) and we want
to duplicate all of it's elements. This can be done in many ways:

- using a list comprehension:
  ```py
  out = [2 * x for x in numbers]
  ```
- using map:
  ```py
  out = map(lambda x: 2 * x, numbers)
  ```
- defining a function (for reusability)
  ```py
  import functools
  dup = functools.partial(map, lambda x: 2 * x)
  out = dup(numbers)
  ```

Using an `f` it looks like this:

```py
numbers = range(15)
dup = f.map(lambda x: 2 * x)
out = dup(numbers)
```

This simply made our third approach a little more terse.

Now what if our task is to add 1 to each element after
duplication? Can we reuse our `dup` function? As
the result of `f.map` has the same type as `f`, we can
use map again:

```py
dupplus1 = dup.map(lambda x: x + 1)
```

`f.sort(fnc)` sorts our list based on the value of `fnc`
applied to the items (just as the `key` argument of python's)
`sorted`. `f.filter(fnc)` keeps only those `i` items, where
`fnc(i)` is ture(ish). These methods also return `F`s
(internally the type of `f` is `F`) so they are chainable.
The `F` below first duplicates, then filters out big
numbers and finally sorts them. (`f.sort`, without a function sorts the elements.)

```py
f.map(lambda x: 2 * x).filter(lambda x: x < 10).sort()
```

### `dict`

Back to our `numbers`, but with the desired output of

```json
{
  "even": [0, 2, 4, 6, 8, 10, 12, 14],
  "odd": [1, 3, 5, 7, 9, 11, 13]
}
```

We can combine the dict method to achive this:

```py
summary = f.dict({
    "even": f.filter(lambda x: (x % 2 == 0)),
    "odd": f.filter(lambda x: (x % 2 == 1)),
})
```

If the dictionary values are `F` objects, those objects will be called with
the input list to form the final values, otherwise the values will be left as is.

### `groupby`

To generalize the above example, we can group our numbers based on the remainder
devided by, say, 3:

```py
summary = f.groupby(lambda x: x % 3)
# [[0, 3, 6, 9, 12], [1, 4, 7, 10, 13], [2, 5, 8, 11, 14]]
```

To make it more informative, the desired output should be:

```json
[
  { "remainder": 0, "numbers": [0, 3, 6, 9, 12] },
  { "remainder": 1, "numbers": [1, 4, 7, 10, 13] },
  { "remainder": 2, "numbers": [2, 5, 8, 11, 14] }
]
```

This can be done by using `groupkey`:

```py
summary = f.groupby(lambda x: x % 3, f.dict({
  "remainder": f.groupkey(),
  "numbers": f
}))
```

`f.groupkey(level=0)` gives the deepest level group key, while `f.groupkey(1)`
is the one level above group key in case of nested `groupby`'s.
