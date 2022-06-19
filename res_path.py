import os
import json


def res_path(filename: str) -> str:
    with open('config.json') as config_file:
        config_data = json.load(config_file)
    return os.path.join(f'res/images/{config_data["icons"]["folder"]}', filename)


def flag_path(country_code: str) -> str:
    return os.path.join(f'/res/flags', (country_code.upper() + '.png'))
