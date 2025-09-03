from config import llm
from langchain.prompts import PromptTemplate

class SummaryAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["results", "tasks"],
            template=(
                "You are the Summary Agent. You receive structured results from other agents.\n\n"
                "Tasks executed: {tasks}\n"
                "Results:\n{results}\n\n"
                "Format the final output into clear sections:\n"
                "- 📱 Search Results (if product_search present)\n"
                "- 📊 Comparison (if comparison present)\n"
                "- 🌟 Exclusive Deals (if deal_advisor present)\n"
                "- 💡 Final Recommendation (always include)\n\n"
                "Only summarize the results clearly — no raw JSON."
            )
        )

    def execute(self, state):
        tasks = ", ".join(state.get("tasks", []))
        results = state.get("results", {})

        chain = self.prompt | llm
        summary = chain.invoke({
            "results": str(results),
            "tasks": tasks
        }).content.strip()

        return {"messages": [("summary", summary)]}
