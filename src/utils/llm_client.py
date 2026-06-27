import os
from dotenv import load_dotenv
from openai import OpenAI

class MockLLMClient:
    def generate_text(self, prompt: str) -> str:
        return """# Cover Letter Draft

Dear Hiring Team,

I am excited to apply for this role. Based on the structured job analysis and candidate profile, this position aligns with my background in machine learning, computer vision, and applied AI workflows.

My experience with Python, PyTorch, OpenCV, and machine learning projects provides a strong foundation for contributing to the responsibilities described in the role. I am especially interested in opportunities involving computer vision, document understanding, and practical AI-powered workflows.

Thank you for your consideration.

Sincerely,
Candidate
"""


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
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.35,
        )

        return response.choices[0].message.content or ""