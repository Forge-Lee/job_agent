from pathlib import Path
import json

from src.schemas.models import ParsedJD, MatchResult

def format_bullets(items: list[str]) -> str:
    if not items:
        return "- Not specified"
    return "\n".join(f"- {item}" for item in items)

def format_role_overview(parsed_jd: ParsedJD) -> str:
    res = '## Role Overview \n\n'
    info = [
        'Company: ' + parsed_jd.company,
        'Role: ' + parsed_jd.role,
        'Employment Type: ' + parsed_jd.employment_type,
        'Location: ' + parsed_jd.location,
        'Start Date: ' + parsed_jd.start_date,
        'Duration: ' + parsed_jd.duration
    ]
    bulleted_output = format_bullets(info)
    res += bulleted_output

    return res

def format_strengths(match_result: MatchResult) -> str:
    res = '## Key Strengths \n\n'
    bulleted_strength = format_bullets(match_result.strengths)
    res += bulleted_strength
    return res


def format_gaps(match_result: MatchResult, max_items: int = 5) -> str:
    res = '## Potential Gaps \n\n'
    bulleted_gaps = format_bullets(match_result.gaps[:max_items])
    gap_length = len(match_result.gaps)
    if gap_length >= max_items:
        returning_gaps = f'Listing top {max_items} gaps. \n'
    else:
        returning_gaps = f'Listing top {gap_length} gaps. \n'
    
    returning_gaps += bulleted_gaps
    res += returning_gaps
    return res

def format_req_qualification(match_result: MatchResult) -> str:
    res = '## Matched Required Qualifications \n\n'
    bulleted_gaps = format_bullets(match_result.matched_required_skills)
    res += bulleted_gaps
    return res

def format_pre_qualification(match_result: MatchResult) -> str:
    res = '## Matched Preferred Qualifications \n\n'
    bulleted_gaps = format_bullets(match_result.matched_preferred_skills)
    res += bulleted_gaps
    return res

def format_proj(match_result: MatchResult) -> str:
    res = '## Relevant Projects \n\n'
    bulleted_gaps = format_bullets(match_result.relevant_projects)
    res += bulleted_gaps
    return res

class MaterialGenerator:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def generate_match_report(
        self,
        parsed_jd: ParsedJD,
        match_result: MatchResult,
        candidate_profile: dict
    ) -> str:
        section = []

        candidate_name = candidate_profile.get("name", "Candidate")

        section.append('# Job Matching Report')
        section.append(f'## Candidate \n\n{candidate_name}')
        section.append(format_role_overview(parsed_jd))
        section.append(f'## Match Score \n\nOverall Match Score: {str(match_result.match_score)}')
        section.append(format_strengths(match_result))
        section.append(format_gaps(match_result))
        section.append(format_req_qualification(match_result))
        section.append(format_pre_qualification(match_result))
        section.append(format_proj(match_result))
        section.append(f'## Suggested Positioning \n\n{match_result.positioning_summary}')

        return '\n\n'.join(section)

    def generate_cover_letter(
        self,
        parsed_jd: ParsedJD,
        match_result: MatchResult,
        candidate_profile: dict
    ) -> str:
        if self.llm_client is None:
            raise ValueError("LLM client is required for cover letter generation.")

        prompt_template = Path("src/prompts/cover_letter_prompt.txt").read_text(
            encoding="utf-8"
        )

        prompt = prompt_template.format(
            job_info=parsed_jd.model_dump_json(indent=2),
            candidate_profile=json.dumps(candidate_profile, indent=2),
            match_result=match_result.model_dump_json(indent=2),
        )

        return self.llm_client.generate_text(prompt)
    
    def generate_linkedin_message(
        self,
        parsed_jd: ParsedJD,
        match_result: MatchResult,
        candidate_profile: dict,
    ) -> str:
        if self.llm_client is None:
            raise ValueError("LLM client is required for follow-up message generation.")

        prompt_template = Path("src/prompts/linkedin_message_prompt.txt").read_text(
            encoding="utf-8"
        )

        prompt = prompt_template.format(
            job_info=parsed_jd.model_dump_json(indent=2),
            candidate_profile=json.dumps(candidate_profile, indent=2),
            match_result=match_result.model_dump_json(indent=2),
        )

        return self.llm_client.generate_text(prompt)
    
    def generate_resume_bullets(
        self,
        parsed_jd: ParsedJD,
        match_result: MatchResult,
        candidate_profile: dict
    ) -> str:
        if self.llm_client is None:
            raise ValueError("LLM client is required for recommended resume bullets generation.")

        prompt_template = Path("src/prompts/resume_bullets_prompt.txt").read_text(
            encoding="utf-8"
        )

        prompt = prompt_template.format(
            job_info=parsed_jd.model_dump_json(indent=2),
            candidate_profile=json.dumps(candidate_profile, indent=2),
            match_result=match_result.model_dump_json(indent=2),
        )

        return self.llm_client.generate_text(prompt)