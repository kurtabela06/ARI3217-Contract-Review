"""Passage splitting extracted from the supplied notebook."""

import re


ABBREV = {"inc", "corp", "co", "ltd", "llc", "no", "nos", "sec", "secs", "art", "mr", "mrs", "ms", "dr", "st", "vs", "v",
          "e.g", "i.e", "u.s", "u.k", "n.a", "s.a", "l.p", "etc", "approx", "jr", "sr", "p", "pp", "ex"}


SENT_END = re.compile(r"[.!?]\s+(?=[\"'“(\[]?[A-Z0-9])")


BLANK_LINE = re.compile(r"\n\s*\n")


def sentence_chunks(text: str, min_len: int = 40, max_len: int = 1500) -> list[tuple[int, int]]:
    '''Character spans of sentence-like chunks. Blank lines and sentence ends split; pieces shorter than
    min_len (headings, clause numbers) merge forward; pieces longer than max_len split at '; '.'''
    cuts = {0, len(text)} | {m.end() for m in BLANK_LINE.finditer(text)}
    for m in SENT_END.finditer(text):
        w = re.search(r"([\w.]+)$", text[max(0, m.start() - 12):m.start()])
        if not (w and (w.group(1).lower() in ABBREV or len(w.group(1)) == 1)):   # "Inc." or "A." does not end a sentence
            cuts.add(m.start() + 1)
    cuts, out, start = sorted(cuts), [], None
    for s, e in zip(cuts[:-1], cuts[1:]):
        start = s if start is None else start
        if len(text[start:e].strip()) < min_len and e < len(text):
            continue
        s0, e0 = start, e
        while s0 < e0 and text[s0].isspace(): s0 += 1
        while e0 > s0 and text[e0 - 1].isspace(): e0 -= 1
        while e0 - s0 > max_len:
            cut = text.rfind("; ", s0 + max_len // 2, s0 + max_len)
            cut = cut + 2 if cut >= 0 else (text.rfind(" ", s0 + max_len // 2, s0 + max_len) + 1 or s0 + max_len)
            out.append((s0, cut)); s0 = cut
        if e0 > s0:
            out.append((s0, e0))
        start = None
    return out


def window_chunks(text: str, size: int = 512, overlap: int = 0) -> list[tuple[int, int]]:
    '''Fixed character windows, the default in many RAG tutorials.'''
    step = size - overlap
    return [(s, min(s + size, len(text))) for s in range(0, max(len(text) - overlap, 1), step)]


def make_chunks(contracts, chunker=sentence_chunks, **kwargs):
    """Build passage locations for explicitly supplied contracts."""
    import pandas as pd

    rows = [
        (contract_id, k, start, end)
        for contract_id, text in zip(
            contracts.contract_id, contracts.text
        )
        for k, (start, end) in enumerate(chunker(text, **kwargs))
    ]
    chunks = pd.DataFrame(
        rows,
        columns=["contract_id", "k", "start", "end"],
    )
    chunks["relpos"] = (
        chunks.k
        / chunks.groupby("contract_id").k.transform("size")
    )
    return chunks
