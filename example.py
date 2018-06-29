from rel2tree.core import Dict, Field, GroupBy, GroupKey, Computed
from rel2tree.fields import GroupByFields, SumField


report = Dict(
    even=Field(_where=lambda x: not (x % 2)),
    odd=Field(_where=lambda x: x % 2),
    sum=Field(_aggregator=sum),
    comp=Computed(),
    group=GroupBy(
        _groupkey=lambda x: x % 2,
        _sortkey=lambda x: -x,
        field=Dict(
            key=GroupKey(),
            values=Field(),
        ))
)
report.feed([1, 2, 3])
print(report.get())

report = GroupByFields('region', field=Dict(
        region=GroupKey(),
        total=SumField('amount'),
    )
)
report.feed([
    {'region': 'east', 'amount': 5},
    {'region': 'west', 'amount': 2},
    {'region': 'east', 'amount': 3},
    {'region': 'west', 'amount': 4},
])
print(report.get())
