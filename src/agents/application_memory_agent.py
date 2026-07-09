from pathlib import Path

class ApplicationMemoryAgent():
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def format_retrieved_context(self, retrieved_results):
        counter = 1
        formulated_text = ''
        for apps in retrieved_results:
            formulate_header = f"Retrieved Application {counter}\n"
            id_line = f"Application ID: {apps['application_id']}\n"
            company_line = f"Company: {apps['company']}\n"
            role_line = f"Role: {apps['role']}\n"
            status_line = f"Status: {apps['status']}\n"
            match_score_line = f"Match Score: {apps['match_score']}\n"
            retrieval_score_line = f"Retrieval Score: {apps['retrieval_score']}\n"
            retrieved_text_line = f"Relevant Context:\n{apps.get('retrieved_text', '')}\n"
            formulated_text += formulate_header + id_line + company_line + role_line + status_line + match_score_line + retrieval_score_line + retrieved_text_line + '---\n\n'
            counter += 1
        
        return formulated_text

    def ask(self, query, retrieved_results):
        if len(retrieved_results) == 0:
            return "No relevant application records were found for this query."
        if self.llm_client is None:
            raise ValueError("LLM client is required for application memory agent.")
        
        retrieved_context = self.format_retrieved_context(retrieved_results)
        prompt_template = Path("src/prompts/application_memory_prompt.txt").read_text(
            encoding="utf-8"
        )

        prompt = prompt_template.format(
            query = query,
            retrieved_context = retrieved_context
        )
        
        return self.llm_client.generate_text(prompt)
