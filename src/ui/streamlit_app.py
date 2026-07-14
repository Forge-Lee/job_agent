import streamlit as st
import pandas as pd
from pathlib import Path

from src.workflows.job_analysis_workflow import run_job_analysis
from src.workflows.application_memory_workflow import run_application_memory_query
from src.tools.application_tracker import ApplicationTracker
from src.tools.profile_manager import parse_comma_list, save_user_profile, list_saved_profiles

st.set_page_config(
    page_title="AI Job Application Assistant",
    layout="wide",
)

st.title("AI Job Application Assistant")
st.caption("JD analysis, application tracking, and RAG-based application memory.")

tab_analysis, tab_tracker, tab_memory, tab_profile = st.tabs([
    "Job Analysis",
    "Application Tracker",
    "Application Memory",
    "User Profile"
])

with tab_analysis:
    st.header("Job Analysis")

    jd_input_mode = st.radio(
        "Job description input mode",
        ["Use local path", "Paste JD text"],
    )

    if jd_input_mode == "Paste JD text":
        jd_text = st.text_area(
            "Paste job description",
            height=300,
            placeholder="Paste the full job description here...",
        )

        if jd_text.strip():
            upload_dir = Path("data/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)

            jd_path = upload_dir / "pasted_jd.txt"
            jd_path.write_text(jd_text, encoding="utf-8")

            jd_path = str(jd_path)
        else:
            jd_path = None
    else:
        jd_path = st.text_input(
            "Job description path",
            value="data/sample_jd.txt",
        )

    profile_input_mode = st.radio(
        "Candidate profile input mode",
        ["Use saved profile", "Use local path"],
    )

    if profile_input_mode == "Use saved profile":
        saved_profiles = list_saved_profiles()

        if saved_profiles:
            profile_path = st.selectbox(
                "Select saved profile",
                saved_profiles,
            )
        else:
            st.warning("No saved profiles found. Please create one in the User Profile tab.")
            profile_path = "data/candidate_profile.example.json"
    else:
        profile_path = st.text_input(
            "Candidate profile path",
            value="data/candidate_profile.example.json",
        )

    use_mock_llm = st.checkbox("Use mock LLM", value=True)
    generate_cover_letter = st.checkbox("Generate cover letter", value=False)
    generate_linkedin_message = st.checkbox("Generate LinkedIn message", value=False)
    generate_resume_bullets = st.checkbox("Generate resume bullets", value=False)
    save_application = st.checkbox("Save application", value=False)
    use_llm_matcher = st.checkbox("Use LLM-based semantic matching", value=False)
    use_llm_jd_parser = st.checkbox("Use LLM-based JD parsing", value=False,)
    if st.button("Clear Job Analysis Result"):
        st.session_state.pop("job_analysis_result", None)
        st.success("Cleared previous job analysis result.")

    if st.button("Analyze Job"):
        try:
            if not jd_path:
                st.error("Please provide a job description before analyzing.")
            else:
                with st.spinner("Analyzing job..."):
                    result = run_job_analysis(
                        jd_path=jd_path,
                        profile_path=profile_path,
                        use_mock_llm=use_mock_llm,
                        generate_cover_letter=generate_cover_letter,
                        generate_linkedin_message=generate_linkedin_message,
                        generate_resume_bullets=generate_resume_bullets,
                        save_application=save_application,
                        use_llm_matcher=use_llm_matcher,
                        use_llm_jd_parser=use_llm_jd_parser,
                        verbose=False,
                    )

                st.session_state["job_analysis_result"] = result

                st.success("Job analysis completed.")

        except Exception as e:
            st.error("Job analysis failed.")
            st.exception(e)
        
    if "job_analysis_result" in st.session_state:
        result = st.session_state["job_analysis_result"]

        parsed_jd = result["parsed_jd"]
        match_result = result["match_result"]

        st.subheader("Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Match Score", match_result.match_score)

        with col2:
            st.metric("Required Skills Matched", len(match_result.matched_required_skills))

        with col3:
            st.metric("Missing Required Skills", len(match_result.missing_required_skills))

        st.markdown(f"**Company:** {parsed_jd.company}")
        st.markdown(f"**Role:** {parsed_jd.role}")
        st.markdown(f"**Employment Type:** {parsed_jd.employment_type}")
        st.markdown(f"**Location:** {parsed_jd.location}")

        st.subheader("Strengths")
        for strength in match_result.strengths:
            st.markdown(f"- {strength}")

        st.subheader("Gaps")
        for gap in match_result.gaps:
            st.markdown(f"- {gap}")

        st.subheader("Positioning Summary")
        st.write(match_result.positioning_summary)

        with st.expander("Output Files"):
            match_report_path = result["match_report_path"]
            cover_letter_path = result["cover_letter_path"]
            linkedin_message_path = result["linkedin_message_path"]
            resume_bullets_path = result["resume_bullets_path"]
            if match_report_path is not None:
                st.write(f"Match report is stored in {match_report_path}.")
            else:
                st.write("Match report is not generated.")
                
            if cover_letter_path is not None:
                st.write(f"Cover letter is stored in {cover_letter_path}.")
            else:
                st.write("Cover letter is not generated.")

            if linkedin_message_path is not None:
                st.write(f"LinkedIn follow-up message is stored in {linkedin_message_path}.")
            else:
                st.write("LinkedIn follow-up message is not generated.")

            if resume_bullets_path is not None:
                st.write(f"Recommended resume bullets are stored in {resume_bullets_path}.")
            else:
                st.write("Recommended resume bullets is not generated.")

with tab_tracker:
    st.header("Application Tracker")

    app_tracker_path = st.text_input(
        "Application tracker path",
        value="data/applications.json",
    )

    if st.button("Load Applications"):
        tracker = ApplicationTracker(app_tracker_path)
        applications = tracker.list_applications()

        if not applications:
            st.info("No applications found.")
        else:
            df = pd.DataFrame(applications)
            st.dataframe(df, use_container_width=True)

with tab_memory:
    st.header("Application Memory")

    memory_query = st.text_input(
        "Ask a question over past applications",
        value="Which previous applications are most relevant to computer vision?",
    )

    top_k = st.number_input(
        "Top K",
        min_value=1,
        max_value=10,
        value=3,
    )

    use_mock_memory_llm = st.checkbox("Use mock LLM for memory answer", value=True)

    retrieval_mode = st.selectbox(
        "Retrieval mode",
        ["keyword", "embedding"],
    )

    use_mock_embedding = st.checkbox(
        "Use mock embedding client",
        value=True,
    )

    if st.button("Ask Memory"):
        try:
            with st.spinner("Querying application memory..."):
                result = run_application_memory_query(
                    query=memory_query,
                    top_k=top_k,
                    use_mock_llm=use_mock_memory_llm,
                    app_tracker_path=app_tracker_path,
                    retrieval_mode=retrieval_mode,
                    use_mock_embedding=use_mock_embedding,
                    verbose=False,
                )
            
            st.session_state["memory_result"] = result

        except Exception as e:
            st.error("Application memory query failed.")
            st.exception(e)

    if "memory_result" in st.session_state:
        result = st.session_state["memory_result"]
        st.subheader("Answer")
        st.write(result["answer"])

        st.subheader("Retrieved Applications")
        retrieved_results = result["retrieved_results"]

        if retrieved_results:
            st.dataframe(pd.DataFrame(retrieved_results), use_container_width=True)
        else:
            st.info("No relevant applications found.")



with tab_profile:
    st.header("User Profile")

    if "profile_projects" not in st.session_state:
        st.session_state["profile_projects"] = [
            {
                "name": "AI Job Application Assistant",
                "description": "Built an AI-powered job application assistant with JD parsing, hybrid profile matching, LLM material generation, application tracking, and embedding-based RAG memory.",
                "keywords": "LLM, RAG, Streamlit, Python, OpenAI, agentic workflow",
            }
        ]

    if "profile_education" not in st.session_state:
        st.session_state["profile_education"] = [
            {
                "school": "Example University",
                "degree": "M.S. in Example Engineering",
                "details": "Graduate student focusing on machine learning, computer vision, and AI systems.",
            }
        ]

    profile_name = st.text_input("Profile name", value="default_profile")

    st.subheader("Education")

    if st.button("Add Education"):
        st.session_state["profile_education"].append({
            "degree": "",
            "school": "",
            "focus": "",
        })

    for i, edu in enumerate(st.session_state["profile_education"]):
        with st.expander(f"Education #{i + 1}", expanded=True):
            edu["degree"] = st.text_input(
                "Degree",
                value=edu.get("degree", ""),
                key=f"edu_degree_{i}",
            )

            edu["school"] = st.text_input(
                "School",
                value=edu.get("school", ""),
                key=f"edu_school_{i}",
            )

            edu["focus"] = st.text_input(
                "Focus areas",
                value=edu.get("focus", ""),
                key=f"edu_focus_{i}",
                help="Comma-separated, e.g. Machine Learning, Computer Vision, Robotics",
            )

    st.subheader("Skills")

    programming = st.text_input(
        "Programming languages",
        value="Python, C++",
    )

    ml_skills = st.text_input(
        "ML / AI skills",
        value="Machine Learning, Deep Learning, Computer Vision, LLM, Robotics",
    )

    tools = st.text_input(
        "Tools",
        value="PyTorch, OpenCV, Streamlit, FastAPI, Git, Docker",
    )

    domains = st.text_input(
        "Domains",
        value="Computer Vision, AI Agents, Robotics",
    )

    others = st.text_input(
        "Other skills you hope to provide",
        value="N/A"
    )

    st.subheader("Projects")


    if st.button("Add Project"):
        st.session_state["profile_projects"].append({
            "name": "",
            "description": "",
            "keywords": "",
        })

    for i, project in enumerate(st.session_state["profile_projects"]):
        with st.expander(f"Project #{i + 1}", expanded=True):
            project["name"] = st.text_input(
                "Project name",
                value=project.get("name", ""),
                key=f"project_name_{i}",
            )

            project["description"] = st.text_area(
                "Project description",
                value=project.get("description", ""),
                key=f"project_description_{i}",
            )

            project["keywords"] = st.text_input(
                "Project keywords",
                value=project.get("keywords", ""),
                key=f"project_keywords_{i}",
            )

    if st.button("Save Profile"):
        education_records = []

        for edu in st.session_state["profile_education"]:
            degree = edu.get("degree", "").strip()
            school = edu.get("school", "").strip()
            focus = parse_comma_list(edu.get("focus", ""))

            if degree or school:
                education_item = {
                    "degree": degree,
                    "school": school,
                }

                if focus:
                    education_item["focus"] = focus

                education_records.append(education_item)

        projects = []

        for project in st.session_state["profile_projects"]:
            if project.get("name", "").strip():
                projects.append({
                    "name": project.get("name", "").strip(),
                    "description": project.get("description", "").strip(),
                    "keywords": parse_comma_list(project.get("keywords", "")),
                })

        profile = {
            "education": education_records,
            "skills": {
                "programming": parse_comma_list(programming),
                "machine_learning": parse_comma_list(ml_skills),
                "tools": parse_comma_list(tools),
                "domains": parse_comma_list(domains),
                "other": parse_comma_list(others),
            },
            "projects": projects,
        }

        profile_path = save_user_profile(profile_name, profile)
        st.success(f"Profile saved to {profile_path}")
        st.json(profile)