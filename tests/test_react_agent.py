from src.workflows.react_workflow import run_react_workflow

# result = run_react_workflow(
#     user_request=(
#         "Analyze the sample job using the default candidate profile, "
#         "save the application, then summarize whether it is a strong fit."
#     ),
#     use_mock_llm=False,
#     max_steps=4,
#     default_jd_path="data/sample_jd.txt",
#     default_profile_path="data/candidate_profile.example.json",
#     default_tracker_path="data/applications.json",
# )

result = run_react_workflow(
    user_request=(
        "Analyze the sample job using the default candidate profile, "
        "save the application, then search my application memory for similar past applications, "
        "and compare whether this one is stronger or weaker."
    ),
    use_mock_llm=False,
    max_steps=5,
    default_jd_path="data/sample_jd.txt",
    default_profile_path="data/candidate_profile.example.json",
    default_tracker_path="data/applications.json",
)

print(result["final_answer"])
print(result["observations"])