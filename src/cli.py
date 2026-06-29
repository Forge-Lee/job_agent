import typer
from pathlib import Path
import json
import datetime

from src.agents.jd_parser import JDParser
from src.agents.profile_matcher import ProfileMatcher
from src.agents.material_generator import MaterialGenerator
from src.utils.llm_client import MockLLMClient, OpenAIClient
from src.tools.application_tracker import ApplicationTracker

def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(path: str, data: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(data, encoding="utf-8")

def save_text(path: str, data: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(data, encoding="utf-8")

app = typer.Typer()

@app.command()
def analyze(
    jd_path: str = "data/sample_jd.txt", 
    profile_path: str = "data/candidate_profile.json", 
    parsed_jd_output_path: str = "outputs/parsed_jd.json",
    match_result_output_path: str = "outputs/match_result.json",
    match_report_output_path: str = "outputs/match_report.md",
    cover_letter_output_path: str = "outputs/cover_letter.md",
    linkedin_message_output_path: str = "outputs/linkedin_message.md",
    app_tracker_path: str = "data/applications.json",
    app_status: str = "interested",
    app_notes: str = '',
    use_mock_llm: bool = True,
    generate_cover_letter: bool = False,
    generate_linkedin_message: bool = False,
    save_application: bool = False
):
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
    llm_client = MockLLMClient()
    generator = MaterialGenerator(llm_client=llm_client)

    match_report = generator.generate_match_report(
        parsed_jd=parsed_jd,
        match_result=match_result,
        candidate_profile=candidate_profile
    )

    save_text(
        match_report_output_path,
        match_report
    )

    print(f"Saved match report to {match_report_output_path}")

    if generate_cover_letter or generate_linkedin_message:
        if use_mock_llm:
            llm_client = MockLLMClient()
            print('Using MockLLMClient as api placeholder.')
        else:
            llm_client = OpenAIClient()
            print('Using real LLM API as backend.')

        generator = MaterialGenerator(llm_client=llm_client)

    if generate_cover_letter:
        cover_letter = generator.generate_cover_letter(
            parsed_jd=parsed_jd,
            match_result=match_result,
            candidate_profile=candidate_profile,
        )

        save_text(
            cover_letter_output_path,
            cover_letter
        )

        print(f"Saved cover letter to {cover_letter_output_path}")

    if generate_linkedin_message:
        linkedin_message = generator.generate_linkedin_message(
            parsed_jd=parsed_jd,
            match_result=match_result,
            candidate_profile=candidate_profile,
        )

        save_text(
            linkedin_message_output_path,
            linkedin_message
        )

        print(f"Saved LinkedIn message to {linkedin_message_output_path}")

    # 5. Track the Application
    if save_application:
        tracker = ApplicationTracker(app_tracker_path)

        # generate record for current job
        app_id = parsed_jd.company + ' ' + parsed_jd.role
        app_id = app_id.lower()
        app_id = app_id.replace(' ','-')
        company = parsed_jd.company
        role = parsed_jd.role
        match_score = match_result.match_score
        create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            'id': app_id,
            'company': company,
            'role': role,
            'status': app_status,
            'match_score': match_score,
            'jd_path': jd_path,
            'match_report_path': match_report_output_path,
            'cover_letter_path': cover_letter_output_path,
            'linkedin_message_path': linkedin_message_output_path,
            'notes': [app_notes] if app_notes else [],
            'created_at': create_time,
            'updated_at': create_time
        }

        tracker.add_application(record)
        print(f"Saved application record: {app_id}")

    print()
    print("End-to-end test completed successfully.")

@app.command()
def list_applications(app_tracker_path: str = "data/applications.json"):
    tracker = ApplicationTracker(app_tracker_path)
    print(tracker.list_applications())

@app.command()
def update_status(app_id: str, new_status: str, app_tracker_path: str = "data/applications.json"):
    status_list = [
        'interested',
        'applied',
        'followed_up',
        'interviewing',
        'rejected',
        'offer',
        'closed'
    ]
    tracker = ApplicationTracker(app_tracker_path)
    if new_status in status_list:
        tracker.update_status(app_id, new_status)
        print("Application after update:\n")
        print(tracker.find_application(app_id))
    else:
        print('Invalid status, please choose a status from\n')
        print('interested, applied, followed_up, interviewing, rejected, offer, and closed')

if __name__ == "__main__":
    app()