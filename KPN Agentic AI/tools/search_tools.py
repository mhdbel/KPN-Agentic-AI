"""Utility wrappers that expose the simple vector stores to the agents."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from storage.vector_store import vector_store_manager


def _format_result_items(results: List[Tuple[Dict[str, Any], float]]) -> List[Dict[str, Any]]:
    formatted: List[Dict[str, Any]] = []
    for record, score in results:
        item = dict(record)
        item["score"] = round(score, 2)
        formatted.append(item)
    return formatted


def _format_product_lines(items: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for idx, item in enumerate(items, start=1):
        line = [f"{idx}. {item['product_name']} ({item['brand']})", f"   Price: €{item['price']}"]
        if item.get("monthly_price"):
            line.append(f"   Monthly: €{item['monthly_price']} ({item.get('contract_type', '')})")
        if item.get("kpn_exclusive"):
            line.append("   🌟 KPN Exclusive Deal!")
        if item.get("features"):
            line.append("   Key features: " + ", ".join(item.get("features", [])[:3]))
        lines.append("\n".join(line))
    return "\n\n".join(lines)


def search_kpn_products(query: str) -> Dict[str, Any]:
    store_results = vector_store_manager.search_kpn(query, k=3)
    if not store_results:
        return {"text": "No KPN products found matching your query.", "items": []}

    items = _format_result_items(store_results)
    text = "📱 KPN product suggestions:\n\n" + _format_product_lines(items)
    return {"text": text, "items": items}


def search_external_products(query: str) -> Dict[str, Any]:
    store_results = vector_store_manager.search_external(query, k=3)
    if not store_results:
        return {"text": "No external products found matching your query.", "items": []}

    items = _format_result_items(store_results)
    text = "🌐 External market options:\n\n" + _format_product_lines(items)
    return {"text": text, "items": items}


def compare_with_market(query: str) -> Dict[str, Any]:
    store_results = vector_store_manager.search_hybrid(query, k=6)
    if not store_results:
        return {
            "text": "No overlapping results found for market comparison.",
            "kpn_products": [],
            "external_products": [],
            "insight": "",
        }

    kpn_results = [result for result in store_results if result[0].get("source") == "kpn"]
    external_results = [result for result in store_results if result[0].get("source") == "external"]

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
        if avg_kpn <= avg_external * 1.05:
            insight = "💡 KPN pricing is competitive against the wider market."
        else:
            insight = "💡 Position KPN extras to offset the higher hardware price."
        summary_sections.append(insight)

    text = "\n\n".join(section for section in summary_sections if section)
    return {
        "text": text,
        "kpn_products": kpn_items,
        "external_products": external_items,
        "insight": insight,
    }


def check_kpn_exclusive_deals(query: str) -> Dict[str, Any]:
    store_results = vector_store_manager.search_kpn(query, k=5)
    exclusive_results = [result for result in store_results if result[0].get("kpn_exclusive")]

    if not exclusive_results:
        fallback = search_kpn_products(query)
        text = (
            "Currently no exclusive deals found. Here are closely related KPN devices:\n\n"
            + fallback["text"]
        )
        return {"text": text, "items": fallback.get("items", [])}

    items = _format_result_items(exclusive_results[:3])
    text = "🌟 KPN exclusive promotions:\n\n" + _format_product_lines(items)
    return {"text": text, "items": items}