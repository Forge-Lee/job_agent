# AI Job Application Assistant Agent

## Overview

AI Job Application Assistant Agent is an LLM-powered workflow that helps candidates analyze job descriptions, evaluate role fit, generate application materials, and track job applications.

The goal of this project is not only to generate application text, but to transform an unstructured job application process into a structured, traceable, and reusable agentic workflow.

## Motivation

Job applications often require repeatedly reading job descriptions, identifying key requirements, comparing them with personal experience, and writing customized materials. This project automates that workflow using a modular agent pipeline.

## Core Features

- Parse job descriptions into structured role information
- Match job requirements against a candidate profile and generate a report
- Identify strengths, gaps, and positioning strategies
- Generate LLM-based cover letter or LinkedIn follow-up message
- Save application records for future tracking
- CLI interface support
- Docker support

## Agent Workflow

```text
Job Description
      ↓
JD Parser
      ↓
Requirement Extractor
      ↓
Profile Matcher
      ↓
Gap Analyzer
      ↓
Material Generator
      ↓
Application Tracker 
```

## Project Structure

```
job-application-agent/
├── README.md
├── docs/
│   └── workflow_design.md
├── data/
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
│      ├── jd_parser.py
│      ├── material_generator.py
│      └── profile_matcher.py
│   ├── prompts/
│      ├── cover_letter_prompt.txt
│      └── linkedin_message_prompt.txt
│   ├── schemas/
│      └── models.py
│   ├── tools/
│      ├── application_tracker.py
│      └── file_loader.py
│   ├── utils/
│      ├── __init__.py
│      └── llm_client.py
│   ├── cli.py
│   └── main.py
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── .dockerignore
└── docker-compose.yml
```

## Current Status

The MVP workflow is complete. The project currently supports JD parsing, profile matching, material generation, local application tracking, CLI usage, and Docker-based execution. The next focus is improving robustness, scoring quality, and UI support.

## Planned Output

The MVP will generate:

- `outputs/match_report.md`
- `outputs/cover_letter.md`
- `outputs/linkedin_message.md`
- `data/applications.json`

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

## CLI Usage

- `python -m src.cli analyze --jd-path data/sample_jd.txt --profile-path data/candidate_profile.example.json`
- `python -m src.cli analyze --jd-path data/sample_jd.txt --profile-path data/candidate_profile.example.json --generate-cover-letter --generate-linkedin-message --use-mock-llm`
- `python -m src.cli analyze --jd-path data/sample_jd.txt --profile-path data/candidate_profile.example.json --save-application`
- `python -m src.cli list-applications`
- `python -m src.cli update-status exampletech-ai-project-intern applied`

## Environment Variables

Please formulate your `.env` file according to the `.env.example` template and put it to the same directory as the `.env.example` file.

## Current Limitations

- Rule-based parser/matcher
- LLM output depends on provider
- Tracker is JSON-based local storage

## Future Work

- Add structured LLM-based job description parsing
- Add SQLite-backed application tracking
- Add duplicate detection / upsert for application records
- Add Streamlit or FastAPI frontend
- Add RAG over past applications
- Add evaluation checks for generated materials
- Improve matching score calibration
