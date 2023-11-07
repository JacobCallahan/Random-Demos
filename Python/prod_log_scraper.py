"""Some utilities for scraping Satellite production logs"""
import argparse
from pathlib import Path


def log_to_dicts(log_path):
    """Convert a Satellite log file to a list of dict log entries"""
    dict_list = []
    log_entry = {}
    current_group = ""
    with log_path.open() as log_file:
        for line in log_file:
            if " Started " in line:
                current_group = "Started"
            elif " Processing " in line:
                current_group = "Processing"
            elif " Parameters:" in line:
                current_group = "Parameters"
            elif " Completed " in line:
                log_entry["Completed"] = line
                current_group = ""
                if "/api/" in log_entry["Started"]:
                    dict_list.append(log_entry)
                log_entry = {}
            if current_group:
                if current_group in log_entry:
                    log_entry[current_group] += line
                else:
                    log_entry[current_group] = line
    return dict_list


def path_sanitizer(api_path):
    """Remove numerical ids from the api path"""
    path_list = api_path.split("/")
    for index, path in enumerate(path_list):
        if path.isdigit():
            path_list[index] = "<id>"
    return "/".join(path_list)


def endpoint_counter(dict_list):
    """Count the number of times each endpoint is called"""
    endpoint_dict = {}
    for log_entry in dict_list:
        endpoint = path_sanitizer((split_path := log_entry["Started"].split())[4])
        endpoint = f"{split_path[3]} {endpoint}"
        if endpoint in endpoint_dict:
            endpoint_dict[endpoint] += 1
        else:
            endpoint_dict[endpoint] = 1
    return endpoint_dict


def sorted_endpoints(endpoint_dict):
    """Sort the endpoint dictionary by number of calls"""
    return sorted(endpoint_dict.items(), key=lambda item: item[1], reverse=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("log_path", help="Path to the production.log file")
    args = parser.parse_args()
    log_path = args.log_path
    if not (log_path := Path(log_path)).is_file():
        raise FileNotFoundError(f"{log_path} is not a file")
    dict_list = log_to_dicts(log_path)
    endpoint_dict = endpoint_counter(dict_list)
    sorted_endpoints = sorted_endpoints(endpoint_dict)
    for endpoint, count in sorted_endpoints:
        print(f"{endpoint}: {count}")
