from copy import deepcopy

from config import llm
from langchain.prompts import PromptTemplate

from agents.utils import intent_to_search_query
from tools.search_tools import search_kpn_products

class ProductSearchAgent:
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=["intent"],
            template=(
                "You are the Product Search Agent. "
                "Search KPN’s phone catalog based on the user’s intent:\n{intent}\n\n"
                "Return the best matches with name, price, and key features."
            )
        )

    def execute(self, state):
        intent = state.get("intent", {})
        query = intent_to_search_query(intent)
        rag_response = search_kpn_products(query)

        chain = self.prompt | llm
        response = chain.invoke({"intent": str(intent)}).content.strip()

        message = f"{rag_response['text']}\n\n🤖 Reasoning summary:\n{response}"

        results = deepcopy(state.get("results", {}))
        results["product_search"] = {
            "query": query,
            "matches": rag_response["items"],
            "analysis": response,
        }

        return {
            "messages": [("product_search", message)],
            "results": results,
            "current_task": state.get("current_task", 0) + 1,
        }
