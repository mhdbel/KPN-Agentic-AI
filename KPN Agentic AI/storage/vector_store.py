"""In-memory product search utilities without external dependencies."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


@dataclass
class ProductRecord:
    product_name: str
    brand: str
    price: float
    description: str
    contract_type: Optional[str] = None
    monthly_price: Optional[float] = None
    kpn_exclusive: bool = False
    features: Optional[List[str]] = None
    source: str = "external"
    _tokens: Sequence[str] = field(default_factory=list, init=False, repr=False)

    @classmethod
    def from_payload(cls, payload: Dict, source: str) -> "ProductRecord":
        features = payload.get("features") or []
        if isinstance(features, str):
            features = [features]

        record = cls(
            product_name=str(payload.get("product_name", "")),
            brand=str(payload.get("brand", "")),
            price=float(payload.get("price", 0)),
            description=str(payload.get("description", "")),
            contract_type=payload.get("contract_type"),
            monthly_price=float(payload.get("monthly_price", 0)) if payload.get("monthly_price") is not None else None,
            kpn_exclusive=bool(payload.get("kpn_exclusive", False)),
            features=[str(feature) for feature in features],
            source=source,
        )
        record._tokens = _tokenize(record.search_blob)
        return record

    @property
    def search_blob(self) -> str:
        sections = [self.product_name, self.brand, self.description]
        if self.features:
            sections.extend(self.features)
        if self.contract_type:
            sections.append(self.contract_type)
        if self.monthly_price:
            sections.append(f"monthly {self.monthly_price}")
        return " ".join(section for section in sections if section)

    def to_dict(self) -> Dict[str, object]:
        return {
            "product_name": self.product_name,
            "brand": self.brand,
            "price": self.price,
            "monthly_price": self.monthly_price or 0,
            "contract_type": self.contract_type or "",
            "kpn_exclusive": self.kpn_exclusive,
            "features": self.features or [],
            "source": self.source,
            "description": self.description,
        }


class SimpleVectorStore:
    """Minimal semantic-ish search based on token overlap and heuristics."""

    def __init__(self, records: Iterable[ProductRecord]):
        self.records: List[ProductRecord] = list(records)

    def search(self, query: str, k: int = 3) -> List[Tuple[Dict[str, object], float]]:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        query_set = set(query_tokens)
        results: List[Tuple[Dict[str, object], float]] = []

        for record in self.records:
            if not record.product_name:
                continue

            token_overlap = len(query_set.intersection(record._tokens))
            brand_match = 1 if record.brand.lower() in query_set else 0

            score = token_overlap + brand_match

            # Budget awareness: if the query includes a numeric limit prefer
            # devices under that price ceiling.
            budget = _extract_budget(query_tokens)
            if budget and record.price <= budget:
                score += 2

            # Promote exclusive deals when searching the KPN store.
            if record.kpn_exclusive:
                score += 0.5

            if score == 0:
                continue

            results.append((record.to_dict(), float(score)))

        results.sort(key=lambda item: (-item[1], item[0].get("price", 0)))
        return results[:k]


def _extract_budget(tokens: Sequence[str]) -> Optional[int]:
    for token in tokens:
        if token.isdigit():
            try:
                value = int(token)
            except ValueError:
                continue
            if 100 <= value <= 5000:
                return value
    return None


class VectorStoreManager:
    """Loads the curated datasets and exposes lightweight search helpers."""

    def __init__(self, data_dir: str = os.path.join(os.path.dirname(__file__), "..", "data")):
        self.data_dir = os.path.abspath(data_dir)
        self.kpn_store: SimpleVectorStore | None = None
        self.external_store: SimpleVectorStore | None = None
        self.hybrid_store: SimpleVectorStore | None = None
        self.refresh()

    def refresh(self) -> None:
        kpn_records = self._load_records("kpn_products.json", source="kpn")
        external_records = self._load_records("external_products.json", source="external")

        self.kpn_store = SimpleVectorStore(kpn_records)
        self.external_store = SimpleVectorStore(external_records)
        self.hybrid_store = SimpleVectorStore([*kpn_records, *external_records])

    def _load_records(self, filename: str, source: str) -> List[ProductRecord]:
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)

        records: List[ProductRecord] = []
        for raw in payload:
            record = ProductRecord.from_payload(raw, source=source)
            if record.product_name:
                records.append(record)
        return records

    # Convenience wrappers -------------------------------------------------
    def search_kpn(self, query: str, k: int = 3) -> List[Tuple[Dict[str, object], float]]:
        if not self.kpn_store:
            return []
        return self.kpn_store.search(query, k=k)

    def search_external(self, query: str, k: int = 3) -> List[Tuple[Dict[str, object], float]]:
        if not self.external_store:
            return []
        return self.external_store.search(query, k=k)

    def search_hybrid(self, query: str, k: int = 6) -> List[Tuple[Dict[str, object], float]]:
        if not self.hybrid_store:
            return []
        return self.hybrid_store.search(query, k=k)


vector_store_manager = VectorStoreManager()

__all__ = ["VectorStoreManager", "vector_store_manager"]
