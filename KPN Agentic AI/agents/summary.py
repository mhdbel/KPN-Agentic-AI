"""Generate deterministic summaries for completed workflows."""
from __future__ import annotations

from typing import Dict, List


class SummaryAgent:
    """Compose a readable recap of the tasks executed by the pipeline."""

    def execute(self, state: Dict) -> Dict:
        results = state.get("results", {})
        sections: List[str] = []

        product_block = results.get("product_search", {})
        product_matches = product_block.get("matches", [])
        if product_matches:
            lines = ["📱 Search Results:"]
            for item in product_matches:
                line = f"- {item['product_name']} ({item['brand']}) – €{item['price']}"
                if item.get("features"):
                    line += f" | {', '.join(item['features'][:3])}"
                lines.append(line)
            sections.append("\n".join(lines))

        comparison_block = results.get("comparison", {})
        if comparison_block.get("kpn_products") or comparison_block.get("external_products"):
            lines = ["📊 Comparison:"]
            if comparison_block.get("kpn_products"):
                lines.append("KPN picks:")
                for item in comparison_block["kpn_products"]:
                    lines.append(f"  • {item['product_name']} – €{item['price']}")
            if comparison_block.get("external_products"):
                lines.append("Market alternatives:")
                for item in comparison_block["external_products"]:
                    lines.append(f"  • {item['product_name']} – €{item['price']}")
            if comparison_block.get("insight"):
                lines.append(comparison_block["insight"])
            sections.append("\n".join(lines))

        deals_block = results.get("deal_advisor", {})
        deals = deals_block.get("deals", [])
        if deals:
            lines = ["🌟 Exclusive Deals:"]
            for item in deals:
                line = f"- {item['product_name']} – €{item['price']}"
                if item.get("contract_type"):
                    line += f" ({item['contract_type']})"
                lines.append(line)
            sections.append("\n".join(lines))

        recommendation = self._build_recommendation(product_matches, comparison_block, deals)
        sections.append(f"💡 Final Recommendation:\n{recommendation}")

        return {"messages": [("summary", "\n\n".join(sections))]}

    def _build_recommendation(self, products: List[Dict], comparison: Dict, deals: List[Dict]) -> str:
        if deals:
            best_deal = deals[0]
            return (
                f"Leverage the KPN exclusive offer on {best_deal['product_name']} "
                f"for €{best_deal['price']} to maximise savings."
            )

        if products:
            candidate = min(products, key=lambda item: item.get("price", 0))
            return (
                f"{candidate['product_name']} delivers the best balance of price and "
                "features based on your preferences."
            )

        if comparison.get("kpn_products"):
            candidate = comparison["kpn_products"][0]
            return (
                f"Consider {candidate['product_name']} from the KPN line-up to keep "
                "everything under one provider."
            )

        if comparison.get("external_products"):
            candidate = comparison["external_products"][0]
            return (
                f"Market alternative {candidate['product_name']} is the closest match "
                "available right now."
            )

        return "Let us know more about your requirements and we'll refine the search."
