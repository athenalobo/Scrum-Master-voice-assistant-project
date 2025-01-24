import json
import os
import platform
from pathlib import Path
from typing import Optional, Any, Dict, Mapping


def get_app_data() -> Optional[str]:
    system = platform.system()

    if system == "Windows":
        return os.getenv('APPDATA')
    elif system == "Darwin":
        return os.path.expanduser('~/Library/Application Support')
    elif system == "Linux":
        return os.path.expanduser('~/.local/share')
    else:
        return None


def get_settings_path() -> str:
    app_data_path = get_app_data()

    if app_data_path is None:
        app_data_path = "."

    dir_path = os.path.join(app_data_path, "Cast", "jira-assistant")

    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, 'settings.json')


def write_file(path: str, data: str, encoding="utf-8"):
    with open(path, "w", encoding=encoding) as f:
        f.write(data)


def write_json(path: str, data: Mapping[str, Any], encoding="utf-8"):
    with open(path, "w", encoding=encoding) as f:
        f.write(json.dumps(data, indent=4))


def is_file(path: str) -> bool:
    return Path(path).is_file()


def read_json(path: str) -> Mapping[str, Any]:
    with open(path, 'r') as f:
        data = json.loads(f.read())

    return data
