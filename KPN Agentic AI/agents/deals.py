from tools.search_tools import check_kpn_exclusive_deals

class DealAdvisorAgent:
    def execute(self, state):
        query = state["messages"][-1].content
        result = check_kpn_exclusive_deals(query)
        return {"messages": [("deal_advisor", result)]}
