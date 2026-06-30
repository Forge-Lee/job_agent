import typer

from src.workflows.job_analysis_workflow import run_job_analysis
from src.tools.application_tracker import ApplicationTracker

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