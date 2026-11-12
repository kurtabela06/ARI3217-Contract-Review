from contract_review.config import load_settings


def write_settings(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text(
        "data_path: data\n"
        "model_path: models/model.joblib\n"
        "seed: 3217\n",
        encoding="utf-8",
    )
    env = tmp_path / ".env"
    env.write_text("", encoding="utf-8")
    return config, env


def test_yaml_defaults_apply_without_environment_overrides(
    tmp_path, monkeypatch
):
    monkeypatch.delenv("DATA_PATH", raising=False)
    monkeypatch.delenv("MODEL_PATH", raising=False)
    config, env = write_settings(tmp_path)

    settings = load_settings(config, env)

    assert settings["data_path"] == "data"
    assert settings["model_path"] == "models/model.joblib"
    assert settings["seed"] == 3217


def test_dotenv_overrides_yaml(tmp_path, monkeypatch):
    monkeypatch.delenv("DATA_PATH", raising=False)
    config, env = write_settings(tmp_path)
    env.write_text("DATA_PATH=local-data\n", encoding="utf-8")

    settings = load_settings(config, env)

    assert settings["data_path"] == "local-data"


def test_shell_environment_overrides_dotenv(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_PATH", "shell-data")
    config, env = write_settings(tmp_path)
    env.write_text("DATA_PATH=local-data\n", encoding="utf-8")

    settings = load_settings(config, env)

    assert settings["data_path"] == "shell-data"
