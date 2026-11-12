"""Read shared project settings."""

import os

import yaml


def load_config(path=None):
    path = path or os.environ.get(
        "CONFIG_PATH", "config/config.yaml"
    )
    with open(path, encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_settings(path=None, env_path=None):
    """Resolve shared defaults and supported environment overrides."""
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=env_path)
    settings = load_config(path).copy()

    settings["data_path"] = os.environ.get(
        "DATA_PATH", settings["data_path"]
    )
    settings["model_path"] = os.environ.get(
        "MODEL_PATH", settings["model_path"]
    )
    settings["log_level"] = os.environ.get("LOG_LEVEL", "INFO")

    return settings
