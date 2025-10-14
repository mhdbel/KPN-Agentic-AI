from copy import deepcopy

from agents.utils import get_latest_user_message, intent_to_search_query
from tools.search_tools import check_kpn_exclusive_deals

class DealAdvisorAgent:
    def execute(self, state):
        user_query = get_latest_user_message(state)
        intent_query = intent_to_search_query(state.get("intent", {}), fallback=user_query or "KPN phones")
        result = check_kpn_exclusive_deals(intent_query)

        results = deepcopy(state.get("results", {}))
        results["deal_advisor"] = {
            "query": intent_query,
            "deals": result.get("items", []),
        }

        return {
            "messages": [("deal_advisor", result.get("text", ""))],
            "results": results,
            "current_task": state.get("current_task", 0) + 1,
        }
