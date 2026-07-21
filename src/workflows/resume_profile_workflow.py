from src.agents.resume_parser import ResumeParser
from src.tools.resume_loader import load_resume_text
from src.utils.llm_client import MockLLMClient, OpenAIClient

from pathlib import Path
import json

def run_resume_profile_workflow(
    resume_path: str,
    output_profile_path: str = "data/profiles/resume_profile.json",
    use_mock_llm: bool = False,
) -> dict:
    loaded_resume = load_resume_text(resume_path=resume_path)
    llm_client = MockLLMClient()

    if not use_mock_llm:
        llm_client = OpenAIClient()

    resume_parser = ResumeParser(llm_client=llm_client)

    parsed_resume = resume_parser.parse_resume_text(loaded_resume)

    Path(output_profile_path).write_text(
        json.dumps(parsed_resume, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "profile": parsed_resume,
        "profile_path": output_profile_path,
        "resume_text_preview": loaded_resume[:1000],
    }