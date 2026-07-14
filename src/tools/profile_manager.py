import json
import re
from pathlib import Path

def slugify_profile_name(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = name.strip("-")
    return name or "default-profile"

def parse_comma_list(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]

def save_user_profile(profile_name: str, profile: dict) -> str:
    profile_dir = Path("data/profiles")
    profile_dir.mkdir(parents=True, exist_ok=True)

    profile_id = slugify_profile_name(profile_name)
    profile_path = profile_dir / f"{profile_id}.json"

    profile_path.write_text(
        json.dumps(profile, indent=2),
        encoding="utf-8",
    )

    return str(profile_path)

def list_saved_profiles() -> list[str]:
    profile_dir = Path("data/profiles")
    profile_dir.mkdir(parents=True, exist_ok=True)

    return [str(path) for path in profile_dir.glob("*.json")]