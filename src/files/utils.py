import re
import uuid


def slugify(filename: str) -> str:

    parts = filename.rsplit(".", maxsplit=1)
    name = parts[0].lower().strip()
    ext = parts[1].lower() if len(parts) > 1 else ""
    name = re.sub(r"[^a-z0-9]+", "-", name).strip("-")
    unique_id = str(uuid.uuid4())[:8]
    slug = f"{name}-{unique_id}"
    if ext:
        slug = f"{slug}.{ext}"
    return slug
