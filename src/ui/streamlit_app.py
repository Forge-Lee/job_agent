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
    use_llm_matcher = st.checkbox("Use LLM-based semantic matching", value=False)

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
                    use_llm_matcher=use_llm_matcher,
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