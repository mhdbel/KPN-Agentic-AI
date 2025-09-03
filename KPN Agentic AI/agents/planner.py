from config import llm
from langchain.prompts import PromptTemplate

class PlannerAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["intent"],
            template=(
                "You are the Planner Agent. Based on the user's intent, decide which tasks are needed.\n"
                "Possible tasks:\n"
                " - product_search (search KPN phones)\n"
                " - comparison (compare KPN vs external market)\n"
                " - deal_advisor (check KPN exclusive deals)\n\n"
                "User intent:\n{intent}\n\n"
                "Return a JSON list of tasks in the order they should run. "
                "Example: [\"product_search\", \"comparison\"]"
            )
        )

    def execute(self, state):
        intent = state.get("intent", {})
        chain = self.prompt | llm
        response = chain.invoke({"intent": str(intent)}).content.strip()

        # Parse tasks safely
        try:
            tasks = eval(response) if response.startswith("[") else ["product_search"]
        except Exception:
            tasks = ["product_search"]

        return {"tasks": tasks}
