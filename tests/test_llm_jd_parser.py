from src.agents.jd_parser import JDParser
from src.utils.llm_client import MockLLMClient, OpenAIClient

jd_text = open("data/sample_jd.txt", encoding="utf-8").read()

rule_parser = JDParser()
rule_result = rule_parser.parse(jd_text, use_llm_parser=False)

llm_parser = JDParser(llm_client=OpenAIClient())
llm_result = llm_parser.parse(jd_text, use_llm_parser=True)

print("===== Rule-based Parsed JD =====")
print(rule_result.model_dump_json(indent=2))

print("===== LLM-based Parsed JD =====")
print(llm_result.model_dump_json(indent=2))