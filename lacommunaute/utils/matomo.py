from datetime import date

import httpx
from dateutil.relativedelta import relativedelta
from django.conf import settings

from lacommunaute.forum_stats.models import Stat


def get_matomo_data(
    period,
    search_date,
    method,
    token_auth="anonymous",
    **kwargs,
):
    """
    function to request matomo api
    * period: day, week, month
    * date: 2023-01-16
    * method: VisitSummary, Events.getCategory
    """

    params = {
        "module": "API",
        "idSite": settings.MATOMO_SITE_ID,
        "method": method,
        "format": "JSON",
        "period": period,
        "date": search_date.strftime("%Y-%m-%d"),
        "token_auth": token_auth,
        "force_api_session": 1,
        "expanded": 1,
        "filter_limit": -1,
        **kwargs,
    }
    response = httpx.get(settings.MATOMO_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"Matomo API error: {response.text}")

    try:
        return response.json()
    except Exception as e:
        raise Exception(f"Matomo API error: {response.text}") from e


def get_matomo_visits_data(period, search_date):
    """
    function to extract data from matomo api VisitSummary call
    """
    data = get_matomo_data(period=period, search_date=search_date, method="VisitsSummary.get")
    return [
        {
            "period": period,
            "date": search_date.strftime("%Y-%m-%d"),
            "name": "nb_uniq_visitors",
            "value": data.get("nb_uniq_visitors", 0),
        }
    ]


def get_matomo_events_data(period, search_date, nb_uniq_visitors_key="nb_uniq_visitors"):
    """
    function to extract data from matomo api Events.getCategory call
    """
    datas = get_matomo_data(period=period, search_date=search_date, method="Events.getCategory")

    if not datas:
        return [
            {
                "period": period,
                "date": search_date.strftime("%Y-%m-%d"),
                "name": "nb_uniq_active_visitors",
                "value": 0,
            },
            {
                "period": period,
                "date": search_date.strftime("%Y-%m-%d"),
                "name": "nb_uniq_engaged_visitors",
                "value": 0,
            },
        ]

    stats = []

    for data in datas:
        nb_uniq_active_visitors = data.get(nb_uniq_visitors_key, 0)
        stat = {
            "period": period,
            "date": search_date.strftime("%Y-%m-%d"),
            "name": "nb_uniq_active_visitors",
            "value": nb_uniq_active_visitors,
        }
        stats.append(stat)

        subtable = data.get("subtable", None)

        if subtable:
            nb_uniq_engaged_visitors = nb_uniq_active_visitors - sum(
                [item.get(nb_uniq_visitors_key, 0) for item in subtable if item["label"] == "view"]
            )
            stat = {
                "period": period,
                "date": search_date.strftime("%Y-%m-%d"),
                "name": "nb_uniq_engaged_visitors",
                "value": nb_uniq_engaged_visitors,
            }
            stats.append(stat)
        else:
            stat = {
                "period": period,
                "date": search_date.strftime("%Y-%m-%d"),
                "name": "nb_uniq_engaged_visitors",
                "value": 0,
            }
            stats.append(stat)

    return stats


def collect_stats_from_matomo_api(period="day", from_date=date(2022, 12, 5), to_date=date.today()):
    """
    function to get stats from matomo api, day by day from 2022-10-31 to today
    """
    keys = {"day": "nb_uniq_visitors", "week": "sum_daily_nb_uniq_visitors", "month": "sum_daily_nb_uniq_visitors"}
    stats = []
    while from_date <= to_date:

        stats += get_matomo_visits_data(period, from_date)
        stats += get_matomo_events_data(period, from_date, nb_uniq_visitors_key=keys[period])
        print(f"Stats collected for {period} {from_date} ({len(stats)} stats collected)")

        if period == "day":
            from_date += relativedelta(days=1)
        elif period == "week":
            from_date += relativedelta(days=7)
        else:
            from_date += relativedelta(months=1)

    Stat.objects.bulk_create([Stat(**stat) for stat in stats])
