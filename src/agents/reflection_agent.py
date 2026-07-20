from pydantic import BaseModel, Field
from pathlib import Path
import json

def parse_llm_json_response(response: str) -> dict:
    cleaned = response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()

    if cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-len("```")].strip()

    return json.loads(cleaned)

class ReflectionResult(BaseModel):
    passed: bool = Field(
        description="Whether the final answer is fully supported by observations and completes the user request."
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Problems found in the draft final answer."
    )
    revised_answer: str = Field(
        description="A corrected final answer. If passed is true, this can be the original answer."
    )

class ReflectionAgent:
    def __init__(
        self,
        llm_client=None,
        use_langchain: bool = True,
        model_name: str = "gpt-4o-mini",
        provider: str = "gemini"
    ):
        self.llm_client = llm_client
        self.use_langchain = use_langchain
        self.model_name = model_name
        self.provider = provider

    def _reflect_with_existing_client(
            self,
            user_request: str, 
            final_answer: str,
            observations: list[dict],
            completed_actions: list[str],
        ):
        prompt = self._build_prompt(
            user_request,
            final_answer,
            observations,
            completed_actions
        )

        response = self.llm_client.generate_text(prompt)
        parsed = parse_llm_json_response(response)

        return ReflectionResult(**parsed)

    def _build_prompt(
            self, 
            user_request: str, 
            final_answer: str,
            observations: list[dict],
            completed_actions: list[str],
        ):
        template = Path("src/prompts/reflection_prompt.txt").read_text(encoding="utf-8")
        return template.format(
            user_request=user_request,
            final_answer=final_answer,
            observations=json.dumps(observations, indent=2, default=str),
            completed_actions=json.dumps(completed_actions, indent=2),
        )

    def reflect(
        self,
        user_request: str,
        final_answer: str,
        observations: list[dict],
        completed_actions: list[str],
    ) -> ReflectionResult:
        prompt = self._build_prompt(
            user_request,
            final_answer,
            observations,
            completed_actions
        )

        if self.use_langchain:
            if self.provider == "openai":
                from langchain_openai import ChatOpenAI
                model = ChatOpenAI(model=self.model_name, temperature=0)

            elif self.provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                model = ChatGoogleGenerativeAI(model=self.model_name, temperature=0)
            
            else:
                raise ValueError(f"Unsupported LangChain provider: {self.provider}")

            structured_model = model.with_structured_output(ReflectionResult)
            return structured_model.invoke(prompt)

        else:
            # use existing llm to respond
            result = self._reflect_with_existing_client(
                user_request,
                final_answer,
                observations,
                completed_actions
            )
            return result