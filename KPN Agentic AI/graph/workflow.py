"""Light-weight orchestrator that emulates the previous LangGraph flow."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from agents.comparison import ComparisonAgent
from agents.deals import DealAdvisorAgent
from agents.intent import CustomerIntentAgent
from agents.planner import PlannerAgent
from agents.product_search import ProductSearchAgent
from agents.summary import SummaryAgent


@dataclass
class AgentState:
    messages: List[Tuple[str, str]] = field(default_factory=list)
    intent: Dict[str, Any] = field(default_factory=dict)
    tasks: List[str] = field(default_factory=list)
    current_task: int = 0
    results: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_previous(cls, previous: Dict[str, Any]) -> "AgentState":
        messages: List[Tuple[str, str]] = []
        for message in previous.get("messages", []):
            if isinstance(message, dict):
                role = str(message.get("role") or message.get("type") or "assistant")
                content = str(message.get("content", ""))
                messages.append((role, content))
            elif isinstance(message, (list, tuple)) and len(message) == 2:
                role, content = message
                messages.append((str(role), str(content)))
        return cls(
            messages=messages,
            intent=dict(previous.get("intent", {})),
            tasks=list(previous.get("tasks", [])),
            current_task=int(previous.get("current_task", 0)),
            results=dict(previous.get("results", {})),
        )

    def add_messages(self, new_messages: List[Tuple[str, str]]) -> None:
        self.messages.extend((str(role), str(content)) for role, content in new_messages)


class AgenticGraph:
    """Recreates the decision flow of the LangGraph pipeline in pure Python."""

    def __init__(self) -> None:
        self.intent_agent = CustomerIntentAgent()
        self.planner = PlannerAgent()
        self.product_search = ProductSearchAgent()
        self.comparison = ComparisonAgent()
        self.deals = DealAdvisorAgent()
        self.summary = SummaryAgent()

    def invoke(self, query: str, previous_state: Dict[str, Any] | None = None) -> Dict[str, Any]:
        state = AgentState.from_previous(previous_state or {})
        state.add_messages([("user", query)])

        self._apply_update(state, self.intent_agent.execute(state.__dict__))
        self._apply_update(state, self.planner.execute(state.__dict__))

        while state.current_task < len(state.tasks):
            task_name = state.tasks[state.current_task]
            if task_name == "product_search":
                update = self.product_search.execute(state.__dict__)
            elif task_name == "comparison":
                update = self.comparison.execute(state.__dict__)
            elif task_name == "deal_advisor":
                update = self.deals.execute(state.__dict__)
            else:
                break

            self._apply_update(state, update)
            self._apply_update(state, self.planner.execute(state.__dict__))

        self._apply_update(state, self.summary.execute(state.__dict__))
        state.current_task = len(state.tasks)
        return {
            "messages": state.messages,
            "intent": state.intent,
            "tasks": state.tasks,
            "current_task": state.current_task,
            "results": state.results,
        }

    def _apply_update(self, state: AgentState, update: Dict[str, Any]) -> None:
        if not update:
            return
        if "messages" in update:
            state.add_messages(update["messages"])
        if "intent" in update:
            state.intent.update(update["intent"])
        if "tasks" in update:
            state.tasks = list(update["tasks"])
        if "current_task" in update:
            state.current_task = int(update["current_task"])
        if "results" in update:
            state.results.update(update["results"])


def build_agentic_graph() -> AgenticGraph:
    return AgenticGraph()