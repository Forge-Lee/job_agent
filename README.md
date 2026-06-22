# AI Job Application Assistant Agent

## Overview

AI Job Application Assistant Agent is an LLM-powered workflow that helps candidates analyze job descriptions, evaluate role fit, generate tailored application materials, and track job applications.

The goal of this project is not only to generate application text, but to transform an unstructured job application process into a structured, traceable, and reusable agentic workflow.

## Motivation

Job applications often require repeatedly reading job descriptions, identifying key requirements, comparing them with personal experience, and writing customized materials. This project automates that workflow using a modular agent pipeline.

## Core Features

- Parse job descriptions into structured role information
- Extract required and preferred qualifications
- Match job requirements against a candidate profile
- Identify strengths, gaps, and positioning strategies
- Generate tailored application materials
- Save application records for future tracking

## Agent Workflow

text
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

## Project Structure

job-application-agent/
├── README.md
├── docs/
│   └── workflow_design.md
├── data/
│   ├── sample_jd.txt
│   └── candidate_profile.json
├── outputs/
├── src/
├── tests/
├── requirements.txt
├── Dockerfile
└── docker-compose.yml

## Current Status

This project is currently in the initial development stage. The first milestone is to build a command-line MVP that takes a job description and a candidate profile as input, then generates a structured job match report.

## Planned Output

The MVP will generate:

- `outputs/match_report.md`
- `outputs/cover_letter.md`
- `outputs/linkedin_message.md`
- `data/applications.json`

## How to Run

- Local Python Environment:

`pip install -r requirements.txt`

`python -m src.main`

- Docker:

`cp .env.example .env`

`docker compose up --build`

## Future Work

- Add structured LLM-based job description parsing
- Add profile-to-role matching logic
- Add application tracking with JSON or SQLite
- Add Streamlit UI
- Add RAG over past applications
- Add evaluation checks for generated materials

