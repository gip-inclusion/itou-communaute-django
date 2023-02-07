# temp file. To be removed after datas are in the database

import json


def get_json_data(file_name):
    try:
        with open(file_name) as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        return []


def extract_values_in_list(datas):
    values = {
        "date": [],
        "nb_unique_contributors": [],
        "nb_uniq_visitors": [],
        "nb_uniq_active_visitors": [],
        "nb_engagment_events": [],
    }
    for data in datas:
        values[data["name"]].append(data["value"])
        if data["date"] not in values["date"]:
            values["date"].append(data["date"])
    return values
