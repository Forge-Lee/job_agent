import os
import json
from pathlib import Path

class ApplicationRetriever():
    def __init__(self):
        self.record = None # list[dict], stores all the application records
        self.documents = []
        self.match_record = None
        self.bullets_record = None
        
    def load_records(self, record_path: str = 'data/applications.json'):
        if not os.path.isfile(record_path):
            self.record = []
        else:
            self.record = json.loads(Path(record_path).read_text(encoding="utf-8"))
        return self.record

    def build_documents(self, match_report_path: str = 'outputs/match_report.md', resume_bullet_path: str = 'outputs/resume_bullets.md'):
        if not os.path.isfile(match_report_path):
            self.match_record = []
        else:
            self.match_record = Path(match_report_path).read_text(encoding="utf-8")

        if not os.path.isfile(resume_bullet_path):
            self.bullets_record = []
        else:
            self.bullets_record = Path(resume_bullet_path).read_text(encoding="utf-8")

        for rec in self.record:
            rec_comp = rec['company']
            rec_role = rec['role']
            doc = {
                'application_id': rec['id'],
                'company': rec_comp,
                'role': rec_role,
                'status': rec['status'],
                'match_score': rec['match_score'],
                'notes': rec['notes']
            }
            
            

    def score_documents(self):
        pass

    def retrieve(self, query: str, top_k: int = 3):
        pass