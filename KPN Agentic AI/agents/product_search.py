from config import llm
from langchain.prompts import PromptTemplate

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
        chain = self.prompt | llm
        response = chain.invoke({"intent": str(intent)}).content.strip()

        # Save structured output
        results = state.get("results", {})
        results["product_search"] = response

        return {"messages": [("product_search", response)], "results": results}
