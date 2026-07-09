from src.utils.llm_client import MockLLMClient, OpenAIClient
from src.tools.application_retriever import ApplicationRetriever
from src.agents.application_memory_agent import ApplicationMemoryAgent

def run_application_memory_query(
    query: str,
    use_mock_llm: bool = True,
    top_k: int = 3,
    app_tracker_path: str = "data/applications.json",
    verbose: bool = True
):
    retriever = ApplicationRetriever()
    retriever.load_records(app_tracker_path)
    retriever.build_documents()
    retrieved_results = retriever.retrieve(query, top_k)

    if not retrieved_results:
        ans = "No relevant application records were found for this query."
        return {
            "query": query,
            "retrieved_results": [],
            "answer": ans,
        }

    if use_mock_llm:
        llm_client = MockLLMClient()
        if verbose:
            print('Using MockLLMClient as api placeholder.')
    else:
        llm_client = OpenAIClient()
        if verbose:
            print('Using real LLM API as backend.')
    
    application_mem_agent = ApplicationMemoryAgent(llm_client)
    ans = application_mem_agent.ask(query, retrieved_results)

    res = {
        "query": query,
        "retrieved_results": retrieved_results,
        "answer": ans,
    }

    return res