import argparse
import sys
from configparser import ConfigParser
from pathlib import Path
import yaml


def convert_data(data):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = convert_data(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = convert_data(item)
    else:
        # handle pattern  default=something,alternate=another
        if "=" in data and not "==" in data:
            data_pairs = [pairs.split("=") for pairs in data.split(",")]
            _data = {pair[0]: pair[1] for pair in data_pairs}
            # sometimes this pattern needs to remain a string
            # if dict conversion results in data loss, don't convert
            if len(data_pairs) == len(_data):
                data = _data
    return data


def ini_to_yaml(ini_file, destination=None, split=False):
    ini_config = ConfigParser()
    ini_config.read(ini_file.absolute())
    if not split:
        new_name = f"{ini_file.name.replace('.ini', '')}.yaml"
        if destination.is_dir():
            destination = destination.joinpath(new_name)
        print(f"Saving config to {destination.absolute()}")
        with destination.open("w") as yml_conf:
            yaml.dump(convert_data(ini_config._sections), yml_conf)
    else:
        for category, data in ini_config._sections.items():
            new_file = destination.joinpath(f"{category}.yaml")
            print(f"Saving category {category} to {new_file.absolute()}")
            with new_file.open("w") as yml_conf:
                yaml.dump(convert_data(data), yml_conf)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "inifile", type=str,
        help="Path to the ini file you want to convert.")
    parser.add_argument(
        "destination", type=str,
        help="Path to the destination you want your file(s) created.")
    parser.add_argument(
        "--split", action="store_true",
        help="If passed, each ini section will be split into its own file.")
    args = parser.parse_args(sys.argv[1:])

    ini_file = Path(args.inifile)
    if not ini_file.exists():
        print(f"Can't find ini file: {ini_file}")
        return
    destination = Path(args.destination)
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
    ini_to_yaml(ini_file, destination, args.split)

if __name__ == "__main__":
    main()
