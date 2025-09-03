from config import llm
from langchain.prompts import PromptTemplate

class CustomerIntentAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["query", "current_intent"],
            template=(
                "You are an assistant that extracts customer intent from queries.\n"
                "User query: {query}\n"
                "Current known intent: {current_intent}\n\n"
                "Extract and update preferences in JSON with keys:\n"
                "- budget (if mentioned)\n"
                "- brand (if mentioned)\n"
                "- features (list of features if mentioned)\n\n"
                "If nothing is specified, keep the current intent unchanged.\n"
                "Return only valid JSON."
            )
        )

    def execute(self, state):
        user_query = state["messages"][-1].content
        current_intent = state.get("intent", {"budget": None, "brand": None, "features": []})

        chain = self.prompt | llm
        response = chain.invoke({"query": user_query, "current_intent": str(current_intent)}).content.strip()

        try:
            import json
            new_intent = json.loads(response)
        except Exception:
            new_intent = current_intent  # fallback if parsing fails

        return {
            "messages": [("intent_agent", f"Updated intent: {new_intent}")],
            "intent": new_intent
        }
