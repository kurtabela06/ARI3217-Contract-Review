import copy
import hashlib
import json
from pathlib import Path

path = Path("29_contract_review.ipynb")
raw = path.read_bytes()
original = json.loads(raw)
cleaned = copy.deepcopy(original)

digest = hashlib.sha256(raw).hexdigest()
backup_dir = Path("data/reference")
backup_dir.mkdir(parents=True, exist_ok=True)
backup = backup_dir / f"reference-{digest[:12]}.ipynb"

if not backup.exists():
    backup.write_bytes(raw)

cleared = 0
for cell in cleaned["cells"]:
    if cell["cell_type"] == "code":
        cleared += bool(cell.get("outputs"))
        cell["outputs"] = []
        cell["execution_count"] = None

cleaned.get("metadata", {}).pop("widgets", None)

assert [
    (cell["cell_type"], cell["source"])
    for cell in original["cells"]
] == [
    (cell["cell_type"], cell["source"])
    for cell in cleaned["cells"]
], "Cell sources changed unexpectedly."

path.write_text(
    json.dumps(cleaned, ensure_ascii=False, indent=1) + "\n",
    encoding="utf-8",
)

verified = json.loads(path.read_text(encoding="utf-8"))
assert all(
    not cell.get("outputs") and cell.get("execution_count") is None
    for cell in verified["cells"]
    if cell["cell_type"] == "code"
)

print(f"Reference saved locally: {backup}")
print(f"Reference SHA-256: {digest}")
print(f"Cleared outputs from {cleared} cells.")
print("Verified: code and Markdown sources unchanged.")
