"""Intent extraction heuristics."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Dict, List

from agents.utils import get_latest_user_message
from config import DEFAULT_INTENT, FEATURE_KEYWORDS, KNOWN_BRANDS


class CustomerIntentAgent:
    """Derive a lightweight intent model from the latest user utterance."""

    def execute(self, state: Dict) -> Dict:
        user_query = get_latest_user_message(state)
        current_intent = deepcopy(state.get("intent", DEFAULT_INTENT))

        if not user_query:
            return {
                "messages": [("intent_agent", f"Intent unchanged: {current_intent}")],
                "intent": current_intent,
            }

        normalized = user_query.lower()

        # ------------------------------------------------------------------
        # Brand detection
        # ------------------------------------------------------------------
        for keyword, brand in KNOWN_BRANDS.items():
            if keyword in normalized:
                current_intent["brand"] = brand
                break

        # ------------------------------------------------------------------
        # Budget detection – grab the lowest mentioned amount to stay safe
        # ------------------------------------------------------------------
        budget_candidates: List[int] = []
        for match in re.findall(r"(?:€\s*)?(\d{3,4})", normalized):
            try:
                budget_candidates.append(int(match))
            except ValueError:
                continue

        # Detect phrases such as "under 800" or "below 700" explicitly.
        for match in re.findall(r"(?:under|below|max)\s+(\d{3,4})", normalized):
            try:
                budget_candidates.append(int(match))
            except ValueError:
                continue

        if budget_candidates:
            current_intent["budget"] = min(budget_candidates)

        # ------------------------------------------------------------------
        # Feature detection – map any keyword occurrences to canonical labels
        # ------------------------------------------------------------------
        features = set(current_intent.get("features", []) or [])
        for keyword, label in FEATURE_KEYWORDS.items():
            if keyword in normalized:
                features.add(label)

        current_intent["features"] = sorted(features)

        return {
            "messages": [
                (
                    "intent_agent",
                    "Updated intent → "
                    f"brand={current_intent.get('brand')}, "
                    f"budget={current_intent.get('budget')}, "
                    f"features={current_intent.get('features')}",
                )
            ],
            "intent": current_intent,
        }