from src.workflows.job_analysis_workflow import run_job_analysis


def main() -> None:
    jd_path = "data/sample_jd.txt"
    profile_path = "data/candidate_profile.json"

    parsed_jd_output_path = "outputs/parsed_jd.json"
    match_result_output_path = "outputs/match_result.json"
    match_report_output_path = "outputs/match_report.md"
    cover_letter_output_path = "outputs/cover_letter.md"
    linkedin_message_output_path = "outputs/linkedin_message.md"
    app_tracker_path = "data/applications.json",
    app_status = "interested",
    app_notes = '',
    use_mock_llm = True,
    generate_cover_letter = False,
    generate_linkedin_message = False,
    save_application = False

    res = run_job_analysis(
        jd_path, 
        profile_path, 
        parsed_jd_output_path,
        match_result_output_path,
        match_report_output_path,
        cover_letter_output_path,
        linkedin_message_output_path,
        app_tracker_path,
        app_status,
        app_notes,
        use_mock_llm,
        generate_cover_letter,
        generate_linkedin_message,
        save_application,
        verbose = True
    )


if __name__ == "__main__":
    main()