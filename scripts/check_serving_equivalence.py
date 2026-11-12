"""Compare loaded-bundle inference with the reference pipeline."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from contract_review.artifacts import load_bundle
from contract_review.inference import score_contract
from contract_review.pipeline import run_configured_pipeline
from contract_review.review import review_pack


def selected_passages(pack, chunks):
    """Compare source locations and tags instead of local row numbers."""
    return [
        (
            int(chunks.loc[index, "start"]),
            int(chunks.loc[index, "end"]),
            tuple(sorted(tags)),
        )
        for index, tags in pack.items()
    ]


def main():
    root = Path(__file__).resolve().parents[1]
    result, settings = run_configured_pipeline()

    model_path = Path(settings["model_path"])
    bundle = load_bundle(model_path)

    assert bundle["categories"] == result["categories"]
    assert (
        bundle["training"]["holdout_sha256"]
        == result["holdout_sha256"]
    )
    assert bundle["review_budget"] == settings["review_budget"]

    contracts = result["contracts"]
    chunks = result["chunks"]
    selected = contracts[
        contracts.split.isin(["test", "held-out type"])
    ]

    rows = []

    for number, contract in enumerate(
        selected.itertuples(), start=1
    ):
        served = score_contract(contract.text, bundle)
        indices = chunks.index[
            chunks.contract_id == contract.contract_id
        ].to_numpy()
        reference_chunks = chunks.loc[indices]

        np.testing.assert_array_equal(
            served["chunks"][["start", "end"]].to_numpy(),
            reference_chunks[["start", "end"]].to_numpy(),
        )

        expected_probabilities = result["probabilities"][indices]
        np.testing.assert_allclose(
            served["probabilities"],
            expected_probabilities,
            rtol=1e-6,
            atol=1e-7,
        )

        expected_pack = review_pack(
            result["probabilities"],
            chunks,
            contract.contract_id,
            result["categories"],
            bundle["red_flags"],
            bundle["review_budget"],
        )
        served_pack = review_pack(
            served["probabilities"],
            served["chunks"],
            0,
            bundle["categories"],
            bundle["red_flags"],
            bundle["review_budget"],
        )

        assert selected_passages(
            expected_pack, chunks
        ) == selected_passages(
            served_pack, served["chunks"]
        ), f"Review selection differs for contract {contract.contract_id}"

        rows.append({
            "contract_id": contract.contract_id,
            "split": contract.split,
            "passages": len(served["chunks"]),
            "maximum_probability_difference": float(
                np.abs(
                    served["probabilities"] - expected_probabilities
                ).max()
            ),
            "review_selection_matches": True,
        })

        if number % 10 == 0:
            print(f"Checked {number}/{len(selected)} contracts", flush=True)

    evidence = root / "evidence"
    report = pd.DataFrame(rows)
    report.to_csv(
        evidence / "serving-equivalence-results.csv", index=False
    )

    summary = {
        "contracts_checked": len(report),
        "contracts_by_split": report.groupby("split").size().to_dict(),
        "all_review_selections_match": True,
        "maximum_probability_difference": float(
            report.maximum_probability_difference.max()
        ),
        "probability_rtol": 1e-6,
        "probability_atol": 1e-7,
        "bundle_sha256": hashlib.sha256(
            model_path.read_bytes()
        ).hexdigest(),
        "holdout_sha256": result["holdout_sha256"],
        "input_note": (
            "Uses the notebook's already-masked test contract text; "
            "masking behaviour is checked separately by unit tests."
        ),
    }
    (evidence / "serving-equivalence-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2))
    print("All passage boundaries, probabilities and review selections match.")


if __name__ == "__main__":
    main()
