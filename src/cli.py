import typer
from rich.console import Console
from rich.table import Table

from src.workflows.job_analysis_workflow import run_job_analysis
from src.tools.application_tracker import ApplicationTracker

app = typer.Typer()

@app.command()
def analyze(
    jd_path: str = typer.Option("data/sample_jd.txt", help='Customize your job description path'), 
    profile_path: str = typer.Option("data/candidate_profile.json", help='Customize your profile path'), 
    parsed_jd_output_path: str = typer.Option("outputs/parsed_jd.json", help='Customize your parsed job description output path'),
    match_result_output_path: str = typer.Option("outputs/match_result.json", help='Customize your matching result output path'),
    match_report_output_path: str = typer.Option("outputs/match_report.md", help='Customize your matching result output path'),
    cover_letter_output_path: str = typer.Option("outputs/cover_letter.md", help='Customize your output cover letter path'),
    linkedin_message_output_path: str = typer.Option("outputs/linkedin_message.md", help='Customize your output LinkedIn follow-up message path'),
    app_tracker_path: str = typer.Option("data/applications.json", help='Customize your application memory path'),
    app_status: str = typer.Option("interested", help='Customize your job application status'),
    app_notes: str = typer.Option('', help='Customize your job application notes for yourselves, default is set as ""'),
    use_mock_llm: bool = typer.Option(True, help='Use MOCKLLM placeholder or real LLM API'),
    generate_cover_letter: bool = typer.Option(False, help='Generate cover letter or not'),
    generate_linkedin_message: bool = typer.Option(False, help='Generate LinkedIn follow-up message or not'),
    save_application: bool = typer.Option(False, help='Save current application to application tracker or not')
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
def list_applications(app_tracker_path: str = typer.Option("data/applications.json", help='Customize your application memory path')):
    tracker = ApplicationTracker(app_tracker_path)
    current_apps = tracker.list_applications()
    if len(current_apps) == 0:
        print("No applications found.")
    else:
        table = Table(title= "Currently Tracked Applications")
        table.add_column("Application ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Company", justify="center", style="white", no_wrap=True)
        table.add_column("Role", justify="center", style="magenta", no_wrap=True)
        table.add_column("Status", justify="center", style="blue", no_wrap=True)
        table.add_column("Score", justify="center", style="green", no_wrap=True)
        
        for app in current_apps:
            table.add_row(app["id"], app["company"], app["role"], app["status"], str(app["match_score"]))
        
        console = Console()
        console.print(table)

@app.command()
def update_status(
    app_id: str = typer.Option('', help='The application id you want to update the status'), 
    new_status: str = typer.Option('', help='The new status you want to update'), 
    app_tracker_path: str = typer.Option("data/applications.json", help='Customize your application memory path')
):
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