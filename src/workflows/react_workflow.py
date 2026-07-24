from src.agents.react_agent import ReActAgent
from src.utils.llm_client import MockLLMClient, OpenAIClient
from src.agents.reflection_agent import ReflectionAgent

def run_react_workflow(
    user_request: str,
    use_mock_llm: bool = True,
    use_langchain_reflection: bool = True,
    enable_reflection: bool = True,
    reflection_model_name: str = "gpt-4o-mini",
    provider: str = "openai",
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

    react_result = agent.run(user_request)

    if enable_reflection:
        reflection_agent = ReflectionAgent(
            llm_client=llm_client,
            use_langchain=use_langchain_reflection,
            model_name=reflection_model_name,
            provider=provider
        )
        reflection_result = reflection_agent.reflect(
            user_request=user_request,
            final_answer=react_result.get("final_answer", ""),
            observations=react_result.get("observations", []),
            completed_actions=react_result.get("completed_actions", []),
        )

        react_result["reflection"] = reflection_result.model_dump()

        if not reflection_result.passed:
            react_result["final_answer"] = reflection_result.revised_answer

    return react_result