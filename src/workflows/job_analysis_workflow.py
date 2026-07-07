import datetime

from src.agents.jd_parser import JDParser
from src.agents.profile_matcher import ProfileMatcher
from src.agents.material_generator import MaterialGenerator
from src.utils.llm_client import MockLLMClient, OpenAIClient
from src.tools.application_tracker import ApplicationTracker
from src.tools.file_loader import *
from src.tools.material_validator import MaterialValidator

def run_job_analysis(
    jd_path: str = "data/sample_jd.txt", 
    profile_path: str = "data/candidate_profile.json", 
    parsed_jd_output_path: str = "outputs/parsed_jd.json",
    match_result_output_path: str = "outputs/match_result.json",
    match_report_output_path: str = "outputs/match_report.md",
    cover_letter_output_path: str = "outputs/cover_letter.md",
    linkedin_message_output_path: str = "outputs/linkedin_message.md",
    resume_bullets_output_path: str = "outputs/resume_bullets.md",
    app_tracker_path: str = "data/applications.json",
    app_status: str = "interested",
    app_notes: str = '',
    use_mock_llm: bool = True,
    generate_cover_letter: bool = False,
    generate_linkedin_message: bool = False,
    generate_resume_bullets: bool = False,
    save_application: bool = False,
    verbose: bool = True
):
    if verbose:
        print("AI Job Application Assistant Agent")
        print("=" * 45)

    # 1. Load input files
    job_description = load_text(jd_path)
    candidate_profile = load_json(profile_path)

    if verbose:
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

    if verbose:
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

    if verbose:
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

    if verbose:
        print(f"Saved match report to {match_report_output_path}")

    if generate_cover_letter or generate_linkedin_message or generate_resume_bullets:
        if use_mock_llm:
            llm_client = MockLLMClient()
            if verbose:
                print('Using MockLLMClient as api placeholder.')
        else:
            llm_client = OpenAIClient()
            if verbose:
                print('Using real LLM API as backend.')

        generator = MaterialGenerator(llm_client=llm_client)

        validator = MaterialValidator()

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

        if verbose:
            print(f"Saved cover letter to {cover_letter_output_path}")
            print('Validating cover letter...')
        
        cover_letter_validation = validator.validate_cover_letter(cover_letter, parsed_jd, candidate_profile)
        if verbose:
            print(cover_letter_validation)

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

        if verbose:
            print(f"Saved LinkedIn message to {linkedin_message_output_path}")
            print('Validating LinkedIn message...')
        
        linkedin_message_validation = validator.validate_linkedin_message(linkedin_message, parsed_jd, candidate_profile)
        if verbose:
            print(linkedin_message_validation)
    
    if generate_resume_bullets:
        resume_bullets = generator.generate_resume_bullets(
            parsed_jd=parsed_jd,
            match_result=match_result,
            candidate_profile=candidate_profile,
        )

        save_text(
            resume_bullets_output_path,
            resume_bullets
        )

        if verbose:
            print(f"Saved recommended resume bullets to {resume_bullets_output_path}")
            print('Validating recommended resume bullets...')
        
        resume_bullets_validation = validator.validate_resume_bullets(resume_bullets, parsed_jd, candidate_profile)
        if verbose:
            print(resume_bullets_validation)

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
            'resume_bullets_path': resume_bullets_output_path,
            'notes': [app_notes] if app_notes else [],
            'created_at': create_time,
            'updated_at': create_time
        }

        tracker.add_application(record)
        if verbose:
            print(f"Saved application record: {app_id}")

    if verbose:
        print()
        print("End-to-end test completed successfully.")

    res = {
        "parsed_jd": parsed_jd,
        "match_result": match_result,
        "match_report_path": match_report_output_path,
        "cover_letter_path": cover_letter_output_path if generate_cover_letter else None,
        "linkedin_message_path": linkedin_message_output_path if generate_linkedin_message else None,
        "resume_bullets_path": resume_bullets_output_path if generate_resume_bullets else None,
        "application_id": app_id if save_application else None
    }

    return res