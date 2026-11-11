"""Read shared project settings."""

import os

import yaml


def load_config(path=None):
    path = path or os.environ.get(
        "CONFIG_PATH", "config/config.yaml"
    )
    with open(path, encoding="utf-8") as file:
        return yaml.safe_load(file)
