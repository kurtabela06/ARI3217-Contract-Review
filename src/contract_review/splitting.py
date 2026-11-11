"""Contract-family grouping and evaluation partitioning."""

import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def group_contract_families(contracts, duplicate_cosine=0.80):
    """Return contracts with family IDs, duplicate pairs and text vectors."""
    result = contracts.copy()

    vectors = TfidfVectorizer(
        min_df=2,
        max_features=100_000,
        sublinear_tf=True,
        dtype=np.float32,
    ).fit_transform(result.text)

    similarity = (vectors @ vectors.T).tocoo()
    pairs = [
        (i, j)
        for i, j, value in zip(
            similarity.row,
            similarity.col,
            similarity.data,
        )
        if i < j and value >= duplicate_cosine
    ]

    graph = nx.Graph()
    graph.add_nodes_from(result.contract_id)
    graph.add_edges_from(pairs)

    family = {
        node: family_id
        for family_id, component in enumerate(
            nx.connected_components(graph)
        )
        for node in component
    }
    result["family"] = result.contract_id.map(family)

    return result, pairs, vectors
