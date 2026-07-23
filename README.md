# AI Job Application Assistant Agent

## Overview

AI Job Application Assistant Agent is an end-to-end LLM-powered job application workflow system. It helps candidates parse resumes and job descriptions, evaluate candidate-job fit, generate tailored application materials, track applications, retrieve similar past opportunities, and run multi-step job analysis through a custom ReAct-style agent.

The project is designed not only to generate application text, but also to turn job search into a convenient, structured, traceable, and reusable workflow with persistent application memory, vector retrieval, and agent-based orchestration.

## Key Features

- **Resume-to-profile parsing**
  - Extracts text from PDF and DOCX resumes
  - Uses LLM-based parsing to generate candidate profile JSON
  - Supports downstream JD matching and agent workflows
  - Supports manually adding data to profile apart from the uploaded resume

- **Job description parsing**
  - Supports rule-based and LLM-based JD parsing
  - Extracts company, role, employment type, location, required skills, preferred skills, tools, and domains
  - Handles pasted JD text and local JD files

- **Hybrid candidate-job matching**
  - Combines rule-based skill matching with LLM-based semantic assessment
  - Identifies strengths, gaps, partial evidence, and positioning improvements
  - Uses evidence-aware matching to avoid treating indirect evidence as missing

- **Application material generation**
  - Generates cover letters, LinkedIn follow-up messages, and resume bullet suggestions
  - Includes validation checks for missing sections and material quality

- **Application tracking**
  - Stores application records in local JSON
  - Supports application status updates and upsert-style tracking

- **Application memory and RAG**
  - Retrieves similar past applications using keyword search, embedding similarity, or Chroma vector search
  - Separates Chroma collections by embedding backend and dimension to avoid vector mismatch issues

- **Custom ReAct agent**
  - Plans multi-step workflows over tools such as job analysis, application memory, and application listing
  - Supports runtime context injection for JD path, profile path, tracker path, and retrieval mode
  - Produces structured tool traces for debugging and transparency

- **Reflection layer**
  - Uses an optional LangChain/Pydantic reflection step to verify final answers against tool observations

- **Streamlit frontend and CLI**
  - Provides both command-line and web UI workflows
  - Supports simple job analysis, application tracker, memory querying, profile management, and agent execution

## Agent Workflow and System Architecture

```text
Resume PDF / DOCX
        ↓
Resume Loader
        ↓
LLM Resume Parser
        ↓
Candidate Profile JSON
        ↓
Job Description / Pasted JD
        ↓
Rule-based or LLM JD Parser
        ↓
Hybrid Profile Matcher
        ↓
Match Report + Strengths / Gaps / Positioning
        ↓
Material Generator + Validator
        ↓
Application Tracker
        ↓
Application Memory / Chroma RAG
        ↓
ask_memory Tool
        ↓
Custom ReAct Agent
        ↓
Reflection Agent
        ↓
CLI / Streamlit UI
```

## Project Structure

```
job-application-agent/
├── README.md
├── docs/
│   └── workflow_design.md
├── data/
│      ├── resumes/
│      └── sample_resume.pdf
│   ├── sample_jd.txt
│   ├── applications.example.json
│   └── candidate_profile.example.json
├── outputs/
│   └── sample/
│      ├── cover_letter.md
│      ├── linkedin_message.md
│      ├── match_report.md
│      ├── match_result.json
│      └── parsed_jd.json
├── src/
│   ├── agents/
│      ├── application_memory_agent.py
│      ├── jd_parser.py
│      ├── material_generator.py
│      ├── profile_matcher.py
│      ├── react_agent.py
│      ├── reflection_agent.py
│      └── resume_parser.py
│   ├── prompts/
│      ├── application_memory_prompt.txt
│      ├── cover_letter_prompt.txt
│      ├── jd_parser_prompt.txt
│      ├── linkedin_message_prompt.txt
│      ├── lprofile_match_prompt.txt
│      ├── react_agent_prompt.txt
│      ├── reflection_prompt.txt
│      ├── resume_bullets_prompt.txt
│      └── resume_parser_prompt.txt
│   ├── schemas/
│      └── models.py
│   ├── tools/
│      ├── application_retriever.py
│      ├── application_tracker.py
│      ├── chroma_application_retriever.py
│      ├── embedding_application_retriever.py
│      ├── file_loader.py
│      ├── material_validator.py
│      ├── profile_manager.py
│      ├── react_tools.py
│      └── resume_loader.py
│   ├── ui/
│      └── streamlit_app.py
│   ├── utils/
│      ├── __init__.py
│      ├── embedding_client.py
│      └── llm_client.py
│   ├── workflows/
│      ├── application_memory_workflow.py
│      ├── job_analysis_workflow.py
│      ├── react_workflow.py
│      └── resume_profile_workflow.py
│   ├── cli.py
│   └── main.py
├── tests/
│   ├── test_chroma_retirever.py
│   ├── test_embedding_retirever.py
│   ├── test_llm_jd_parser.py
│   ├── test_react_agent.py
│   └── test_resume_parser.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── .dockerignore
└── docker-compose.yml
```

## Completed Features

The project now supports an end-to-end job application workflow:

- PDF/DOCX resume parsing into structured candidate profiles
- Rule-based and LLM-based job description parsing
- Hybrid profile matching with semantic evidence assessment
- Cover letter, LinkedIn message, and resume bullet generation
- Local application tracking
- Keyword, embedding, and Chroma-based application memory retrieval
- Custom ReAct agent for multi-step job analysis and comparison
- Optional LangChain/Pydantic reflection for final-answer verification
- Streamlit frontend and CLI interface
- Docker-based execution support

## Setup

- Local setup:

`pip install -r requirements.txt`

`python -m src.cli --help`

`python -m src.cli analyze --jd-path data/sample_jd.txt --profile-path data/candidate_profile.example.json`

- Docker setup:

`cp .env.example .env`

`docker compose build`

`docker compose run job-agent python -m src.cli --help`

`docker compose run job-agent python -m src.cli analyze --jd-path data/sample_jd.txt --profile-path data/candidate_profile.example.json`

## Sample Output

Please check `outputs/sample` directory.

## Streamlit Frontend Usage (Recommended)

Run the Streamlit app:

```bash
python -m streamlit run src/ui/streamlit_app.py
```

The UI supports:
- Pasting or loading job descriptions
- Uploading PDF/DOCX resumes and generating candidate profiles
- Selecting saved profiles for job analysis
- Viewing match score, strengths, gaps, and positioning summaries
- Tracking saved applications
- Querying application memory
- Running the ReAct agent with pasted JD input, saved profile selection, retrieval mode selection, and optional reflection

## CLI Usage

### Parse a resume into a candidate profile
- python -m src.cli parse-resume data/resumes/my_resume.pdf --output-profile-path data/profiles/my_profile.json

### Analyze a job
- python -m src.cli analyze --jd-path data/sample_jd.txt --profile-path data/profiles/my_profile.json --use-llm-jd-parser --use-llm-matcher

### Analyze and save an application
- python -m src.cli analyze --jd-path data/sample_jd.txt --profile-path data/profiles/my_profile.json --save-application

### Query application memory
- python -m src.cli ask-memory "Which previous applications are most relevant to AI agents?" --retrieval-mode chroma

### Run the ReAct agent
- python -m src.cli agent "Analyze the sample job, save it, search my application memory for similar applications, and recommend whether I should prioritize it." --max-steps 7

### Track applications
- python -m src.cli list-applications
- python -m src.cli update-status exampletech-ai-project-intern applied


## Example ReAct Workflow

A user can paste a new job description into the Streamlit Agent tab and ask:

```text
Analyze this new job using my resume-generated profile, save the application, search my application memory for similar past applications, and recommend whether I should prioritize it.
```

The ReAct agent can then:

Step 1: analyze_job
- Parse the pasted JD
- Match it against the selected candidate profile
- Generate a match score and strengths/gaps

Step 2: ask_memory
- Retrieve similar saved applications from application memory

Step 3: final_answer
- Compare the new role with previous applications
- Recommend whether the candidate should prioritize it

Optional Step 4: reflection
- Verify the final answer against structured tool observations

## Design Highlights

### Evidence-aware hybrid matching

The matcher combines exact/alias-based rule matching with LLM semantic assessment. The LLM matcher distinguishes between strong evidence, partial evidence, true gaps, and positioning improvements, making the fit evaluation more realistic than simple keyword overlap.

### Persistent application memory

Saved applications are used as a reusable memory base. The system supports keyword retrieval, embedding similarity, and Chroma vector search for comparing new roles against past opportunities.

### Chroma collection namespacing

Chroma collections are separated by embedding backend, model, and dimension to avoid vector-dimension conflicts between mock embeddings and real embedding models.

### Custom ReAct tool orchestration

The ReAct agent uses structured tool calls, runtime context, argument validation, and observation traces to plan multi-step workflows over job analysis and memory retrieval tools.

### Reflection-based verification

An optional LangChain/Pydantic reflection layer checks whether the final answer is supported by tool observations and whether requested subtasks were completed.

## Environment Variables

Please formulate your `.env` file according to the `.env.example` template and put it to the same directory as the `.env.example` file.

## Current Limitations


- Scanned or image-only resumes are not supported without OCR.
- LLM parsing and matching quality depends on the selected model and prompt quality.
- The application tracker currently uses local JSON storage rather than a production database.
- The system is intended for workflow assistance, not fully automated application submission.
- Some soft skills and ambiguous requirements may require manual review.
- API quota and rate limits may affect real-model testing.
- Total robustness and generalization need further tests.

## Future Work

- Add a database backend such as SQLite or PostgreSQL for persistent application tracking.
- Add richer duplicate detection across similar job postings.
- Add requirement-level matching tables with weighted scoring by core, supporting, soft, and nice-to-have requirements.
- Add OCR support for scanned resumes.
- Add automated evaluation tests for generated application materials and ReAct outputs.
- Add user authentication and deployment-ready configuration.
- Add more agent tools, such as editing tracker status, generating materials on demand, and retrieving detailed application records.
