import json
from pathlib import Path

from src.tools.react_tools import TOOL_REGISTRY
from src.agents.jd_parser import parse_llm_json_response
from src.tools.react_tools import ToolExecutor

class ReActAgent:
    def __init__(self, llm_client, max_steps: int = 3, runtime_context: dict | None = None,):
        self.llm_client = llm_client
        self.max_steps = max_steps
        self.runtime_context = runtime_context or {}
        self.tool_executor = ToolExecutor(self.runtime_context)
        self.tool_registry = self.tool_executor.get_tool_registry()

    def _format_observations(self, observations: list[dict]) -> str:
        if not observations:
            return "No previous observations."

        lines = []
        for i, obs in enumerate(observations, start=1):
            lines.append(f"Step {i}:")
            lines.append(json.dumps(obs, indent=2, default=str))
        return "\n".join(lines)

    def _build_prompt(self, user_request: str, observations: list[dict]) -> str:
        prompt_template = Path("src/prompts/react_agent_prompt.txt").read_text(
            encoding="utf-8"
        )

        return prompt_template.format(
            user_request=user_request,
            observations=self._format_observations(observations),
            default_jd_path=self.runtime_context.get("default_jd_path", "data/sample_jd.txt"),
            default_profile_path=self.runtime_context.get("default_profile_path", "data/candidate_profile.example.json"),
            default_tracker_path=self.runtime_context.get("default_tracker_path", "data/applications.json"),
            default_retrieval_mode=self.runtime_context.get("default_retrieval_mode", "chroma"),
        )

    def run(self, user_request: str) -> dict:
        observations = []

        for step in range(self.max_steps):
            prompt = self._build_prompt(user_request, observations)
            response = self.llm_client.generate_text(prompt)

            try:
                decision = parse_llm_json_response(response)
            except Exception as e:
                return {
                    "final_answer": "The agent failed to parse the LLM decision.",
                    "error": str(e),
                    "raw_response": response,
                    "observations": observations,
                }

            if "final_answer" in decision:
                return {
                    "final_answer": decision["final_answer"],
                    "observations": observations,
                    "steps_used": step + 1,
                }

            action = decision.get("action")
            action_input = decision.get("action_input", {})

            if action not in self.tool_registry:
                return {
                    "final_answer": f"Unknown tool requested: {action}",
                    "observations": observations,
                    "steps_used": step + 1,
                }

            tool_fn = self.tool_registry[action]

            try:
                tool_result = tool_fn(action_input)
            except Exception as e:
                tool_result = {
                    "error": str(e)
                }

            observations.append({
                "thought": decision.get("thought", ""),
                "action": action,
                "action_input": action_input,
                "observation": self._summarize_tool_result(tool_result),
            })

        return {
            "final_answer": "Reached the maximum number of reasoning steps before producing a final answer.",
            "observations": observations,
            "steps_used": self.max_steps,
        }

    def _summarize_tool_result(self, tool_result: dict) -> dict:
        """
        Keep observations compact so the next LLM step is not overloaded.
        """
        if "match_result" in tool_result:
            match_result = tool_result["match_result"]
            parsed_jd = tool_result["parsed_jd"]

            return {
                "application_id": tool_result.get("application_id"),
                "company": parsed_jd.company,
                "role": parsed_jd.role,
                "match_score": match_result.match_score,
                "strengths": match_result.strengths[:3],
                "gaps": match_result.gaps[:3],
            }

        if "answer" in tool_result:
            return {
                "answer": tool_result.get("answer"),
                "retrieved_results": tool_result.get("retrieved_results", [])[:3],
            }

        if "applications" in tool_result:
            return {
                "applications": tool_result.get("applications", [])[:5],
            }

        return tool_result