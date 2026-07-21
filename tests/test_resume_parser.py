from src.agents.resume_parser import normalize_profile

# profile normalization test

messy = {
    "education": [
        {"school": " UCSD ", "degree": "M.S. ECE"},
        {}
    ],
    "skills": {
        "programming": "Python, C++, ",
        "tools": [" PyTorch ", "", None, "OpenCV"]
    },
    "projects": {
        "name": "AI Job Agent",
        "description": "Built a ReAct-style assistant.",
        "keywords": ["LLM", "RAG", "ReAct"]
    }
}
print(normalize_profile(messy))