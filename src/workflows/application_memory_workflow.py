from src.utils.llm_client import MockLLMClient, OpenAIClient
from src.tools.application_retriever import ApplicationRetriever
from src.agents.application_memory_agent import ApplicationMemoryAgent
from src.tools.embedding_application_retriever import EmbeddingApplicationRetriever
from src.utils.embedding_client import MockEmbeddingClient, OpenAIEmbeddingClient

def run_application_memory_query(
    query: str,
    use_mock_llm: bool = True,
    top_k: int = 3,
    app_tracker_path: str = "data/applications.json",
    retrieval_mode: str = "keyword",
    use_mock_embedding: bool = True,
    verbose: bool = True
):
    if retrieval_mode == 'keyword':
        retriever = ApplicationRetriever()
        retriever.load_records(app_tracker_path)
        retriever.build_documents()
        retrieved_results = retriever.retrieve(query, top_k)

    elif retrieval_mode == 'embedding':
        if use_mock_embedding:
            embedding_client = MockEmbeddingClient()
        else:
            embedding_client = OpenAIEmbeddingClient()

            retriever = EmbeddingApplicationRetriever(
                embedding_client=embedding_client,
                app_tracker_path=app_tracker_path,
            )

            retriever.load_records()
            retriever.build_documents()
            retriever.build_embedding_index()

            retrieved_results = retriever.retrieve(query, top_k)
    else:
        raise ValueError(f"Unsupported retrieval_mode: {retrieval_mode}")

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