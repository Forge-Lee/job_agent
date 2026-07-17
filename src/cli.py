import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import json

from src.workflows.job_analysis_workflow import run_job_analysis
from src.workflows.application_memory_workflow import run_application_memory_query
from src.workflows.react_workflow import run_react_workflow
from src.tools.application_tracker import ApplicationTracker
from src.tools.application_retriever import ApplicationRetriever

app = typer.Typer()

@app.command()
def analyze(
    jd_path: str = typer.Option("data/sample_jd.txt", help='Customize your job description path'), 
    profile_path: str = typer.Option("data/candidate_profile.example.json", help='Customize your profile path'), 
    parsed_jd_output_path: str | None = typer.Option(None, help='Customize your parsed job description output path'),
    match_result_output_path: str | None = typer.Option(None, help='Customize your matching result output path'),
    match_report_output_path: str | None = typer.Option(None, help='Customize your matching result output path'),
    cover_letter_output_path: str | None = typer.Option(None, help='Customize your output cover letter path'),
    linkedin_message_output_path: str | None = typer.Option(None, help='Customize your output LinkedIn follow-up message path'),
    resume_bullets_output_path: str | None = typer.Option(None, help='Customize your output recommended resume bullets path'),
    app_tracker_path: str = typer.Option("data/applications.json", help='Customize your application memory path'),
    app_status: str = typer.Option("interested", help='Customize your job application status'),
    app_notes: str = typer.Option('', help='Customize your job application notes for yourselves, default is set as ""'),
    use_mock_llm: bool = typer.Option(True, help='Use MOCKLLM placeholder or real LLM API'),
    generate_cover_letter: bool = typer.Option(False, help='Generate cover letter or not'),
    generate_linkedin_message: bool = typer.Option(False, help='Generate LinkedIn follow-up message or not'),
    generate_resume_bullets: bool = typer.Option(False, help='Generate recommended resume bullets or not'),
    use_llm_matcher: bool = typer.Option(False, help="Use LLM-based semantic profile matching."),
    use_llm_jd_parser: bool = typer.Option(False,help="Use LLM-based structured JD parsing."),
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
        resume_bullets_output_path,
        app_tracker_path,
        app_status,
        app_notes,
        use_mock_llm,
        generate_cover_letter,
        generate_linkedin_message,
        generate_resume_bullets,
        save_application,
        use_llm_matcher,
        use_llm_jd_parser,
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
    app_id: str = typer.Argument(..., help="Application ID to update."),
    new_status: str = typer.Argument(..., help="New application status."),
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

@app.command()
def search_applications(
    query: str = typer.Argument(..., help="Search query for past applications."),
    top_k: int = typer.Option(3, help="Return the top-k application records related to the query."),
    app_tracker_path: str = typer.Option("data/applications.json", help="Path to the application tracker JSON file.")
):
    retriever = ApplicationRetriever()
    retriever.load_records(app_tracker_path)
    retriever.build_documents()
    results = retriever.retrieve(query, top_k)
    if not results:
        print("No relevant applications found.")
        return
    else:
        digit = len(results)
        table = Table(title= f"Top-{digit} Application Record Related to User's Query")
        table.add_column("Application ID", justify="center", style="cyan", no_wrap=True)
        table.add_column("Company", justify="center", style="white", no_wrap=True)
        table.add_column("Role", justify="center", style="magenta", no_wrap=True)
        table.add_column("Status", justify="center", style="blue", no_wrap=True)
        table.add_column("Match Score", justify="center", style="green", no_wrap=True)
        table.add_column("Retrieval Score", justify="center", style="green", no_wrap=True)

        for app in results:
            table.add_row(app["application_id"], app["company"], app["role"], app["status"], str(app["match_score"]), str(app["retrieval_score"]))
        
        console = Console()
        console.print(table)

@app.command()
def ask_memory(
    query: str = typer.Argument(..., help="Ask query for past applications."),
    use_mock_llm: bool = typer.Option(True, help='Use MOCKLLM placeholder or real LLM API'),
    top_k: int = typer.Option(3, help="Search for the top-k application records related to the query."),
    app_tracker_path: str = typer.Option("data/applications.json", help="Path to the application tracker JSON file."),
    retrieval_mode: str = typer.Option("keyword", help="Retrieval mode: keyword, embedding, or chroma."),
    use_mock_embedding: bool = typer.Option(True, help="Use mock embedding client or real embedding API.")
):
    answers = run_application_memory_query(
        query = query,
        use_mock_llm = use_mock_llm,
        top_k = top_k,
        app_tracker_path = app_tracker_path,
        retrieval_mode=retrieval_mode,
        use_mock_embedding=use_mock_embedding
    )
    print(answers['answer'])
    # print(answers['retrieved_results'])

@app.command()
def agent(
    request: str = typer.Argument(..., help="Natural-language request for the ReAct agent."),
    use_mock_llm: bool = typer.Option(False, help="Use mock LLM instead of real LLM."),
    max_steps: int = typer.Option(5, help="Maximum number of ReAct tool-calling steps."),
    default_jd_path: str = typer.Option("data/sample_jd.txt", help="Default job description path."),
    default_profile_path: str = typer.Option("data/candidate_profile.example.json", help="Default candidate profile path."),
    default_tracker_path: str = typer.Option("data/applications.json", help="Default application tracker path."),
    default_retrieval_mode: str = typer.Option("chroma", help="Default retrieval mode: keyword, embedding, or chroma."),
):
    """Run the ReAct-style job application agent."""
    result = run_react_workflow(
        user_request=request,
        use_mock_llm=use_mock_llm,
        max_steps=max_steps,
        default_jd_path=default_jd_path,
        default_profile_path=default_profile_path,
        default_tracker_path=default_tracker_path,
        default_retrieval_mode=default_retrieval_mode,
    )

    console = Console()

    # console.print("\n[bold green]Final Answer[/bold green]")
    # console.print(result.get("final_answer", ""))

    # console.print("\n[bold cyan]Tool Trace[/bold cyan]")
    # for i, obs in enumerate(result.get("observations", []), start=1):
    #     console.print(f"\n[bold]Step {i}[/bold]")
    #     console.print(f"[yellow]Thought:[/yellow] {obs.get('thought', '')}")
    #     console.print(f"[yellow]Action:[/yellow] {obs.get('action', '')}")
    #     console.print(f"[yellow]Action Input:[/yellow] {obs.get('action_input', {})}")
    #     console.print(f"[yellow]Observation:[/yellow] {obs.get('observation', {})}")

    # console.print(f"\n[bold]Steps used:[/bold] {result.get('steps_used', 'unknown')}")
    console.print(Panel(result.get("final_answer", ""), title="Final Answer"))

    table = Table(title="ReAct Tool Trace")
    table.add_column("Step")
    table.add_column("Action")
    table.add_column("Thought")
    table.add_column("Observation Summary")

    for i, obs in enumerate(result.get("observations", []), start=1):
        observation_text = json.dumps(
            obs.get("observation", {}),
            indent=2,
            default=str,
        )

        table.add_row(
            str(i),
            obs.get("action", ""),
            obs.get("thought", ""),
            observation_text[:500],
        )

    console.print(table)

if __name__ == "__main__":
    app()