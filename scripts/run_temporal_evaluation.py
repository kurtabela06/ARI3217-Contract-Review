"""Run the separately documented chronological robustness experiment."""

import hashlib
import json
import platform
import subprocess
from pathlib import Path
from time import perf_counter

from contract_review.config import load_settings
from contract_review.evaluation import eval_scores
from contract_review.pipeline import run_pipeline
from contract_review.review import pack_eval


def main():
    root = Path(__file__).resolve().parents[1]
    settings = load_settings(
        root / "config/config.yaml",
        root / ".env",
    )

    data_path = Path(settings["data_path"])
    if not data_path.is_absolute():
        data_path = root / data_path

    started = perf_counter()
    result = run_pipeline(
        data_dir=data_path,
        seed=settings["seed"],
        negative_sample=settings["negative_sample"],
        max_features=settings["max_features"],
        evaluation_protocol="temporal",
    )
    pipeline_seconds = perf_counter() - started

    expected_counts = {
        "train": 184,
        "valid": 60,
        "test": 220,
        "excluded_crossing_boundary": 4,
        "excluded_franchise_family": 15,
        "excluded_missing_year": 27,
    }
    actual_counts = (
        result["contracts"].groupby("split").size().to_dict()
    )
    if actual_counts != expected_counts:
        raise ValueError("Temporal partitions differ from the frozen plan.")

    evaluation = eval_scores(
        result["combined_scores"],
        result["masks"]["test"],
        result["chunks"],
        result["labels"],
        result["categories"],
    )

    red_flags_path = Path(settings["red_flags_path"])
    if not red_flags_path.is_absolute():
        red_flags_path = root / red_flags_path
    red_flags = json.loads(red_flags_path.read_text(encoding="utf-8"))

    packs = pack_eval(
        result["probabilities"],
        result["contracts"],
        result["chunks"],
        result["labels"],
        result["categories"],
        red_flags,
        "test",
        budgets=(settings["review_budget"],),
    )

    present = int(packs["present"].sum())
    found = int(packs["found"].sum())

    summary = {
        "protocol": "supplementary_filing_year",
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
        ).strip(),
        "python": platform.python_version(),
        "requirements_sha256": hashlib.sha256(
            (root / "requirements.txt").read_bytes()
        ).hexdigest(),
        "seed": settings["seed"],
        "negative_sample": settings["negative_sample"],
        "max_features": settings["max_features"],
        "periods": {
            "train": "before 2010",
            "valid": "2010 through 2014",
            "test": "2015 onwards",
        },
        "partition_counts": actual_counts,
        "holdout_sha256": result["holdout_sha256"],
        "knowledge_weight": result["weight"],
        "test_macro_aupr": float(evaluation.AUPR.mean()),
        "categories_with_defined_aupr": int(
            evaluation.AUPR.notna().sum()
        ),
        "categories_with_fewer_than_5_positive_test_contracts": int(
            (evaluation["contracts with clause"] < 5).sum()
        ),
        "review_budget": settings["review_budget"],
        "red_flag_occurrences_present": present,
        "red_flag_occurrences_found": found,
        "red_flag_recall": found / present,
        "highlights_on_target": (
            int(packs["on target"].sum())
            / int(packs["highlights"].sum())
        ),
        "pipeline_seconds": pipeline_seconds,
        "timing_scope": "Pipeline only; excludes subsequent evaluation exports.",
        "limitation": (
            "Filing year is derived from titles. Different test populations "
            "prevent a direct causal comparison with primary baseline metrics."
        ),
    }

    evidence = root / "evidence"
    evaluation.to_csv(evidence / "temporal-category-results.csv")
    packs.to_csv(evidence / "temporal-review-results.csv", index=False)
    (evidence / "temporal-evaluation-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2))
    print("Temporal evidence saved. No serving bundle was written.")


if __name__ == "__main__":
    main()
