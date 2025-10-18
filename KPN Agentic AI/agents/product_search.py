"""Agent that surfaces KPN catalogue matches for the captured intent."""

from __future__ import annotations

from copy import deepcopy
from typing import Dict

from agents.utils import intent_to_search_query
from tools.search_tools import search_kpn_products


class ProductSearchAgent:
    def execute(self, state: Dict) -> Dict:
        intent = state.get("intent", {})
        query = intent_to_search_query(intent)
        rag_response = search_kpn_products(query)

        summary_lines = ["📱 KPN product suggestions:"]
        if rag_response["items"]:
            for item in rag_response["items"]:
                line = f"- {item['product_name']} ({item['brand']}) – €{item['price']}"
                if item.get("features"):
                    line += f" | Features: {', '.join(item['features'][:3])}"
                summary_lines.append(line)
        else:
            summary_lines.append("No matching devices were found in the KPN catalogue.")

        message = "\n".join(summary_lines)

        results = deepcopy(state.get("results", {}))
        results["product_search"] = {
            "query": query,
            "matches": rag_response["items"],
        }

        return {
            "messages": [("product_search", message)],
            "results": results,
            "current_task": state.get("current_task", 0) + 1,
        }
