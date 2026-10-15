"""Render classroom placeholders. Run with Python 3; no external modules."""
import os
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
image = os.environ.get("IMAGE_V1", "")
host = os.environ.get("APP_HOST", "")
if not re.fullmatch(r"[a-zA-Z0-9._:/@-]+@sha256:[0-9a-f]{64}", image):
    raise SystemExit("Set IMAGE_V1 to a registry image reference pinned with @sha256:<64 hex digits>")
if len(host) > 253 or not all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", part) for part in host.split(".")):
    raise SystemExit("Set APP_HOST to a valid lower-case DNS hostname")
out = root / "rendered"
out.mkdir(exist_ok=True)
for name in ("app.yaml", "tls.yaml"):
    text = (root / "manifests" / name).read_text()
    (out / name).write_text(text.replace("IMAGE_REFERENCE", image).replace("APP_HOST", host))
print("Wrote rendered/app.yaml and rendered/tls.yaml")
