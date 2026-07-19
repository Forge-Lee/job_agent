from pydantic import BaseModel, Field
from pathlib import Path
import json
from langchain_openai import ChatOpenAI

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
    ):
        self.llm_client = llm_client
        self.use_langchain = use_langchain
        self.model_name = model_name

    def _reflect_with_existing_client(...):
        prompt = self._build_prompt(...)

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
        prompt = self._build_prompt(...)

        if self.use_langchain:
            model = ChatOpenAI(model=self.model_name, temperature=0)
            structured_model = model.with_structured_output(ReflectionResult)
            return structured_model.invoke(prompt)

        ...