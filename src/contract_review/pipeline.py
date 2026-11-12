"""Connect the supplied model's extracted processing steps."""

import logging

import numpy as np

from contract_review.chunking import make_chunks
from contract_review.data import load_cuad
from contract_review.features import (
    bm25_matrix,
    build_classifier_features,
    build_counts,
    query_matrix,
)
from contract_review.knowledge import knowledge_queries
from contract_review.labelling import label_chunks
from contract_review.metadata import contract_type, filing_year
from contract_review.model import calibrate, fit_linear
from contract_review.scoring import select_knowledge_weight
from contract_review.splitting import (
    group_contract_families,
    split_contracts,
)


logger = logging.getLogger(__name__)


def run_pipeline(
    data_dir,
    seed=3217,
    negative_sample=0.25,
    max_features=150_000,
):
    """Run the supplied full-data classifier and knowledge blend."""
    logger.info("Loading contract dataset")
    contracts, spans, questions = load_cuad(data_dir)
    logger.info("Loaded %d contracts and %d annotations", len(contracts), len(spans))
    categories = questions.category.tolist()

    contracts["ctype"] = contracts.title.map(contract_type)
    contracts["year"] = contracts.title.map(filing_year)
    contracts, _, _ = group_contract_families(contracts)
    contracts, fingerprint = split_contracts(
        contracts, spans, seed=seed
    )

    chunks = make_chunks(contracts)
    logger.info("Created %d passages", len(chunks))
    lookup = contracts.set_index("contract_id")

    chunks["split"] = chunks.contract_id.map(lookup["split"])
    chunks["text"] = [
        lookup.loc[cid, "text"][start:end]
        for cid, start, end in zip(
            chunks.contract_id, chunks.start, chunks.end
        )
    ]

    labels, coverage = label_chunks(chunks, spans, categories)
    masks = {
        name: (chunks["split"] == name).to_numpy()
        for name in ["train", "valid", "test", "held-out type"]
    }

    counts, vocabulary, vectorizer = build_counts(
        chunks, masks["train"], max_features=max_features
    )
    features, transformer = build_classifier_features(
        counts, chunks, masks["train"]
    )
    classifier_scores, fitted_rows, models = fit_linear(
        features,
        masks["train"],
        labels,
        categories,
        seed=seed,
        negative_sample=negative_sample,
    )

    logger.info("Fitted %d classifiers using %d passages", len(models), fitted_rows)
    weighted = bm25_matrix(counts, masks["train"])
    query_vectors = query_matrix(
        knowledge_queries(questions), vectorizer, vocabulary
    )
    knowledge_scores = np.asarray(
        (weighted @ query_vectors.T).todense()
    )

    combined, weight, scaling = select_knowledge_weight(
        classifier_scores,
        knowledge_scores,
        masks["train"],
        masks["valid"],
        chunks,
        labels,
        categories,
    )
    probabilities, calibration = calibrate(
        combined, masks["valid"], labels
    )

    logger.info("Selected knowledge weight %.2f", weight)
    logger.info("Calibration completed")

    return {
        "contracts": contracts,
        "chunks": chunks,
        "labels": labels,
        "coverage": coverage,
        "categories": categories,
        "masks": masks,
        "combined_scores": combined,
        "probabilities": probabilities,
        "weight": weight,
        "holdout_sha256": fingerprint,
        "fitted_training_passages": fitted_rows,
        "models": models,
        "vectorizer": vectorizer,
        "vocabulary": vocabulary,
        "transformer": transformer,
        "scaling": scaling,
        "calibration": calibration,
    }


def run_configured_pipeline(config_path=None, env_path=None):
    """Resolve settings and execute the supplied model workflow."""
    from contract_review.config import load_settings

    settings = load_settings(config_path, env_path)
    from contract_review.logging_setup import setup_logging
    setup_logging(settings["log_level"])

    result = run_pipeline(
        data_dir=settings["data_path"],
        seed=settings["seed"],
        negative_sample=settings["negative_sample"],
        max_features=settings["max_features"],
    )

    return result, settings
