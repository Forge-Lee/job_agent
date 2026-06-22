from pathlib import Path
import json


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    jd_path = "data/sample_jd.txt"
    profile_path = "data/candidate_profile.json"

    job_description = load_text(jd_path)
    candidate_profile = load_json(profile_path)

    print("AI Job Application Assistant Agent")
    print("=" * 45)
    print(f"Loaded job description: {jd_path}")
    print(f"Job description length: {len(job_description)} characters")
    print(f"Loaded candidate profile: {profile_path}")
    print(f"Candidate name: {candidate_profile.get('name', 'Unknown')}")
    print("Project initialized successfully.")


if __name__ == "__main__":
    main()