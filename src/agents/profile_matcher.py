from src.schemas.models import ParsedJD, MatchResult
from pathlib import Path
import json

SKILL_ALIASES = {
    "machine learning": [
        "ml",
        "deep learning",
        "neural network",
        "model training",
        "supervised learning",
    ],
    "deep learning": [
        "dl",
        "neural network",
        "cnn",
        "rnn",
        "lstm",
        "gru",
        "pytorch",
        "tensorflow",
    ],
    "computer vision": [
        "cv",
        "image processing",
        "opencv",
        "object detection",
        "segmentation",
        "ocr",
        "visual recognition",
    ],
    "document ai": [
        "ocr",
        "document understanding",
        "invoice extraction",
        "form extraction",
        "receipt extraction",
        "text extraction",
    ],
    "large language model": [
        "llm",
        "gpt",
        "rag",
        "prompt engineering",
        "agent",
        "agentic workflow",
    ],
    "llm": [
        "large language model",
        "gpt",
        "rag",
        "prompt engineering",
        "agent",
        "agentic workflow",
    ],
    "rag": [
        "retrieval augmented generation",
        "retrieval",
        "embedding",
        "vector search",
        "semantic search",
    ],
    "data pipeline": [
        "preprocessing",
        "etl",
        "workflow",
        "automation",
        "data processing",
    ],
    "python": [
        "python programming",
        "scripting",
    ],
    "pytorch": [
        "torch",
        "deep learning",
        "model training",
    ],
    "opencv": [
        "computer vision",
        "image processing",
    ],
    "robotics": [
        "robot",
        "robot control",
        "motion planning",
        "perception",
        "autonomous systems",
    ],
}

def expand_term(term: str) -> list[str]:
    term_low = term.lower().strip()

    expanded_terms = {term_low}

    if term_low in SKILL_ALIASES:
        for alias in SKILL_ALIASES[term_low]:
            expanded_terms.add(alias.lower().strip())

    return list(expanded_terms)

def flatten_profile_skills(candidate_profile: dict) -> list[str]:
    res = []
    for _, val in candidate_profile['skills'].items():
        for skill in val:
            res.append(skill)
    
    if res:
        return res
    return []

SHORT_EXACT_TERMS = {"ai", "ml", "cv", "dl"}

def text_matches_profile(item: str, profile_terms: list[str]) -> bool:
    item_aliases = expand_term(item)

    profile_aliases = []
    for term in profile_terms:
        profile_aliases.extend(expand_term(term))

    for item_term in item_aliases:
        for profile_term in profile_aliases:
            if item_term in SHORT_EXACT_TERMS or profile_term in SHORT_EXACT_TERMS:
                if item_term == profile_term:
                    return True
            else:
                if item_term in profile_term or profile_term in item_term:
                    return True

    return False

def find_relevant_projects(parsed_jd: ParsedJD, candidate_profile: dict) -> list[str]:
    jd_terms = []
    jd_terms_no = set()
    required_skills = parsed_jd.required_skills
    preferred_skills = parsed_jd.preferred_skills
    required_tools = parsed_jd.tools
    job_domains = parsed_jd.domains

    relevant_proj = []

    for skill in required_skills:
        jd_terms_no.add(skill)
    for skill in preferred_skills:
        jd_terms_no.add(skill)
    for tool in required_tools:
        jd_terms_no.add(tool)
    for domain in job_domains:
        jd_terms_no.add(domain)

    for item in jd_terms_no:
        jd_terms.append(item)

    for proj in candidate_profile['projects']:
        keywords = proj['keywords']
        for kw in keywords:
            if text_matches_profile(kw, jd_terms):
                relevant_proj.append(proj["name"])
                break
    
    if relevant_proj:
        return relevant_proj
    
    return []

def safe_ratio(matched_count: int, total_count: int) -> float:
    if total_count == 0:
        return 0.0
    return matched_count / total_count

class ProfileMatcher:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def rule_based_match(self, parsed_jd: ParsedJD, candidate_profile: dict) -> MatchResult:
        matched_required_skills = []
        missing_required_skills = []
        matched_preferred_skills = []
        missing_preferred_skills = []
        matched_tools = []
        matched_domains = []
        relevant_projects = []
        strengths = []
        gaps = []
        positioning_summary = 'not specified'

        required_skills = parsed_jd.required_skills
        preferred_skills = parsed_jd.preferred_skills
        required_tools = parsed_jd.tools
        job_domains = parsed_jd.domains

        candidate_skills = flatten_profile_skills(candidate_profile)
        for proj in candidate_profile['projects']:
            keywords = proj['keywords']
            for kw in keywords:
                if kw not in candidate_skills:
                    candidate_skills.append(kw)
        
        for skill in required_skills:
            skill_low = skill.lower()
            if text_matches_profile(skill_low, candidate_skills):
                matched_required_skills.append(skill)
            else:
                missing_required_skills.append(skill)

        for skill in preferred_skills:
            skill_low = skill.lower()
            if text_matches_profile(skill_low, candidate_skills):
                matched_preferred_skills.append(skill)
            else:
                missing_preferred_skills.append(skill)

        for tool in required_tools:
            tool_low = tool.lower()
            if text_matches_profile(tool_low, candidate_skills):
                matched_tools.append(tool)
        
        for domain in job_domains:
            domain_low = domain.lower()
            if text_matches_profile(domain_low, candidate_skills):
                matched_domains.append(domain)

        relevant_projects = find_relevant_projects(parsed_jd, candidate_profile)

        filtering_kws = ['degree', 'currently pursuing', 'communication', 'documentation']
        technical_required_skills = []
        technical_preferred_skills = []
        matched_technical_required_skills = []
        matched_technical_preferred_skills = []

        for req_skills in parsed_jd.required_skills:
            req_skill_low = req_skills.lower()
            block = False
            for kw in filtering_kws:
                if kw in req_skill_low:
                    block = True
                    break
            if not block:
                technical_required_skills.append(req_skills)

        for req_skills in matched_required_skills:
            req_skill_low = req_skills.lower()
            block = False
            for kw in filtering_kws:
                if kw in req_skill_low:
                    block = True
                    break
            if not block:
                matched_technical_required_skills.append(req_skills)

        for pre_skills in parsed_jd.preferred_skills:
            pre_skills_low = pre_skills.lower()
            block = False
            for kw in filtering_kws:
                if kw in pre_skills_low:
                    block = True
                    break
            if not block:
                technical_preferred_skills.append(pre_skills)
        
        for pre_skills in matched_preferred_skills:
            pre_skills_low = pre_skills.lower()
            block = False
            for kw in filtering_kws:
                if kw in pre_skills_low:
                    block = True
                    break
            if not block:
                matched_technical_preferred_skills.append(pre_skills)

        required_score = safe_ratio(len(matched_technical_required_skills), len(technical_required_skills))
        preferred_score = safe_ratio(len(matched_technical_preferred_skills), len(technical_preferred_skills))
        tool_score = safe_ratio(len(matched_tools), len(parsed_jd.tools))
        domain_score = safe_ratio(len(matched_domains), len(parsed_jd.domains))
        project_score = min(len(relevant_projects) / 2, 1.0)

        match_score = (
            0.40 * required_score
            + 0.15 * preferred_score
            + 0.15 * tool_score
            + 0.15 * domain_score
            + 0.15 * project_score
        )
        match_score = round(match_score, 2)

        if matched_domains:
            strengths.append(
                f"Relevant domain background in {', '.join(matched_domains)}."
            )
        
        if matched_tools:
            strengths.append(
            f"Hands-on experience with tools such as {', '.join(matched_tools)}."
        )
            
        if relevant_projects:
            strengths.append(
            f"Relevant project experience: {', '.join(relevant_projects)}."
        )
            
        
        if missing_required_skills:
            
            for item in missing_required_skills:
                item_low = item.lower()
                block = False
                for kws in filtering_kws:
                    if kws in item_low:
                        block = True
                        break
                if not block:
                    gaps.append(f"Limited direct evidence for: {item}")
        
        if missing_preferred_skills:
            for item in missing_preferred_skills:
                item_low = item.lower()
                block = False
                for kws in filtering_kws:
                    if kws in item_low:
                        block = True
                        break
                if not block:
                    gaps.append(f"Limited direct evidence for: {item}")

        if "computer vision" in matched_domains:
            positioning_summary = "Position the candidate as an applied AI / computer vision engineer with experience in image processing, ML workflows, and structured project execution."
        elif "ai agents" in matched_domains or "LLM" in matched_tools:
            positioning_summary = "Position the candidate as an applied AI engineer interested in LLM-based workflows and agentic automation."
        else:
            positioning_summary = "Position the candidate around relevant ML engineering experience, project execution, and ability to learn domain-specific tools quickly."

        return MatchResult(
            match_score=match_score,
            matched_required_skills=matched_required_skills,
            missing_required_skills=missing_required_skills,
            matched_preferred_skills=matched_preferred_skills,
            missing_preferred_skills=missing_preferred_skills,
            matched_tools=matched_tools,
            matched_domains=matched_domains,
            relevant_projects=relevant_projects,
            strengths=strengths,
            gaps=gaps,
            positioning_summary=positioning_summary,
        )
    
    def llm_based_match(self, parsed_jd, candidate_profile, rule_result) -> dict:
        if self.llm_client is None:
            raise ValueError("LLM client is required for LLM-based profile matching.")

        prompt_template = Path("src/prompts/profile_match_prompt.txt").read_text(
            encoding="utf-8"
        )

        prompt = prompt_template.format(
            parsed_jd=parsed_jd.model_dump_json(indent=2),
            candidate_profile=json.dumps(candidate_profile, indent=2),
            rule_result=rule_result.model_dump_json(indent=2),
        )

        response = self.llm_client.generate_text(prompt)

        try:
            llm_result = json.loads(response)
        except json.JSONDecodeError:
            llm_result = {
                "llm_score": rule_result.match_score,
                "llm_strengths": [],
                "llm_gaps": ["LLM matcher returned invalid JSON."],
                "llm_reasoning_summary": response,
            }

        return llm_result

    def combine_results(self, rule_result, llm_result, rule_weight = 0.7, llm_weight = 0.3) -> MatchResult:
        try:
            llm_score = float(llm_result.get("llm_score", rule_result.match_score))
        except (TypeError, ValueError):
            llm_score = rule_result.match_score

        llm_score = max(0.0, min(llm_score, 1.0))

        final_score = (
            rule_weight * rule_result.match_score
            + llm_weight * llm_score
        )
        final_score = round(final_score, 2)

        llm_strengths = llm_result.get("llm_strengths", [])
        llm_gaps = llm_result.get("llm_gaps", [])
        llm_reasoning_summary = llm_result.get("llm_reasoning_summary", "")

        combined_strengths = list(rule_result.strengths)
        for strength in llm_strengths:
            combined_strengths.append(f"LLM semantic match: {strength}")

        combined_gaps = list(rule_result.gaps)
        for gap in llm_gaps:
            combined_gaps.append(f"LLM semantic gap: {gap}")

        positioning_summary = rule_result.positioning_summary
        if llm_reasoning_summary:
            positioning_summary = (
                f"{rule_result.positioning_summary}\n\n"
                f"LLM semantic assessment: {llm_reasoning_summary}"
            )

        return MatchResult(
            match_score=final_score,
            matched_required_skills=rule_result.matched_required_skills,
            missing_required_skills=rule_result.missing_required_skills,
            matched_preferred_skills=rule_result.matched_preferred_skills,
            missing_preferred_skills=rule_result.missing_preferred_skills,
            matched_tools=rule_result.matched_tools,
            matched_domains=rule_result.matched_domains,
            relevant_projects=rule_result.relevant_projects,
            strengths=combined_strengths,
            gaps=combined_gaps,
            positioning_summary=positioning_summary,
        )

    def match(self, parsed_jd, candidate_profile, use_llm_matcher=False) -> MatchResult:
        rule_result = self.rule_based_match(parsed_jd, candidate_profile)

        if not use_llm_matcher:
            return rule_result

        llm_result = self.llm_based_match(parsed_jd, candidate_profile, rule_result)
        return self.combine_results(rule_result, llm_result)