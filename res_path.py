import os
import json


def res_path(filename: str) -> str:
    """Функция возвращает путь к требуемому ресурсу, в дальнейшем планировалось использовать различные папки для тем"""
    with open('config.json') as config_file:
        config_data = json.load(config_file)
    return os.path.join(f'res/images/{config_data["icons"]["folder"]}', filename)


def flag_path(country_code: str) -> str:
    """Функция возвращает путь к флагу по коду страны"""
    return os.path.join(f"res/flags", (country_code.upper() + ".png"))
