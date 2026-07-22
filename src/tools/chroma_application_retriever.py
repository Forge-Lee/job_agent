import os
from pathlib import Path
import json

import chromadb
import re


def sanitize_collection_part(value: str) -> str:
    value = str(value).lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = value.strip("_")
    return value or "unknown"


def build_chroma_collection_name(
    base_name: str,
    provider: str,
    model_name: str,
    embedding_dim: int | str,
) -> str:
    provider = sanitize_collection_part(provider)
    model_name = sanitize_collection_part(model_name)
    embedding_dim = sanitize_collection_part(embedding_dim)

    return f"{base_name}_{provider}_{model_name}_{embedding_dim}"

class ChromaApplicationRetriever:
    def __init__(
        self,
        embedding_client,
        app_tracker_path: str = "data/applications.json",
        chroma_path: str = "data/chroma_db",
        collection_name: str = "application_memory",
    ):
        self.embedding_client = embedding_client
        self.app_tracker_path = app_tracker_path
        self.chroma_path = chroma_path
        self.collection_name = collection_name

        self.records = []
        self.documents = []

        self.client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def load_records(self):
        if not os.path.isfile(self.app_tracker_path):
            self.records = []
            return self.records

        self.records = json.loads(
            Path(self.app_tracker_path).read_text(encoding="utf-8")
        )
        return self.records

    def build_documents(self):
        if not self.records:
            self.load_records()

        self.documents = []

        for rec in self.records:
            match_report_text = ""
            resume_bullets_text = ""

            match_report_path = rec.get("match_report_path")
            resume_bullets_path = rec.get("resume_bullets_path")

            if match_report_path and os.path.isfile(match_report_path):
                match_report_text = Path(match_report_path).read_text(encoding="utf-8")

            if resume_bullets_path and os.path.isfile(resume_bullets_path):
                resume_bullets_text = Path(resume_bullets_path).read_text(encoding="utf-8")

            text = f"""
    Application ID: {rec.get("id", "")}
    Company: {rec.get("company", "")}
    Role: {rec.get("role", "")}
    Status: {rec.get("status", "")}
    Match Score: {rec.get("match_score", "")}
    Notes: {rec.get("notes", "")}

    Match Report:
    {match_report_text}

    Resume Bullets:
    {resume_bullets_text}
    """.strip()

            self.documents.append({
                "application_id": rec.get("id", ""),
                "company": rec.get("company", ""),
                "role": rec.get("role", ""),
                "status": rec.get("status", ""),
                "match_score": rec.get("match_score", 0),
                "text": text,
            })

        return self.documents

    def build_embedding_index(self):
        if not self.documents:
            self.build_documents()

        if not self.documents:
            return

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for doc in self.documents:
            ids.append(doc["application_id"])
            documents.append(doc["text"])
            embeddings.append(self.embedding_client.embed_text(doc["text"]))
            metadatas.append({
                "application_id": doc["application_id"],
                "company": doc["company"],
                "role": doc["role"],
                "status": doc["status"],
                "match_score": float(doc["match_score"] or 0),
            })

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def retrieve(self, query: str, top_k: int = 3):
        query_embedding = self.embedding_client.embed_text(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        retrieved_results = []

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for app_id, doc_text, metadata, distance in zip(ids, documents, metadatas, distances):
            retrieved_results.append({
                "application_id": metadata.get("application_id", app_id),
                "company": metadata.get("company", ""),
                "role": metadata.get("role", ""),
                "status": metadata.get("status", ""),
                "match_score": metadata.get("match_score", 0),
                "retrieval_score": round(1.0 - distance, 4),
                "retrieved_text": doc_text[:1500] if doc_text else "",
            })

        return retrieved_results