# rel2tree

Convert a list of records to a `JSON`-like structure.

## Tutorial

Let's suppose you have a set of data:

```py
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

```py
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
set and building the final structure. This code is far from
declarative (looking at the code itself you can not easily say
the final data structure) and if the structure of the data gets
more complex, or your requirements changes, your code can blow
up fast.

Let's see how you do it with `rel2tree`:

```py
f = F().groupby(lambda x: x["name"], F().dict({
    "name": groupkey(),
    "cities": F().groupby(lambda x: x["city"], F().dict({
        "city": groupkey(),
        "sales": F().map(lambda x: x["sales"]).t(sum)
    })),
    "sum": F().map(lambda x: x["sales"]).t(sum)
}))

result = f(data)
```

The code above can be tricky for the first sight, but definitively
much more declarative.

## `map`, `filter`, `sort`

The most basic usage of `rel2tree` is mapping a list.
Say we have a list and want to duplicate of its elements.

```py
data = [1, 2, 3, 4]
result = list(map(lambda x: 2 * x, data))
```

With `rel2tree` it looks like this:

```py
data = [1, 2, 3, 4]
f = F().map(lambda x: 2 * x)
result = f(data)
```

Note that in the above example `f` can be thought of as a
recipe. It can be reused with a different set of data any time.

Now we can further modify our list by mapping again. Say we
want to add 5 to each elements:

```py
f2 = f.map(lambda x: x + 5)
result = f2(data)
result = [7, 9, 11, 13]
```

To filter our list, we need a function that returns `True` for
elements to keep in the list.

```py
f3 = f2.filter(lambda x: x < 10)
result = f3(data)
result = [7, 9]
```

Sorting works the same as python's `sorted` function:

```py
f4 = f3.sort(lambda x: -x)
result = f4(data)
result = [9, 7]
```

## `dict`

The usage of `dict` is easiest to describe with an example:

```py
data = [1, 2, 3, 4]
f = F().dict({
    "list": F(),
    "even": F().filter(lambda x: x % 2 == 0),
    "odd": F().filter(lambda x: x % 2 != 0),
})
result = f(data)
```

Here is the result:

```json
{
  "list": [1, 2, 3, 4],
  "even": [2, 4],
  "odd": [1, 3]
}
```

For each key in the dictionary we specify an `F` expression.
The full list will be processed by each of these `F`-s and the
result will be a single dictionary.

## `groupby`

`groupby` needs a function as its first argument. This function
will be called with each items in the list to calculate a group key. Items with the same group keys are collected in lists.
The result will be a list of these groups.

```py
data = range(10)
f = F().groupby(lambda x: x % 2)
print(json.dumps(f(data)))
```

```json
[[0, 2, 4, 6, 8], [1, 3, 5, 7, 9]]
```

An `F` can be given to `groupby` as the second argument.
In this case each list will be given to this `F`. To continue
our example above, we may calculate the sum of even and odd
numbers:

```py
data = range(10)
f = F().groupby(lambda x: x % 2, F().t(sum))
print(json.dumps(f(data)))
# [20, 25]
```

This last example shows how to apply an arbitrary function
on the whole list: `f.t(func)`. In this case we get
`func(lst)` as a result. `t` means `f.t(func)` does not return
an `F` expression but an instance of class `T`. The difference
is that you can not further chain `T`-s, they are 'terminating'
the chain. Most `F` methods assume they will be used with lists.
If you know your function will return a list which you may
want to further manipulate by chaining, you can use
`f.f(func)`.

## `const` and `groupkey`

TODO
