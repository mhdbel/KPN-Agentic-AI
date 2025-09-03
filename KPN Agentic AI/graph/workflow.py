from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages

# Import agents
from agents.intent import CustomerIntentAgent
from agents.planner import PlannerAgent
from agents.product_search import ProductSearchAgent
from agents.comparison import ComparisonAgent
from agents.deals import DealAdvisorAgent
from agents.summary import SummaryAgent

# --------------------------
# Define State
# --------------------------
class State(TypedDict):
    messages: Annotated[list, add_messages]
    intent: dict
    tasks: list
    current_task: int
    results: dict   # <-- NEW structured agent outputs
    
# --------------------------
# Build Workflow
# --------------------------
def build_agentic_graph():
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("intent_agent", CustomerIntentAgent().execute)
    workflow.add_node("planner", PlannerAgent().execute)
    workflow.add_node("product_search", ProductSearchAgent().execute)
    workflow.add_node("comparison", ComparisonAgent().execute)
    workflow.add_node("deal_advisor", DealAdvisorAgent().execute)
    workflow.add_node("summary", SummaryAgent().execute)

    # Flow
    workflow.add_edge(START, "intent_agent")
    workflow.add_edge("intent_agent", "planner")

    # Conditional execution: handle multiple tasks
    def next_task(state: State):
        idx = state.get("current_task", 0)
        tasks = state.get("tasks", [])
        if idx < len(tasks):
            return tasks[idx]
        else:
            return "summary"

    workflow.add_conditional_edges(
        "planner",
        next_task,
        {
            "product_search": "product_search",
            "comparison": "comparison",
            "deal_advisor": "deal_advisor",
            "summary": "summary",
        }
    )

    # After each task, increment index and decide next
    def task_done(state: State):
        return {"current_task": state.get("current_task", 0) + 1}

    workflow.add_edge("product_search", "planner", condition=task_done)
    workflow.add_edge("comparison", "planner", condition=task_done)
    workflow.add_edge("deal_advisor", "planner", condition=task_done)

    # Summary → END
    workflow.add_edge("summary", END)

    return workflow.compile(checkpointer=MemorySaver())