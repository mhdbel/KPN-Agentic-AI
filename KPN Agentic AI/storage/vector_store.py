"""Utilities for loading curated product data into lightweight FAISS vector stores."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from langchain.docstore.document import Document
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import FAISS


@dataclass
class ProductRecord:
    """Normalized representation of a single catalog entry."""

    product_name: str
    brand: str
    price: float
    description: str
    contract_type: Optional[str] = None
    monthly_price: Optional[float] = None
    kpn_exclusive: bool = False
    features: Optional[List[str]] = None
    source: str = "external"

    @classmethod
    def from_payload(cls, payload: Dict, source: str) -> "ProductRecord":
        """Create a record from a raw ingestion payload."""

        features = payload.get("features") or []
        if isinstance(features, str):
            features = [features]

        return cls(
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

    def to_document(self) -> Document:
        """Convert the record into a LangChain document for vector indexing."""

        content_sections = [self.product_name, self.brand, self.description]
        if self.features:
            content_sections.append("Features: " + ", ".join(self.features))
        if self.contract_type:
            content_sections.append(f"Contract: {self.contract_type}")
        if self.monthly_price:
            content_sections.append(f"Monthly price: €{self.monthly_price}")

        page_content = " \n".join(section for section in content_sections if section)

        metadata = {
            "product_name": self.product_name,
            "brand": self.brand,
            "price": self.price,
            "contract_type": self.contract_type or "",
            "monthly_price": self.monthly_price or 0,
            "kpn_exclusive": self.kpn_exclusive,
            "features": self.features or [],
            "source": self.source,
            "description": self.description,
        }
        return Document(page_content=page_content, metadata=metadata)


class VectorStoreManager:
    """Loads catalog data and provides FAISS-backed semantic search stores."""

    def __init__(self, data_dir: str = os.path.join(os.path.dirname(__file__), "..", "data")):
        self.data_dir = os.path.abspath(data_dir)
        self.embedding = FakeEmbeddings(size=1536)
        self.kpn_vector_store: Optional[FAISS] = None
        self.external_vector_store: Optional[FAISS] = None
        self.hybrid_vector_store: Optional[FAISS] = None
        self.refresh()

    # ------------------------------------------------------------------
    # Ingestion helpers
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """Load product datasets and rebuild the FAISS indexes."""

        kpn_docs = self._load_documents("kpn_products.json", source="kpn")
        external_docs = self._load_documents("external_products.json", source="external")

        self.kpn_vector_store = self._build_store(kpn_docs)
        self.external_vector_store = self._build_store(external_docs)
        self.hybrid_vector_store = self._build_store(kpn_docs + external_docs)

    def _load_documents(self, filename: str, source: str) -> List[Document]:
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        documents = []
        for raw_record in payload:
            record = ProductRecord.from_payload(raw_record, source=source)
            if not record.product_name:
                continue
            documents.append(record.to_document())
        return documents

    def _build_store(self, documents: Iterable[Document]) -> Optional[FAISS]:
        docs = list(documents)
        if not docs:
            return None
        return FAISS.from_documents(docs, self.embedding)


# Single shared instance used by the agents and tools
vector_store_manager = VectorStoreManager()

__all__ = ["VectorStoreManager", "vector_store_manager"]
