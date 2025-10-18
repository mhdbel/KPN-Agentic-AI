"""Central configuration shared across the KPN agent pipeline.

The previous iteration of the project depended on external LLM services
(`gemini-1.5-flash`) that required runtime API keys.  Because those keys are
not available in many testing environments we replace the direct model binding
with simple, deterministic configuration artefacts that can be consumed by the
agents.  The heuristics implemented in the agents reference these structures to
replicate the most important behaviour (brand detection, feature extraction and
task planning) without requiring any optional third-party dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


# ---------------------------------------------------------------------------
# Core domain knowledge
# ---------------------------------------------------------------------------

# Canonical brand names mapped from the keywords users tend to mention.
KNOWN_BRANDS: Dict[str, str] = {
    "samsung": "Samsung",
    "iphone": "Apple",
    "apple": "Apple",
    "pixel": "Google",
    "google": "Google",
    "oneplus": "OnePlus",
}


# Feature keywords mapped onto the phrasing we display back to the user.  The
# heuristics in ``CustomerIntentAgent`` rely on these terms to enrich the search
# query that is sent to the in-memory product catalogue.
FEATURE_KEYWORDS: Dict[str, str] = {
    "camera": "high resolution camera",
    "200mp": "200MP camera",
    "64mp": "64MP camera",
    "48mp": "48MP camera",
    "battery": "long battery life",
    "wireless": "wireless charging",
    "charging": "fast charging",
    "ip67": "IP67 water resistance",
    "ai": "AI features",
    "s-pen": "S-Pen support",
    "night": "night photography",
    "budget": "budget friendly",
    "discount": "discount",
}


# Terms that usually indicate the customer is hunting for promotions.
DEAL_KEYWORDS: Iterable[str] = (
    "deal",
    "discount",
    "promotion",
    "exclusive",
    "offer",
)


# ---------------------------------------------------------------------------
# Baseline intent model
# ---------------------------------------------------------------------------

@dataclass
class IntentDefaults:
    """Reusable default values for newly created intent dictionaries."""

    budget: int | None = None
    brand: str | None = None
    features: List[str] | None = None

    def to_dict(self) -> Dict[str, List[str] | int | None]:
        return {
            "budget": self.budget,
            "brand": self.brand,
            "features": self.features or [],
        }


DEFAULT_INTENT = IntentDefaults().to_dict()


__all__ = [
    "KNOWN_BRANDS",
    "FEATURE_KEYWORDS",
    "DEAL_KEYWORDS",
    "DEFAULT_INTENT",
]
