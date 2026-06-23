from pathlib import Path
import json

from src.agents.jd_parser import JDParser

def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    jd_path = "data/sample_jd.txt"
    profile_path = "data/candidate_profile.json"

    job_description = load_text(jd_path)
    candidate_profile = load_json(profile_path)

    parser = JDParser()
    parsed_jd = parser.parse(job_description)

    output_path = Path("outputs/parsed_jd.json")
    output_path.write_text(
        parsed_jd.model_dump_json(indent=2),
        encoding="utf-8"
    )

    print("AI Job Application Assistant Agent")
    print("=" * 45)
    print(f"Loaded job description: {jd_path}")
    print(f"Job description length: {len(job_description)} characters")
    print(f"Loaded candidate profile: {profile_path}")
    print(f"Candidate name: {candidate_profile.get('name', 'Unknown')}")
    print("Project initialized successfully.")

    print(f"Role: {parsed_jd.role}")
    print(f"Employment type: {parsed_jd.employment_type}")
    print(f"Responsibilities: {len(parsed_jd.responsibilities)}")
    print(f"Required skills: {len(parsed_jd.required_skills)}")
    print(f"Preferred skills: {len(parsed_jd.preferred_skills)}")
    print(f"Saved parsed JD to {output_path}")


if __name__ == "__main__":
    main()