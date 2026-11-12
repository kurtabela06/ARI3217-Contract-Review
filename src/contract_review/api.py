"""HTTP interface for the fitted contract review assistant."""

import hashlib
import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from contract_review.artifacts import load_bundle
from contract_review.config import load_settings
from contract_review.inference import score_contract
from contract_review.logging_setup import setup_logging
from contract_review.review import review_pack

settings = load_settings()
setup_logging(settings["log_level"])
logger = logging.getLogger(__name__)

model_path = Path(settings["model_path"])
bundle = load_bundle(model_path)
bundle_sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
model_version = f'{bundle["package_version"]}:{bundle_sha[:12]}'

logger.info("Loaded serving bundle version %s", model_version)

app = FastAPI(title="Contract Review Assistant")


class ReviewRequest(BaseModel):
    text: str = Field(min_length=1)


@app.get("/health")
def health():
    return {"status": "ok", "model_version": model_version}


@app.post("/review")
def review(item: ReviewRequest):
    if not item.text.strip():
        raise HTTPException(
            status_code=422,
            detail="Contract text must not be blank.",
        )

    request_id = uuid.uuid4().hex
    scored = score_contract(item.text, bundle)
    chunks = scored["chunks"]
    probabilities = scored["probabilities"]

    pack = review_pack(
        probabilities,
        chunks,
        0,
        bundle["categories"],
        bundle["red_flags"],
        bundle["review_budget"],
    )

    highlights = []
    found_categories = set()

    for index, tags in pack.items():
        start = int(chunks.loc[index, "start"])
        end = int(chunks.loc[index, "end"])
        categories = [
            {
                "category": bundle["categories"][tag],
                "probability": float(probabilities[index, tag]),
            }
            for tag in sorted(tags)
        ]
        found_categories.update(
            entry["category"] for entry in categories
        )

        highlights.append({
            "start": start,
            "end": end,
            "text": scored["masked_text"][start:end],
            "categories": categories,
            "citation": f"[{request_id}:{start}-{end}]",
        })

    logger.info(
        "Review %s model=%s characters=%d highlights=%d",
        request_id, model_version, len(item.text), len(highlights),
    )

    return {
        "request_id": request_id,
        "model_version": model_version,
        "review_budget": bundle["review_budget"],
        "highlights": highlights,
        "not_found_in_highlights": sorted(
            set(bundle["red_flags"]) - found_categories
        ),
        "notice": (
            "Highlights support human review, not legal advice. "
            "Not found in highlights does not establish absence."
        ),
    }
