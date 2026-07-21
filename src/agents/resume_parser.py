from pathlib import Path
import json

def parse_llm_json_response(response: str) -> dict:
    cleaned = response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()

    if cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-len("```")].strip()

    return json.loads(cleaned)

def ensure_list(value) -> list[str]:
    res = []

    if isinstance(value, list):
        for i in value:
            if i is None:
                continue
            cleaned = str(i).strip()
            if cleaned:
                res.append(cleaned)
        return res

    elif isinstance(value, str):
        sliced = value.split(',')
        for i in sliced:
            cleaned = i.strip()
            if cleaned:
                res.append(i.strip())
        return res
    
    elif value == None:
        return res
    
    else:
        cleaned = str(value).strip()
        if cleaned:
            res.append(cleaned)
        return res

def ensure_string(value) -> str:
    if value == None:
        return ""
    
    elif isinstance(value, str):
        return value.strip()
    
    else:
        return(str(value).strip())

def normalize_profile(profile: dict) -> dict:
    if not isinstance(profile, dict):
        profile = {}

    # education normalization
    raw_education = profile.get("education", [])
    cleaned_education = []
    formulated_education = []
    if isinstance(raw_education, dict):
        cleaned_education.append(raw_education)

    elif isinstance(raw_education, list):
        cleaned_education = raw_education

    else:
        cleaned_education = []

    for item in cleaned_education:
        if not isinstance(item, dict):
                continue
        normalized_edu = {
            "school": ensure_string(item.get("school")),
            "degree": ensure_string(item.get("degree")),
            "details": ensure_string(item.get("details")),
        }
        if normalized_edu["school"] or normalized_edu["degree"] or normalized_edu["details"]:
            formulated_education.append(normalized_edu)

    # skill normalization
    normalized_skills = {}
    skill_keys = [
        "programming",
        "machine_learning",
        "tools",
        "domains",
        "other",
    ]
    raw_skills = profile.get("skills", {})
    if not isinstance(raw_skills, dict):
        raw_skills = {}

    for key in skill_keys:
        normalized_skills[key] = ensure_list(raw_skills.get(key, []))

    # project normalization
    normalized_projects = []
    raw_projects = profile.get("projects", [])

    if isinstance(raw_projects, dict):
        formulated_project = {
            "name": ensure_string(raw_projects.get("name")),
            "description": ensure_string(raw_projects.get("description")),
            "keywords": ensure_list(raw_projects.get("keywords"))
        }
        if formulated_project["name"] or formulated_project["description"]:
            normalized_projects.append(formulated_project)

    elif isinstance(raw_projects, list):
        for item in raw_projects:
            if not isinstance(item, dict):
                continue
            formulated_project = {
                "name": ensure_string(item.get("name")),
                "description": ensure_string(item.get("description")),
                "keywords": ensure_list(item.get("keywords"))
            }
            if formulated_project["name"] or formulated_project["description"]:
                normalized_projects.append(formulated_project)

    else:
        normalized_projects = []
    
    return {
        "education": formulated_education,
        "skills": normalized_skills,
        "projects": normalized_projects,
    }

class ResumeParser:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def parse_resume_text(self, resume_text: str) -> dict:
        if self.llm_client is None:
            raise ValueError("LLM client is required for LLM-based resume parsing.")
        
        prompt_template = Path("src/prompts/resume_parser_prompt.txt").read_text(
            encoding="utf-8"
        )

        prompt = prompt_template.format(resume_text=resume_text)

        response = self.llm_client.generate_text(prompt)
        parsed = parse_llm_json_response(response)
        normalized = normalize_profile(parsed)

        return normalized