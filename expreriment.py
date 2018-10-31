#!/usr/bin/env python3
import json

from rel2tree.core import Dict, ListOf
from rel2tree.fields import (
    SumField, GroupByFields, GroupKeyField, field, Const
)


d = Dict(
    const_a=Const('a'),
    sum_b=SumField('b'),
    grp=GroupByFields(['group'], Dict(
        g=GroupKeyField('group'),
        sum_c=SumField('c'),
        in_group=ListOf(
            b=field('b')
        )
    ))
)
ret = d.feed([
    {'a': 1, 'b': 11, 'c': 111, 'group': 'A'},
    {'a': 2, 'b': 22, 'c': 222, 'group': 'A'},
    {'a': 3, 'b': 33, 'c': 333, 'group': 'A'},
    {'a': 4, 'b': 44, 'c': 444, 'group': 'B'},
    {'a': 5, 'b': 55, 'c': 555, 'group': 'B'},
    {'a': 6, 'b': 66, 'c': 666, 'group': 'B'},
]).get()
print(json.dumps(ret, indent=2))

###############################################################################

d = ListOf(
    a=lambda x: 2
)
ret = d.feed([1, 2, 3, 4, 5]).get()
print(json.dumps(ret, indent=2))
