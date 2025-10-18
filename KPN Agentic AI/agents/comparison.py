from copy import deepcopy

from agents.utils import get_latest_user_message, intent_to_search_query
from tools.search_tools import compare_with_market

class ComparisonAgent:
    def execute(self, state):
        user_query = get_latest_user_message(state)
        intent_query = intent_to_search_query(state.get("intent", {}), fallback=user_query or "KPN phones")
        result = compare_with_market(intent_query)

        results = deepcopy(state.get("results", {}))
        results["comparison"] = {
            "query": intent_query,
            "kpn_products": result.get("kpn_products", []),
            "external_products": result.get("external_products", []),
            "insight": result.get("insight", ""),
        }

        return {
            "messages": [("comparison", result.get("text", ""))],
            "results": results,
            "current_task": state.get("current_task", 0) + 1,
        }
