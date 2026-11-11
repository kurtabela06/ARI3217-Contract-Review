"""Dataset loading and text preparation."""

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
