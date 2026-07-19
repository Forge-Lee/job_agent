from pathlib import Path

from src.workflows.job_analysis_workflow import run_job_analysis
from src.workflows.application_memory_workflow import run_application_memory_query
from src.tools.application_tracker import ApplicationTracker


def coerce_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
    raise ValueError("must be a boolean")

def validate_tool_args(action: str, args: dict) -> tuple[bool, dict, str | None]:
    if not isinstance(args, dict):
        return False, {}, "action_input must be a JSON object."

    fixed_args = dict(args)

    if action == "analyze_job":
        bool_fields = [
            "use_mock_llm",
            "use_llm_jd_parser",
            "use_llm_matcher",
            "generate_cover_letter",
            "generate_linkedin_message",
            "generate_resume_bullets",
            "save_application",
        ]

        for field in bool_fields:
            if field in fixed_args:
                try:
                    fixed_args[field] = coerce_bool(fixed_args[field])
                except ValueError:
                    return False, fixed_args, f"{field} must be a boolean."

        return True, fixed_args, None

    if action == "ask_memory":
        if not fixed_args.get("query"):
            return False, fixed_args, "ask_memory requires a non-empty query."

        if fixed_args.get("retrieval_mode") not in [None, "keyword", "embedding", "chroma"]:
            return False, fixed_args, "retrieval_mode must be keyword, embedding, or chroma."

        if "top_k" in fixed_args:
            try:
                fixed_args["top_k"] = int(fixed_args["top_k"])
            except Exception:
                return False, fixed_args, "top_k must be an integer."

        return True, fixed_args, None

    if action == "list_applications":
        return True, fixed_args, None

    return False, fixed_args, f"Unknown action: {action}"

class ToolExecutor:
    def __init__(self, runtime_context: dict | None = None):
        self.runtime_context = runtime_context or {}

    def resolve_existing_path(self, path: str | None, default_path: str) -> str:
        if path and Path(path).is_file():
            return path
        return default_path

    def analyze_job(self, args: dict) -> dict:
        default_jd_path = self.runtime_context.get(
            "default_jd_path",
            "data/sample_jd.txt",
        )
        default_profile_path = self.runtime_context.get(
            "default_profile_path",
            "data/candidate_profile.example.json",
        )

        jd_path = self.resolve_existing_path(
            args.get("jd_path"),
            default_jd_path,
        )
        profile_path = self.resolve_existing_path(
            args.get("profile_path"),
            default_profile_path,
        )

        use_llm_jd_parser=args.get(
            "use_llm_jd_parser",
            self.runtime_context.get("default_use_llm_jd_parser", True),
        )

        use_llm_matcher=args.get(
            "use_llm_matcher",
            self.runtime_context.get("default_use_llm_matcher", True),
        )

        if not Path(jd_path).is_file():
            return {
                "error": f"Job description file not found: {jd_path}",
                "available_default_jd_path": default_jd_path,
            }

        if not Path(profile_path).is_file():
            return {
                "error": f"Candidate profile file not found: {profile_path}",
                "available_default_profile_path": default_profile_path,
            }

        return run_job_analysis(
            jd_path=jd_path,
            profile_path=profile_path,
            use_mock_llm=args.get("use_mock_llm", True),
            use_llm_jd_parser=use_llm_jd_parser,
            use_llm_matcher=use_llm_matcher,
            generate_cover_letter=args.get("generate_cover_letter", False),
            generate_linkedin_message=args.get("generate_linkedin_message", False),
            generate_resume_bullets=args.get("generate_resume_bullets", False),
            save_application=args.get("save_application", False),
            verbose=False,
        )

    def ask_memory(self, args: dict) -> dict:
        default_tracker_path = self.runtime_context.get(
            "default_tracker_path",
            "data/applications.json",
        )
        default_retrieval_mode = self.runtime_context.get(
            "default_retrieval_mode",
            "chroma",
        )

        use_mock_embedding = args.get(
            "use_mock_embedding",
            self.runtime_context.get("default_use_mock_embedding", True),
        )

        app_tracker_path = self.resolve_existing_path(
            args.get("app_tracker_path"),
            default_tracker_path,
        )

        return run_application_memory_query(
            query=args.get("query", ""),
            top_k=args.get("top_k", 3),
            use_mock_llm=args.get("use_mock_llm", True),
            retrieval_mode=args.get("retrieval_mode", default_retrieval_mode),
            use_mock_embedding=use_mock_embedding,
            app_tracker_path=app_tracker_path,
            verbose=False,
        )

    def list_applications(self, args: dict) -> dict:
        default_tracker_path = self.runtime_context.get(
            "default_tracker_path",
            "data/applications.json",
        )

        app_tracker_path = self.resolve_existing_path(
            args.get("app_tracker_path"),
            default_tracker_path,
        )

        tracker = ApplicationTracker(app_tracker_path)
        applications = tracker.list_applications()

        return {"applications": applications}

    def get_tool_registry(self) -> dict:
        return {
            "analyze_job": self.analyze_job,
            "ask_memory": self.ask_memory,
            "list_applications": self.list_applications,
        }