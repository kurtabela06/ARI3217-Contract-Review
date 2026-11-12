"""Command-line training entry point."""

import json
import logging
import sys
from pathlib import Path
from time import perf_counter

from contract_review.artifacts import build_bundle, save_bundle
from contract_review.evaluation import eval_scores
from contract_review.pipeline import run_configured_pipeline

logger = logging.getLogger(__name__)


def main():
    started = perf_counter()

    try:
        result, settings = run_configured_pipeline()

        evaluation = eval_scores(
            result["combined_scores"],
            result["masks"]["test"],
            result["chunks"],
            result["labels"],
            result["categories"],
        )
        macro_aupr = float(evaluation.AUPR.mean())

        bundle = build_bundle(result, settings)
        path = save_bundle(bundle, settings["model_path"])
        elapsed = perf_counter() - started

        measurements = {
            "package_version": bundle["package_version"],
            "test_macro_aupr": macro_aupr,
            "knowledge_weight": result["weight"],
            "elapsed_seconds": elapsed,
            "fitted_training_passages": (
                result["fitted_training_passages"]
            ),
            "holdout_sha256": result["holdout_sha256"],
            "timing_scope": (
                "Configured pipeline, test evaluation and bundle saving; "
                "dataset loading may use existing caches."
            ),
        }

        metrics_path = Path(str(path) + ".metrics.json")
        metrics_path.write_text(
            json.dumps(measurements, indent=2) + "\n",
            encoding="utf-8",
        )

        logger.info("Test macro AUPR: %.6f", macro_aupr)
        logger.info("Serving bundle saved to %s", path)
        logger.info("Measurements saved to %s", metrics_path)
        logger.info("Run completed in %.2f seconds", elapsed)

    except Exception:
        logger.exception("Training failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
