"""Score combination from the supplied notebook."""

from contract_review.evaluation import eval_scores


def standardise_scores(scores, reference_mask):
    """Fit the notebook's score scaling on reference rows."""
    parameters = {
        "mean": scores[reference_mask].mean(axis=0),
        "std": scores[reference_mask].std(axis=0),
    }
    return apply_standardisation(scores, parameters), parameters


def apply_standardisation(scores, parameters):
    """Reuse fitted scaling without learning from incoming requests."""
    return (
        (scores - parameters["mean"])
        / (parameters["std"] + 1e-6)
    )


def select_knowledge_weight(
    classifier_scores,
    knowledge_scores,
    train_mask,
    validation_mask,
    chunks,
    labels,
    categories,
    weights=(0.0, 0.1, 0.25, 0.5, 1.0),
):
    """Choose the supplied blend weight using validation macro AUPR."""
    classifier_scaled, classifier_parameters = standardise_scores(
        classifier_scores, train_mask
    )
    knowledge_scaled, knowledge_parameters = standardise_scores(
        knowledge_scores, train_mask
    )

    blends = {
        weight: classifier_scaled + weight * knowledge_scaled
        for weight in weights
    }

    best_weight = max(
        weights,
        key=lambda weight: eval_scores(
            blends[weight],
            validation_mask,
            chunks,
            labels,
            categories,
        ).AUPR.mean(),
    )

    parameters = {
        "classifier": classifier_parameters,
        "knowledge": knowledge_parameters,
    }

    return blends[best_weight], best_weight, parameters
