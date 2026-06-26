from pathlib import Path
import json

from src.agents.jd_parser import JDParser
from src.agents.profile_matcher import ProfileMatcher
from src.agents.material_generator import MaterialGenerator

def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(path: str, data: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(data, encoding="utf-8")

def main() -> None:
    jd_path = "data/sample_jd.txt"
    profile_path = "data/candidate_profile.json"

    parsed_jd_output_path = "outputs/parsed_jd.json"
    match_result_output_path = "outputs/match_result.json"

    print("AI Job Application Assistant Agent")
    print("=" * 45)

    # 1. Load input files
    job_description = load_text(jd_path)
    candidate_profile = load_json(profile_path)

    print(f"Loaded job description: {jd_path}")
    print(f"Loaded candidate profile: {profile_path}")
    print()

    # 2. Parse JD
    parser = JDParser()
    parsed_jd = parser.parse(job_description)

    save_json(
        parsed_jd_output_path,
        parsed_jd.model_dump_json(indent=2)
    )

    print("Parsed JD")
    print("-" * 45)
    print(f"Company: {parsed_jd.company}")
    print(f"Role: {parsed_jd.role}")
    print(f"Employment type: {parsed_jd.employment_type}")
    print(f"Location: {parsed_jd.location}")
    print(f"Start date: {parsed_jd.start_date}")
    print(f"Duration: {parsed_jd.duration}")
    print(f"Responsibilities: {len(parsed_jd.responsibilities)}")
    print(f"Required skills: {len(parsed_jd.required_skills)}")
    print(f"Preferred skills: {len(parsed_jd.preferred_skills)}")
    print(f"Tools: {parsed_jd.tools}")
    print(f"Domains: {parsed_jd.domains}")
    print(f"Saved parsed JD to {parsed_jd_output_path}")
    print()

    # 3. Match candidate profile
    matcher = ProfileMatcher()
    match_result = matcher.match(parsed_jd, candidate_profile)

    save_json(
        match_result_output_path,
        match_result.model_dump_json(indent=2)
    )

    print("Profile Match Result")
    print("-" * 45)
    print(f"Match score: {match_result.match_score}")
    print(f"Matched required skills: {len(match_result.matched_required_skills)}")
    print(f"Missing required skills: {len(match_result.missing_required_skills)}")
    print(f"Matched preferred skills: {len(match_result.matched_preferred_skills)}")
    print(f"Missing preferred skills: {len(match_result.missing_preferred_skills)}")
    print(f"Matched tools: {match_result.matched_tools}")
    print(f"Matched domains: {match_result.matched_domains}")
    print(f"Relevant projects: {match_result.relevant_projects}")
    print(f"Saved match result to {match_result_output_path}")
    print()

    print("Strengths")
    print("-" * 45)
    for strength in match_result.strengths:
        print(f"- {strength}")

    print()

    print("Gaps")
    print("-" * 45)
    for gap in match_result.gaps:
        print(f"- {gap}")

    print()

    print("Positioning Summary")
    print("-" * 45)
    print(match_result.positioning_summary)

    # 4. Generate Matching Report
    generator = MaterialGenerator()

    match_report = generator.generate_match_report(
        parsed_jd=parsed_jd,
        match_result=match_result,
        candidate_profile=candidate_profile
    )

    Path("outputs/match_report.md").write_text(
        match_report,
        encoding="utf-8"
    )

    print("Saved match report to outputs/match_report.md")

    print()
    print("End-to-end test completed successfully.")


if __name__ == "__main__":
    main()