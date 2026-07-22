import hashlib
import random
from typing import List
import os
from openai import OpenAI
from dotenv import load_dotenv

class MockEmbeddingClient:
    """
    Deterministic mock embedding client for testing the retrieval pipeline.

    This does not produce meaningful semantic embeddings.
    It only ensures that the same text always maps to the same vector.
    """

    def __init__(self, dimension: int = 64):
        self.dimension = dimension
        self.provider = "mock"
        self.model_name = "mock"

    def embed_text(self, text: str) -> list[float]:
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)

        return [rng.uniform(-1.0, 1.0) for _ in range(self.dimension)]

class OpenAIEmbeddingClient:
    """
    OpenAI embedding client for semantic retrieval.
    """

    def __init__(self):
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("BASE_URL")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Please set it in your .env file.")
        if not base_url:
            raise ValueError("BASE_URL is missing. Please set it in your .env file.")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = os.getenv("EMBEDDING_MODEL_NAME", "gpt-4o-mini")
        self.provider = "gemini"
        self.dimension = 3072

    def embed_text(self, text: str) -> list[float]:
        """
        Convert input text into an embedding vector.
        """
        text = text.strip()
        if not text:
            raise ValueError("Input text for embedding cannot be empty.")


        response = self.client.embeddings.create(
            model= self.model_name,
            input= text,
            encoding_format="float"
        )
        return response.data[0].embedding