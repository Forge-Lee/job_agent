import os
from dotenv import load_dotenv
import time
import json
from openai import OpenAI, InternalServerError, RateLimitError, APIConnectionError

class MockLLMClient:
    def generate_text(self, prompt: str) -> str:
        if "AI career matching evaluator" in prompt or "llm_score" in prompt:
            return json.dumps({
                "llm_score": 0.76,
                "llm_strengths": [
                    "The candidate shows relevant project-based evidence for the target role."
                ],
                "llm_gaps": [
                    "Some requirements have limited direct evidence in the profile."
                ],
                "llm_reasoning_summary": "The candidate appears to be a strong adjacent fit based on skills, tools, and project experience."
            })
        
        if "You are a ReAct-style job application assistant agent" in prompt:
            if "No previous observations" in prompt:
                return """
        {
        "thought": "The user wants to analyze the default sample job first.",
        "action": "analyze_job",
        "action_input": {
            "jd_path": "data/sample_jd.txt",
            "profile_path": "data/candidate_profile.example.json",
            "use_mock_llm": true,
            "use_llm_jd_parser": false,
            "use_llm_matcher": false,
            "generate_cover_letter": false,
            "generate_linkedin_message": false,
            "generate_resume_bullets": false,
            "save_application": true
        }
        }
        """
            else:
                return """
        {
        "thought": "The job has been analyzed, so I can now provide the final answer.",
        "final_answer": "The sample job has been analyzed and saved. Based on the match result, it appears to be a relevant fit. Review the generated match report for details."
        }
        """
            
        return "This is a mock LLM response generated from the provided prompt."


class OpenAIClient:
    def __init__(self) -> None:
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("BASE_URL")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Please set it in your .env file.")
        if not base_url:
            raise ValueError("BASE_URL is missing. Please set it in your .env file.")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = os.getenv("MODEL_NAME", "gpt-4o-mini")

    def generate_text(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You write grounded job application materials. "
                                "Only use the provided job information, candidate profile, "
                                "and match result. Do not fabricate experiences, skills, "
                                "projects, employers, publications, or years of experience."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=0.4,
                )

                content = response.choices[0].message.content
                return content.strip() if content else ""

            except (InternalServerError, RateLimitError, APIConnectionError) as error:
                wait_time = 20

                if attempt == max_retries - 1:
                    raise error

                print(f"LLM API request failed: {error}")
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)