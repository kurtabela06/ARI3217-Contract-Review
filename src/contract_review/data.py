"""Dataset loading and text preparation."""

import json
import time
from pathlib import Path
import pandas as pd
import re


EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(
    r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)"
)


def mask_same_length(text: str) -> tuple[str, int]:
    """Mask emails and phones without moving annotation offsets."""
    n = 0
    for pat, ch in [(EMAIL, "x"), (PHONE, "#")]:
        hits = list(pat.finditer(text))
        n += len(hits)
        for m in hits:
            text = (
                text[:m.start()]
                + ch * (m.end() - m.start())
                + text[m.end():]
            )
    return text, n


def get_raw(filename: str, raw_dir: Path, kaggle_handle: str) -> Path:
    """Use a local source file, otherwise obtain it through Kaggle."""
    local = raw_dir / filename
    if local.exists():
        return local

    import kagglehub

    return Path(kagglehub.dataset_download(kaggle_handle, path=filename))


def load_cuad(
    data_dir,
    kaggle_handle="konradb/atticus-open-contract-dataset-aok-beta",
):
    """Return masked contracts, annotated spans and category questions."""
    data_dir = Path(data_dir)
    raw_dir = data_dir / "raw" / "cuad"
    processed = data_dir / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)

    cache = [
        processed / f"29_{name}.parquet"
        for name in ("contracts", "spans", "questions")
    ]
    if all(path.exists() for path in cache):
        return tuple(pd.read_parquet(path) for path in cache)

    started = time.time()
    source = get_raw(
        "CUAD_v1/CUAD_v1.json", raw_dir, kaggle_handle
    )
    with open(source, encoding="utf-8") as file:
        data = json.load(file)["data"]

    contracts, spans, questions = [], [], {}

    for i, contract in enumerate(data):
        paragraph = contract["paragraphs"][0]
        text, n_masked = mask_same_length(paragraph["context"])

        contracts.append({
            "contract_id": i,
            "title": contract["title"],
            "text": text,
            "n_masked": n_masked,
        })

        for qa in paragraph["qas"]:
            category = qa["id"].split("__")[-1]
            questions.setdefault(category, qa["question"])

            for answer in qa["answers"]:
                start = answer["answer_start"]
                spans.append({
                    "contract_id": i,
                    "category": category,
                    "start": start,
                    "end": start + len(answer["text"]),
                    "exact": text[start:].startswith(answer["text"]),
                })

    contracts = pd.DataFrame(contracts)
    spans = pd.DataFrame(spans)
    questions = pd.DataFrame({
        "category": list(questions),
        "question": list(questions.values()),
    })

    for frame, path in zip((contracts, spans, questions), cache):
        frame.to_parquet(path)

    print(f"parsed and cached in {time.time() - started:.0f}s")
    return contracts, spans, questions
