# Workflow Design

## Goal

The goal of this project is to build a structured job application assistant that helps users analyze job descriptions, compare them with a candidate profile, and generate tailored application materials.

Instead of directly asking an LLM to write a cover letter, this project decomposes the job application process into multiple intermediate reasoning and generation steps.

## Input

The system takes two main inputs:

1. `job_description.txt`

A raw job description copied from a company career page or job board.

2. `candidate_profile.json`

A structured representation of the candidate's background, including education, skills, projects, experiences, and preferred role directions.

## Output

The system produces:

1. A structured job match report
2. A tailored cover letter draft
3. A LinkedIn recruiter follow-up message
4. A saved application tracking record

## Agent Pipeline

### 1. JD Parser

The JD Parser converts an unstructured job description into structured role metadata.

Expected output:

```json
{
  "company": "Example Company",
  "role": "AI Intern",
  "employment_type": "internship",
  "required_skills": [],
  "preferred_skills": [],
  "responsibilities": [],
  "start_date": "not specified",
  "sponsorship": "not mentioned"
}
```

### 2. Requirement Extractor

The Requirement Extractor identifies the most important qualifications and responsibilities from the parsed job description.

It separates information into:

- Required skills
- Preferred skills
- Responsibilities
- Domain knowledge
- Tools and technologies
- Eligibility constraints

## 3. Profile Matcher

The Profile Matcher compares job requirements with the candidate profile.

It produces:

- Matched skills
- Relevant projects
- Missing or weaker areas
- Estimated match score
- Suggested positioning strategy

## 4. Gap Analyzer

The Gap Analyzer identifies areas where the candidate may not fully match the role.

It also suggests how to mitigate those gaps through related experience.

Example:

``` json
{
  "gap": "Limited OCR-specific experience",
  "mitigation": "Emphasize computer vision, image processing, and document-related preprocessing experience."
}
```

## 5. Material Generator

The Material Generator creates human-reviewable application materials.

Expected outputs:

- Match report
- Cover letter draft
- LinkedIn follow-up message
- Resume bullet suggestions

The generated materials should be grounded in the candidate profile and should not invent experiences.

## 6. Application Tracker

The Application Tracker stores basic metadata about each analyzed job.

Example:

``` json
{
  "company": "Example Company",
  "role": "AI Intern",
  "date_added": "2026-06-21",
  "match_score": 0.78,
  "status": "materials_generated",
  "tags": ["AI", "ML", "internship"]
}
```

## Design Principles

### Structured Intermediate State

Each step should produce structured output, preferably JSON or Pydantic models. This makes the workflow easier to debug, test, and extend.

### Human-in-the-loop

The agent should generate drafts and recommendations, but the user should review and edit final application materials.

### Grounded Generation

Generated text should only use information from the job description and candidate profile. The system should avoid inventing projects, skills, or experiences.

### Modular Design

Each agent or tool should be implemented as a separate module so that the system can be extended later.

### Future Extensions

- Add resume PDF parsing
- Add SQLite-based tracking
- Add RAG over past applications
- Add Streamlit UI
- Add evaluation checks for generated materials
- Add LangGraph-based state management

