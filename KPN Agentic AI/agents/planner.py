import json

from config import llm
from langchain.prompts import PromptTemplate


VALID_TASKS = {"product_search", "comparison", "deal_advisor"}

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

        tasks = self._parse_tasks(response)
        previous_tasks = state.get("tasks", [])
        current_index = state.get("current_task", 0)

        if tasks != previous_tasks:
            current_index = 0
        elif current_index >= len(tasks):
            current_index = len(tasks)

        return {"tasks": tasks, "current_task": current_index}

    def _parse_tasks(self, llm_response: str) -> list:
        """Parse the planner output and validate against supported tasks."""

        try:
            candidate = json.loads(llm_response)
        except json.JSONDecodeError:
            candidate = None

        if not isinstance(candidate, list):
            candidate = ["product_search"]

        cleaned = []
        for task in candidate:
            if isinstance(task, str):
                task_name = task.strip()
                if task_name in VALID_TASKS and task_name not in cleaned:
                    cleaned.append(task_name)

        if not cleaned:
            cleaned = ["product_search"]

        return cleaned
