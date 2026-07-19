from src.agents.react_agent import ReActAgent
from src.utils.llm_client import MockLLMClient, OpenAIClient


def run_react_workflow(
    user_request: str,
    use_mock_llm: bool = True,
    max_steps: int = 3,
    default_jd_path: str = "data/sample_jd.txt",
    default_profile_path: str = "data/candidate_profile.example.json",
    default_tracker_path: str = "data/applications.json",
    default_retrieval_mode: str = "chroma",
    default_use_llm_jd_parser: bool = True,
    default_use_llm_matcher: bool = True,
    default_use_mock_embedding: bool = False,
) -> dict:
    if use_mock_llm:
        llm_client = MockLLMClient()
    else:
        llm_client = OpenAIClient()

    runtime_context = {
        "default_jd_path": default_jd_path,
        "default_profile_path": default_profile_path,
        "default_tracker_path": default_tracker_path,
        "default_retrieval_mode": default_retrieval_mode,
        "default_use_llm_jd_parser": default_use_llm_jd_parser,
        "default_use_llm_matcher": default_use_llm_matcher,
        "default_use_mock_embedding": default_use_mock_embedding,
    }

    agent = ReActAgent(
        llm_client=llm_client,
        max_steps=max_steps,
        runtime_context=runtime_context,
    )

    return agent.run(user_request)