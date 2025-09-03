from tools.search_tools import compare_with_market

class ComparisonAgent:
    def execute(self, state):
        query = state["messages"][-1].content
        result = compare_with_market(query)
        return {"messages": [("comparison", result)]}
