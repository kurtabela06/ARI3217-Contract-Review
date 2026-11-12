"""Build and save the fitted components required for serving."""

import json
from importlib.metadata import version
from pathlib import Path

import joblib


def build_bundle(result, settings):
    """Select serving components without copying dataset tables."""
    with open(
        settings["red_flags_path"], encoding="utf-8"
    ) as file:
        red_flags = json.load(file)

    unknown = set(red_flags) - set(result["categories"])
    if unknown:
        raise ValueError(f"Unknown red-flag categories: {sorted(unknown)}")

    return {
        "format_version": 1,
        "package_version": version("contract-review"),
        "categories": result["categories"],
        "red_flags": red_flags,
        "review_budget": settings["review_budget"],
        "vectorizer": result["vectorizer"],
        "selected_columns": result["selected_columns"],
        "tfidf": result["transformer"],
        "classifiers": result["models"],
        "bm25": result["bm25_reference"],
        "knowledge_query_vectors": result["knowledge_query_vectors"],
        "scaling": result["scaling"],
        "calibration": result["calibration"],
        "knowledge_weight": result["weight"],
        "training": {
            "seed": settings["seed"],
            "negative_sample": settings["negative_sample"],
            "max_features": settings["max_features"],
            "holdout_sha256": result["holdout_sha256"],
        },
    }


def save_bundle(bundle, path):
    """Save the selected fitted components."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path, compress=3)
    return path


def load_bundle(path):
    """Load a trusted bundle produced by this project."""
    return joblib.load(path)
