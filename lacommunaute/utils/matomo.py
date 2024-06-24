import os
from datetime import date

import httpx
from dateutil.relativedelta import relativedelta
from django.conf import settings

from lacommunaute.forum.models import Forum
from lacommunaute.stats.models import ForumStat, Stat


def get_matomo_data(
    period,
    search_date,
    method,
    token_auth=settings.MATOMO_AUTH_TOKEN,
    **kwargs,
):
    """
    function to request matomo api
    * period: day, week, month
    * date: 2023-01-16
    * method: VisitSummary, Events.getCategory, VisitFrequency.get
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
    response = httpx.get(os.path.join(settings.MATOMO_BASE_URL, "index.php"), params=params)

    if response.status_code != 200:
        raise Exception(f"Matomo API error: {response.text}")

    try:
        return response.json()
    except Exception as e:
        raise Exception(f"Matomo API error: {response.text}") from e


def get_matomo_visits_data(period, search_date):
    """
    function to extract data from matomo api VisitSummary call & VisitFrequency.get
    """
    stats = []

    # collect nb_uniq_visitors
    data = get_matomo_data(period=period, search_date=search_date, method="VisitsSummary.get")
    stats.append(
        {
            "period": period,
            "date": search_date.strftime("%Y-%m-%d"),
            "name": "nb_uniq_visitors",
            "value": data.get("nb_uniq_visitors", 0),
        }
    )

    # collect nb_uniq_visitors_returning
    data = get_matomo_data(period=period, search_date=search_date, method="VisitFrequency.get")
    stats.append(
        {
            "period": period,
            "date": search_date.strftime("%Y-%m-%d"),
            "name": "nb_uniq_visitors_returning",
            "value": data.get("nb_uniq_visitors_returning", 0),
        }
    )

    return stats


def get_matomo_events_data(period, search_date, nb_uniq_visitors_key="nb_uniq_visitors", label=None):
    """
    function to extract data from matomo api Events.getCategory call
    """
    datas = get_matomo_data(period=period, search_date=search_date, method="Events.getCategory")
    if label:
        datas = list(filter(lambda d: d.get("label") == label, datas))

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


def get_matomo_forums_data(period, search_date, label=None, ids=[]):
    matomo_datas = get_matomo_data(period=period, search_date=search_date, method="Actions.getPageUrls")
    filtered_datas = [d for d in matomo_datas if d.get("label") == label]

    if len(filtered_datas) != 1:
        raise Exception(
            f"Matomo API err: get_matomo_forum_data {period} {search_date} {label}: {len(filtered_datas)} items found"
        )

    stats = {}
    for forum_data in filtered_datas[0].get("subtable", []):
        forum_id = int(forum_data["label"].split("-")[-1]) if forum_data["label"].split("-")[-1].isdigit() else None

        if forum_id and forum_id in ids:
            # ONE forum can have multiple slugs. We need to aggregate them.
            stats.setdefault(
                forum_id,
                {
                    "date": search_date.strftime("%Y-%m-%d"),
                    "period": period,
                    "visits": 0,
                    "entry_visits": 0,
                    "time_spent": 0,
                },
            )
            stats[forum_id]["visits"] += forum_data.get("nb_visits", 0)
            stats[forum_id]["entry_visits"] += forum_data.get("entry_nb_visits", 0)
            stats[forum_id]["time_spent"] += forum_data.get("sum_time_spent", 0)

    return [{"forum_id": k, **v} for k, v in stats.items()]


def collect_stats_from_matomo_api(period="day", from_date=date(2022, 12, 5), to_date=date.today()):
    """
    function to get stats from matomo api, day by day from 2022-10-31 to today
    """
    keys = {"day": "nb_uniq_visitors", "week": "sum_daily_nb_uniq_visitors", "month": "sum_daily_nb_uniq_visitors"}
    stats = []
    while from_date <= to_date:
        stats += get_matomo_visits_data(period, from_date)
        stats += get_matomo_events_data(period, from_date, nb_uniq_visitors_key=keys[period], label="engagement")
        print(f"Stats collected for {period} {from_date} ({len(stats)} stats collected)")

        if period == "day":
            from_date += relativedelta(days=1)
        elif period == "week":
            from_date += relativedelta(days=7)
        else:
            from_date += relativedelta(months=1)

    Stat.objects.bulk_create([Stat(**stat) for stat in stats])


def collect_forum_stats_from_matomo_api(period="week", from_date=date(2023, 10, 2), to_date=date.today()):
    if period != "week":
        raise ValueError("Only 'week' period is supported for forum stats collection.")

    forums_dict = {
        forum.id: forum
        for forum in Forum.objects.filter(parent__type=Forum.FORUM_CAT, level=1)
        | Forum.objects.filter(type=Forum.FORUM_CAT, level=0)
    }

    search_date = from_date
    while search_date <= to_date:
        forums_stats = get_matomo_forums_data(period, search_date, label="forum", ids=list(forums_dict.keys()))
        print(f"Stats collected for {period} {search_date} ({len(forums_stats)} stats collected)")

        forum_stats_objects = [
            {
                "date": stat["date"],
                "period": stat["period"],
                "forum": forums_dict[stat["forum_id"]],
                "visits": stat["visits"],
                "entry_visits": stat["entry_visits"],
                "time_spent": stat["time_spent"],
            }
            for stat in forums_stats
        ]
        ForumStat.objects.bulk_create([ForumStat(**stat) for stat in forum_stats_objects])

        search_date += relativedelta(days=7)
