# temp file. To be removed after datas are in the database

import json


def get_json_data(file_name):
    try:
        with open(file_name) as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        return []


def extract_values_in_list(datas, indicator_names):
    values = {"date": []}

    for name in indicator_names:
        values[name] = []

    for data in datas:
        values[data["name"]].append(data["value"])
        if data["date"] not in values["date"]:
            values["date"].append(data["date"])

    return values
