from src.utils.embedding_client import OpenAIEmbeddingClient
from src.tools.chroma_application_retriever import ChromaApplicationRetriever

embedding_client = OpenAIEmbeddingClient()

retriever = ChromaApplicationRetriever(
    embedding_client=embedding_client,
    app_tracker_path="data/applications.json",
)

print("Loading records...")
retriever.load_records()

print("Building documents...")
retriever.build_documents()

print("Building Chroma index...")
retriever.build_embedding_index()

print("Retrieving...")
results = retriever.retrieve(
    "Which applications are related to computer vision and OCR?",
    top_k=3,
)

for result in results:
    print(result["application_id"])
    print(result["company"])
    print(result["role"])
    print(result["retrieval_score"])
    print("-" * 40)