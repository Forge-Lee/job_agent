import json
import os
from pathlib import Path
from typing import Any
import numpy as np

from src.tools.file_loader import load_json, save_json

class EmbeddingApplicationRetriever:
    # RAG v1: keyword-matching RAG -> done
    # RAG v2: hand-written embedding RAG
    # RAG v3: engineering embedding RAG with Chroma etc.
    def __init__(
            self, 
            embedding_client, 
            app_tracker_path="data/applications.json",
            embedding_index_path: str = "data/application_embeddings.json"
        ):
        self.embedding_client = embedding_client
        self.app_tracker_path = app_tracker_path
        self.embedding_index_path = embedding_index_path

        self.records = []
        self.documents = []
        self.embedding_index = []

    def load_records(self):
        if not os.path.isfile(self.app_tracker_path):
            self.record = []
        else:
            self.record = json.loads(Path(self.app_tracker_path).read_text(encoding="utf-8"))
        return self.record

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
                    """

            doc = {
                "application_id": rec.get("id", ""),
                "company": rec.get("company", ""),
                "role": rec.get("role", ""),
                "status": rec.get("status", ""),
                "match_score": rec.get("match_score", 0),
                "text": text.strip(),
            }

            self.documents.append(doc)

        return self.documents

    def build_embedding_index(self):
        if not self.documents:
            self.build_documents()

        self.embedding_index = []

        for doc in self.documents:
            embedding = self.embedding_client.embed_text(doc["text"])

            index_item = {
                "application_id": doc["application_id"],
                "company": doc["company"],
                "role": doc["role"],
                "status": doc["status"],
                "match_score": doc["match_score"],
                "text": doc["text"],
                "embedding": embedding,
            }

            self.embedding_index.append(index_item)

        return self.embedding_index

    def save_embedding_index(self):
        ...

    def load_embedding_index(self):
        ...

    def retrieve(self, query: str, top_k: int = 3):
        ...