from src.utils.embedding_client import MockEmbeddingClient, OpenAIEmbeddingClient
from src.tools.embedding_application_retriever import EmbeddingApplicationRetriever

print('Script starts')
embedding_client =MockEmbeddingClient()

retriever = EmbeddingApplicationRetriever(
    embedding_client=embedding_client,
    app_tracker_path="data/applications.example.json",
)

retriever.load_records()
retriever.build_documents()
retriever.build_embedding_index()

results = retriever.retrieve(
    query="Which applications are related to AI project internships and computer vision?",
    top_k=3,
)

for result in results:
    print(result["application_id"])
    print(result["company"])
    print(result["role"])
    print(result["retrieval_score"])
    print("-" * 40)