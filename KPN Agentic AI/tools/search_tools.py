from typing import Any, Dict, List, Tuple

from storage.vector_store import vector_store_manager


def _format_result_items(results: List[Tuple]) -> List[Dict[str, Any]]:
    formatted: List[Dict[str, Any]] = []
    for doc, score in results:
        metadata = doc.metadata
        formatted.append(
            {
                "product_name": metadata.get("product_name", ""),
                "brand": metadata.get("brand", ""),
                "price": metadata.get("price", 0),
                "monthly_price": metadata.get("monthly_price", 0),
                "contract_type": metadata.get("contract_type", ""),
                "kpn_exclusive": bool(metadata.get("kpn_exclusive", False)),
                "features": metadata.get("features", []),
                "source": metadata.get("source", "external"),
                "score": round(score, 4),
            }
        )
    return formatted


def _format_product_lines(items: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for idx, item in enumerate(items, start=1):
        line = [f"{idx}. {item['product_name']} ({item['brand']})", f"   Price: €{item['price']}"]
        if item.get("monthly_price"):
            line.append(f"   Monthly: €{item['monthly_price']} ({item.get('contract_type', '')})")
        if item.get("kpn_exclusive"):
            line.append("   🌟 KPN Exclusive Deal!")
        lines.append("\n".join(line))
    return "\n\n".join(lines)


def search_kpn_products(query: str) -> Dict[str, Any]:
    """Search for KPN products using semantic search (RAG)."""

    store = vector_store_manager.kpn_vector_store
    if not store:
        return {"text": "KPN vector store not initialized.", "items": []}

    results = store.similarity_search_with_score(query, k=3)
    if not results:
        return {"text": "No KPN products found matching your query.", "items": []}

    items = _format_result_items(results)
    text = "📱 KPN product suggestions:\n\n" + _format_product_lines(items)
    return {"text": text, "items": items}


def search_external_products(query: str) -> Dict[str, Any]:
    """Search for products from external sources using semantic search (RAG)."""

    store = vector_store_manager.external_vector_store
    if not store:
        return {"text": "External vector store not initialized.", "items": []}

    results = store.similarity_search_with_score(query, k=3)
    if not results:
        return {"text": "No external products found matching your query.", "items": []}

    items = _format_result_items(results)
    text = "🌐 External market options:\n\n" + _format_product_lines(items)
    return {"text": text, "items": items}


def compare_with_market(query: str) -> Dict[str, Any]:
    """Compare KPN products with broader market offerings using hybrid RAG search."""

    store = vector_store_manager.hybrid_vector_store
    if not store:
        return {"text": "Hybrid vector store not initialized.", "kpn_products": [], "external_products": [], "insight": ""}

    results = store.similarity_search_with_score(query, k=6)
    kpn_results = [(doc, score) for doc, score in results if doc.metadata.get("source") == "kpn"]
    external_results = [(doc, score) for doc, score in results if doc.metadata.get("source") == "external"]

    kpn_items = _format_result_items(kpn_results[:3])
    external_items = _format_result_items(external_results[:3])

    summary_sections = [f"📊 Market comparison for '{query}':\n"]
    if kpn_items:
        summary_sections.append("📱 KPN line-up:\n" + _format_product_lines(kpn_items))
    if external_items:
        summary_sections.append("🌐 Market alternatives:\n" + _format_product_lines(external_items))

    insight = ""
    if kpn_items and external_items:
        avg_kpn = sum(item["price"] for item in kpn_items) / len(kpn_items)
        avg_external = sum(item["price"] for item in external_items) / len(external_items)
        if avg_kpn <= avg_external * 1.1:
            insight = "💡 KPN is price competitive and bundles network perks."
        else:
            insight = "💡 Highlight KPN exclusives or service advantages to offset higher pricing."
        summary_sections.append(insight)

    text = "\n\n".join(section for section in summary_sections if section)
    return {"text": text, "kpn_products": kpn_items, "external_products": external_items, "insight": insight}


def check_kpn_exclusive_deals(query: str) -> Dict[str, Any]:
    """Check for KPN exclusive deals and offers."""

    store = vector_store_manager.kpn_vector_store
    if not store:
        return {"text": "KPN vector store not initialized.", "items": []}

    exclusive_query = f"KPN exclusive deals {query}"
    results = store.similarity_search_with_score(exclusive_query, k=5)
    exclusive_results = [(doc, score) for doc, score in results if doc.metadata.get("kpn_exclusive")]

    if not exclusive_results:
        fallback = search_kpn_products(query)
        text = "Currently no exclusive deals found. Here are closely related KPN devices:\n\n" + fallback["text"]
        return {"text": text, "items": fallback.get("items", [])}

    items = _format_result_items(exclusive_results[:3])
    text = "🌟 KPN exclusive promotions:\n\n" + _format_product_lines(items)
    return {"text": text, "items": items}
