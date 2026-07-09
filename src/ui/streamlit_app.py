import streamlit as st
import pandas as pd

from src.workflows.job_analysis_workflow import run_job_analysis
from src.workflows.application_memory_workflow import run_application_memory_query
from src.tools.application_tracker import ApplicationTracker

st.set_page_config(
    page_title="AI Job Application Assistant",
    layout="wide",
)

st.title("AI Job Application Assistant")
st.caption("JD analysis, application tracking, and RAG-based application memory.")

tab_analysis, tab_tracker, tab_memory = st.tabs([
    "Job Analysis",
    "Application Tracker",
    "Application Memory",
])

with tab_analysis:
    st.header("Job Analysis")

    jd_path = st.text_input(
        "Job description path",
        value="data/sample_jd.txt",
    )

    profile_path = st.text_input(
        "Candidate profile path",
        value="data/candidate_profile.example.json",
    )

    use_mock_llm = st.checkbox("Use mock LLM", value=True)
    generate_cover_letter = st.checkbox("Generate cover letter", value=False)
    generate_linkedin_message = st.checkbox("Generate LinkedIn message", value=False)
    generate_resume_bullets = st.checkbox("Generate resume bullets", value=False)
    save_application = st.checkbox("Save application", value=False)

    if st.button("Analyze Job"):
        try:
            with st.spinner("Analyzing job..."):
                result = run_job_analysis(
                    jd_path=jd_path,
                    profile_path=profile_path,
                    use_mock_llm=use_mock_llm,
                    generate_cover_letter=generate_cover_letter,
                    generate_linkedin_message=generate_linkedin_message,
                    generate_resume_bullets=generate_resume_bullets,
                    save_application=save_application,
                    verbose=False,
                )

            st.success("Job analysis completed.")

            st.subheader("Summary")
            st.write("Application ID:", result["application_id"])
            st.write("Match Report:", result["match_report_path"])

            parsed_jd = result["parsed_jd"]
            match_result = result["match_result"]

            st.metric("Match Score", match_result.match_score)

            st.write("Company:", parsed_jd.company)
            st.write("Role:", parsed_jd.role)
            st.write("Employment Type:", parsed_jd.employment_type)
            st.write("Location:", parsed_jd.location)

            st.subheader("Strengths")
            st.write(match_result.strengths)

            st.subheader("Gaps")
            st.write(match_result.gaps)

            st.subheader("Positioning Summary")
            st.write(match_result.positioning_summary)

        except Exception as e:
            st.error("Job analysis failed.")
            st.exception(e)

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

    if st.button("Ask Memory"):
        try:
            with st.spinner("Querying application memory..."):
                result = run_application_memory_query(
                    query=memory_query,
                    top_k=top_k,
                    use_mock_llm=use_mock_memory_llm,
                    app_tracker_path=app_tracker_path,
                    verbose=False,
                )

            st.subheader("Answer")
            st.write(result["answer"])

            st.subheader("Retrieved Applications")
            retrieved_results = result["retrieved_results"]

            if retrieved_results:
                st.dataframe(pd.DataFrame(retrieved_results), use_container_width=True)
            else:
                st.info("No relevant applications found.")

        except Exception as e:
            st.error("Application memory query failed.")
            st.exception(e)