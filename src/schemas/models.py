from pydantic import BaseModel, Field

class ParsedJD(BaseModel):
    company: str = "not specified"
    role: str = "not specified"
    employment_type: str = "not specified"
    location: str = "not specified"
    start_date: str = "not specified"
    duration: str = "not specified"
    responsibilities: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    sponsorship: str = "not mentioned"

class MatchResult(BaseModel):
    match_score: float = 0.0
    matched_required_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    matched_preferred_skills: list[str] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)
    matched_tools: list[str] = Field(default_factory=list)
    matched_domains: list[str] = Field(default_factory=list)
    relevant_projects: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    positioning_summary: str = "not specified"