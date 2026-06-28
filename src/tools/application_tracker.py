import json
import os
from pathlib import Path
import datetime

class ApplicationTracker:
    def __init__(self, app_tracker_path: str = "data/applications.json"):
        self.record = None # list[dict], stores all the application records
        self.app_tracker_path = app_tracker_path

    def load_applications(self, path: str) -> list[dict]:
        if not os.path.isfile(path):
            return []
        return json.loads(Path(path).read_text(encoding="utf-8"))

    def save_applications(self, applications: list[dict]) -> None:
        ''' format
        applications = [{
            "id" = 'not specified'
            "company" = 'not specified'
            "role" = 'not specified'
            "status" = 'not specified'
            "match_score" = 0.0
            "jd_path" = 'not specified'
            "match_report_path" = 'not specified'
            "cover_letter_path" = 'not specified'
            "linkedin_message_path" = 'not specified'
            "notes" = []
            "created_at" = 'not specified'
            "updated_at"  ='not specified'
        }]
        '''

        current_json_str = json.dumps(applications, indent=2)

        output_path = Path(self.app_tracker_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(current_json_str, encoding="utf-8")

    def add_application(self, record: dict) -> None:
        if self.record is None:
            self.record = self.load_applications(self.app_tracker_path)
        self.record.append(record)
        
        self.save_applications(self.record)

    def list_applications(self) -> list[dict]:
        if self.record is None:
            self.record = self.load_applications(self.app_tracker_path)
        return self.record
    
    def find_application(self, id: str):
        if self.record is None:
            self.record = self.load_applications(self.app_tracker_path)
        for rec in self.record:
            app_id = rec.get("id")
            if id == app_id:
                return rec
        return None
        
    def update_status(self, id: str, status: str):
        if self.record is None:
            self.record = self.load_applications(self.app_tracker_path)
        
        target = self.find_application(id)
        if target:
            self.record.remove(target)
            target['status'] = status
            target['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.record.append(target)
            self.save_applications(self.record)
        else:
            raise ValueError("Application not found")
        