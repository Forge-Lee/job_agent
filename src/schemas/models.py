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