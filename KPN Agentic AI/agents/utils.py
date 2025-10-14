"""Shared utilities for the KPN agent layer."""
from __future__ import annotations

from typing import Any, Dict

from langchain_core.messages import BaseMessage


def get_latest_user_message(state: Dict[str, Any]) -> str:
    """Extract the latest user utterance from the LangGraph state."""

    messages = state.get("messages", [])
    for message in reversed(messages):
        if isinstance(message, BaseMessage):
            if getattr(message, "type", "") in {"human", "user"}:
                return message.content
        elif isinstance(message, tuple) and len(message) == 2:
            role, content = message
            if role in {"user", "human"}:
                return str(content)
        elif isinstance(message, dict):
            role = message.get("type") or message.get("role")
            if role in {"user", "human"}:
                return str(message.get("content", ""))
    return ""


def intent_to_search_query(intent: Dict[str, Any], fallback: str = "KPN phones") -> str:
    """Convert captured intent into a compact semantic-search query."""

    if not intent:
        return fallback

    parts = []
    brand = intent.get("brand")
    budget = intent.get("budget")
    features = intent.get("features") or []

    if isinstance(brand, str) and brand.strip():
        parts.append(brand.strip())
    if budget:
        parts.append(f"under €{budget}")
    if isinstance(features, list):
        parts.extend(str(feature) for feature in features if feature)

    query = " ".join(part for part in parts if part)
    return query or fallback
