from collections import ChainMap, defaultdict

from django.db.models import Count

from lacommunaute.utils.enums import PeriodAggregation


def get_strftime(period=PeriodAggregation.MONTH):
    if period == PeriodAggregation.WEEK:
        return "%Y-%W"
    if period == PeriodAggregation.MONTH:
        return "%b %Y"
    raise ValueError("unknown period")


def count_objects_per_period(qs, name):

    qs = qs.values("period").annotate(number=Count("id")).values("period", "number").order_by("period")
    return [{"period": item["period"], name: item["number"]} for item in qs]


def format_counts_of_objects_for_timeline_chart(datas, period=PeriodAggregation.MONTH):
    # TODO vincentporte : manage period without datas between oldest period and now

    merged_periods = defaultdict(dict)
    for data in datas:
        merged_periods[data["period"]] |= data

    names = dict(ChainMap(*datas)).keys()

    chart_arrays = {}
    for name in names:
        chart_arrays[name] = [merged_periods[k].get(name, 0) for k in sorted(merged_periods.keys())]

    # datetime must be formatted AFTER being sorted
    ft = get_strftime(period)
    chart_arrays["period"] = [v.strftime(ft) for v in chart_arrays["period"]]

    return chart_arrays
