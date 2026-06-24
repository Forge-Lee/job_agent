from src.schemas.models import ParsedJD

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
        "document understanding",
        "document ai",
        "ocr",
        "machine learning",
        "deep learning",
        "multimodal ai",
        "multimodal systems",
        "ai agents",
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

class JDParser:
    def parse(self, text: str) -> ParsedJD:
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



# test codes
# with open('C:\\Users\\15654\\Desktop\\coding\\job_agent\\data\\sample_jd.txt', 'r') as file:
#     job_description = file.read()
# file.close()

# lines = get_non_empty_lines(job_description)

# print(extract_line_after_prefix(lines, "Company:"))
# print(extract_section_items(
#     lines,
#     "Responsibilities:",
#     ["Required Qualifications:", "Preferred Qualifications:", "Internship Details:"]
# ))