import json
import sys
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import platformdirs
from rich.console import Console

from task_tracker import StorageError
from task_tracker.helpers import print_error
from task_tracker.plugins import AvailablePlugins, TaskStorageProtocol

CONFIG_DIR = platformdirs.user_config_path("task.py", ensure_exists=True)
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class Context:
    plugin: AvailablePlugins = AvailablePlugins.JSON
    json_file: Path = Path().home() / "tasks.json"

    @cached_property
    def store(self) -> TaskStorageProtocol:
        try:
            match self.plugin:
                case AvailablePlugins.GOOGLE:
                    from task_tracker.plugins.google import GoogleTaskStorage

                    return GoogleTaskStorage()
                case _:
                    from task_tracker.plugins.json import JsonStorage

                    return JsonStorage(self.json_file)
        except StorageError as e:
            print_error(str(e))
            sys.exit(1)


def load_config(file: Path) -> Context:
    if not CONFIG_FILE.exists() or CONFIG_FILE.stat().st_size == 0:
        CONFIG_DIR.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text("{}")

    try:
        return Context(json.loads(file.read_text()))
    except json.JSONDecodeError as e:
        # print_error(f"Bad config file: {str(e)}")
        print_error(str(e))
        sys.exit(1)


def write_config(config: Context):
    CONFIG_FILE.write_text(json.dumps(config))


context = load_config(CONFIG_FILE)
