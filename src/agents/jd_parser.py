from src.schemas.models import ParsedJD
from pathlib import Path
import json

def get_non_empty_lines(text: str) -> list[str]:
    res = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            res.append(line)
    return res

def extract_line_after_prefix(text: list[str], prefix = 'Company: ') -> str:
    comp_name = ''
    for txt in text:
        if txt.startswith(prefix):
            comp_name = txt.split(prefix, 1)[1].strip()

    if comp_name != '':
        return comp_name
    else:
        return 'not specified'

def extract_section_items(
    text: list[str],
    start_heading: str,
    end_headings: list[str]
) -> list[str]:
    res = []
    record = False
    for line in text:
        if start_heading in line:
            record = True
            continue
        if not record:
            continue
        if line.strip() not in end_headings:
            # remove bullet
            if line.startswith('-'):
                item = line.lstrip("-").strip()
                if item:
                    res.append(item)
            continue
        record = False
        break
    if res != []:
        return res
    else:
        return []

def infer_employment_type(role: str, text: str) -> str:
    emp_sum = {
        'internship': ['internship', 'intern'],
        'full-time': ['full-time', 'full time', 'fulltime'],
        'part-time': ['part-time', 'part time', 'parttime',],
        'contract': ['contract'],
        'temporary': ['temporary'],
    }
    emp_type = ['internship', 'full-time', 'part-time', 'contract', 'temporary']
    role_low = role.lower()
    text_low = text.lower()
    for emp in emp_type:
        for rep in emp_sum[emp]:
            if rep in role_low:
                return emp

    for emp in emp_type:
        for rep in emp_sum[emp]:
            if rep in text_low:
                return emp
    
    return 'not specified'

def infer_tools(text: str) -> list[str]:
    tool_keywords = {
        "python": "Python",
        "pytorch": "PyTorch",
        "opencv": "OpenCV",
        "docker": "Docker",
        "sql": "SQL",
        "llm": "LLM",
        "rag": "RAG"
    }
    text_low = text.lower()
    res = []
    for keyword, display_name in tool_keywords.items():
        if keyword in text_low:
            res.append(display_name)
    
    if res:
        return res

    return []

def infer_domains(text: str) -> list[str]:
    domain_keywords = [
        "computer vision",
        "image processing",
        "object detection",
        "video analysis",
        "tracking",
        "document ai",
        "ocr",
        "machine learning",
        "deep learning",
        "multimodal ai",
        "ai agent",
        "agentic workflow",
    ]
    text_low = text.lower()
    res = []
    for domain in domain_keywords:
        if domain in text_low:
            res.append(domain)
    
    if res:
        return res
    return []

def parse_llm_json_response(response: str) -> dict:
    cleaned = response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()

    if cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-len("```")].strip()

    return json.loads(cleaned)

class JDParser:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def rule_based_parse(self, text: str) -> ParsedJD:
        self.lines = get_non_empty_lines(text)
        self.role = self.lines[0] if self.lines else "not specified"
        self.comp_name = extract_line_after_prefix(self.lines)
        self.responsibility = extract_section_items(
            self.lines, 
            "Responsibilities:", 
            ["Required Qualifications:", "Preferred Qualifications:", "Internship Details:"]
        )
        self.required_skills = extract_section_items(
            self.lines, 
            "Required Qualifications:", 
            ["Preferred Qualifications:", "Internship Details:"]
        )
        self.preferred_skills = extract_section_items(
            self.lines,
            start_heading="Preferred Qualifications:",
            end_headings=["Internship Details:"]
        )
        self.employment_type = infer_employment_type(self.lines[0], text)
        self.tools = infer_tools(text)
        self.domain = infer_domains(text)

        self.duration = extract_line_after_prefix(self.lines, "- Duration:")
        self.location = extract_line_after_prefix(self.lines, "- Location:")
        self.start_date = extract_line_after_prefix(self.lines, "- Start date:")

        return ParsedJD(
            company=self.comp_name,
            role=self.role,
            employment_type=self.employment_type,
            location=self.location,
            start_date=self.start_date,
            duration=self.duration,
            responsibilities=self.responsibility,
            required_skills=self.required_skills,
            preferred_skills=self.preferred_skills,
            tools=self.tools,
            domains=self.domain,
            sponsorship="not mentioned"
        )

    def llm_based_parse(self, text: str) -> ParsedJD:
        if self.llm_client is None:
            raise ValueError("LLM client is required for LLM-based JD parsing.")

        prompt_template = Path("src/prompts/jd_parser_prompt.txt").read_text(
            encoding="utf-8"
        )

        prompt = prompt_template.format(job_description=text)

        response = self.llm_client.generate_text(prompt)
        parsed = parse_llm_json_response(response)

        return ParsedJD(**parsed)

    def parse(self, text: str, use_llm_parser: bool = False) -> ParsedJD:
        if not use_llm_parser:
            return self.rule_based_parse(text)

        try:
            return self.llm_based_parse(text)
        except Exception:
            return self.rule_based_parse(text)
