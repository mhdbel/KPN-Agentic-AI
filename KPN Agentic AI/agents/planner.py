"""Rule based planner for the agent workflow."""

from __future__ import annotations

from typing import Dict, List

from agents.utils import get_latest_user_message
from config import DEAL_KEYWORDS


VALID_TASKS = ("product_search", "comparison", "deal_advisor")


class PlannerAgent:
    """Decide which specialist agents should execute for the current query."""

    def execute(self, state: Dict) -> Dict:
        tasks: List[str] = []
        latest_query = (get_latest_user_message(state) or "").lower()
        intent = state.get("intent", {})

        # Product search is always the primary task if we have a phone related query.
        tasks.append("product_search")

        comparison_keywords = ("compare", "versus", "vs", "difference")
        if any(keyword in latest_query for keyword in comparison_keywords):
            tasks.append("comparison")

        # Trigger comparisons automatically if the intent already mentions
        # multiple brands (e.g. Samsung vs iPhone) by checking for the word
        # "and" between known brand mentions.
        if " and " in latest_query and any(brand in latest_query for brand in ("samsung", "iphone", "apple", "pixel", "google", "oneplus")):
            if "comparison" not in tasks:
                tasks.append("comparison")

        if any(keyword in latest_query for keyword in DEAL_KEYWORDS):
            tasks.append("deal_advisor")

        # If the customer intent already stores deal information we keep the
        # advisor active for subsequent turns.
        if intent and intent.get("features"):
            if any("discount" in feature.lower() for feature in intent["features"]):
                if "deal_advisor" not in tasks:
                    tasks.append("deal_advisor")

        previous_tasks = state.get("tasks", [])
        current_index = state.get("current_task", 0)

        if tasks != previous_tasks:
            current_index = 0
        elif current_index >= len(tasks):
            current_index = len(tasks)

        return {"tasks": tasks, "current_task": current_index}