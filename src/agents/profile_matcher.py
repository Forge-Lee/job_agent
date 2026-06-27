from src.schemas.models import ParsedJD, MatchResult

def flatten_profile_skills(candidate_profile: dict) -> list[str]:
    res = []
    for _, val in candidate_profile['skills'].items():
        for skill in val:
            res.append(skill)
    
    if res:
        return res
    return []

def text_matches_profile(item: str, profile_terms: list[str]) -> bool:
    item_low = item.lower()
    for term in profile_terms:
        term_low = term.lower()
        if term_low in item_low or item_low in term_low:
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
    def match(self, parsed_jd: ParsedJD, candidate_profile: dict) -> MatchResult:
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

        candidate_tools = candidate_profile["skills"].get("tools", [])
        
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

        required_score = safe_ratio(len(matched_required_skills), len(parsed_jd.required_skills))
        preferred_score = safe_ratio(len(matched_preferred_skills), len(parsed_jd.preferred_skills))
        tool_score = safe_ratio(len(matched_tools), len(parsed_jd.tools))
        domain_score = safe_ratio(len(matched_domains), len(parsed_jd.domains))

        match_score = (
            0.5 * required_score
            + 0.2 * preferred_score
            + 0.15 * tool_score
            + 0.15 * domain_score
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
            
        filtering_kws = ['degree', 'currently pursuing', 'communication', 'documentation']
        if missing_required_skills:
            
            for item in missing_required_skills:
                block = False
                for kws in filtering_kws:
                    if kws in item:
                        block = True
                        break
                if not block:
                    gaps.append(f"Limited direct evidence for: {item}")
        
        if missing_preferred_skills:
            for item in missing_preferred_skills:
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