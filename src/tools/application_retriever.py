import os
import json
from pathlib import Path

class ApplicationRetriever():
    def __init__(self):
        self.record = None # list[dict], stores all the application records
        self.documents = []
        self.document_scores = {}
        
    def load_records(self, record_path: str = 'data/applications.json'):
        if not os.path.isfile(record_path):
            self.record = []
        else:
            self.record = json.loads(Path(record_path).read_text(encoding="utf-8"))
        return self.record

    def build_documents(
            self, 
            match_report_path: str | None = None, 
            resume_bullet_path: str | None = None
        ):
        self.documents = []

        for rec in self.record:
            rec_comp = rec['company']
            rec_role = rec['role']
            app_id = rec['id']
            doc = {
                'application_id': app_id,
                'company': rec_comp,
                'role': rec_role,
                'status': rec['status'],
                'match_score': rec['match_score'],
                'notes': rec['notes']
            }

            current_match_report_path = match_report_path if match_report_path is not None else rec.get("match_report_path")
            current_resume_bullet_path = resume_bullet_path if resume_bullet_path is not None else rec.get("resume_bullets_path")
            
            if current_match_report_path and os.path.isfile(current_match_report_path):
                match_record = Path(current_match_report_path).read_text(encoding="utf-8")
            else:
                match_record = ''

            if current_resume_bullet_path and os.path.isfile(current_resume_bullet_path):
                bullets_record = Path(current_resume_bullet_path).read_text(encoding="utf-8")
            else:
                bullets_record = ''

            doc['text'] = match_record + ' ' + bullets_record

            self.documents.append(doc)


    def score_documents(self, query: str):
        query_lower = query.lower()
        query_splitted = query_lower.split(' ')
        query_kw = []
        for words in query_splitted:
            if len(words) > 2:
                query_kw.append(words)
            
        for doc in self.documents:
            app_id = doc['application_id']
            txt = doc['text']
            txt_lower = txt.lower()
            score = 0
            for kw in query_kw:
                if kw in txt_lower:
                    score += 1
            self.document_scores[app_id] = score

    def retrieve(self, query: str, top_k: int = 3):
        self.document_scores = {}

        if self.record is None:
            self.load_records()

        if not self.documents:
            self.build_documents()

        self.score_documents(query)

        sorted_scores = sorted(
            self.document_scores.items(),
            key=lambda item: item[1],
            reverse=True
        )
        top_results = sorted_scores[:top_k]

        res = []
        for app_id, score in top_results:
            for doc in self.documents:
                if score > 0 and doc['application_id'] == app_id:
                    curr_res = {
                        'application_id': app_id,
                        'company': doc['company'],
                        'role': doc['role'],
                        'status': doc['status'],
                        'match_score': doc['match_score'],
                        "retrieval_score": score
                    }
                    res.append(curr_res)

        return res