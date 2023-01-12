from collections import ChainMap, defaultdict

from django.db.models import Count

from lacommunaute.utils.enums import PeriodAggregation


def count_objects_per_period(qs, name, period=PeriodAggregation.MONTH):
    if period == PeriodAggregation.WEEK:
        ft = "%Y-%W"
    elif period == PeriodAggregation.MONTH:
        ft = "%b %Y"
    else:
        raise ValueError("unknown period")

    # [{'period': 'Dec 2022', '<model name>': 59}, {'period': 'Jan 2023', '<model name>': 25}]
    qs = qs.values("period").annotate(number=Count("id")).values("period", "number").order_by("period")
    return [{"period": item["period"].strftime(ft), name: item["number"]} for item in qs]


def format_counts_of_objects_for_timeline_chart(datas):

    # aggregate counts of objects per month in a dict
    # {'Dec 2022': {'period': 'Dec 2022', 'users': 59, 'posts': 5, 'upvotes': 3},
    #  'Jan 2023': {'period': 'Jan 2023', 'users': 25, 'posts': 39, 'upvotes': 11, 'pollvotes': 26}
    # }
    merged_periods = defaultdict(dict)
    for data in datas:
        merged_periods[data["period"]] |= data

    # objects name
    names = dict(ChainMap(*datas)).keys()

    # extract one array per object name
    # {'period': ['Dec 2022', 'Jan 2023'],
    #  'pollvotes': [0, 26],
    #  'upvotes': [3, 11],
    #  'posts': [5, 39],
    #  'users': [59, 25]
    # }
    chart_arrays = {}
    for name in names:
        chart_arrays[name] = [merged_periods[k].get(name, 0) for k in merged_periods.keys()]

    return chart_arrays
