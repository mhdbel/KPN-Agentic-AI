from typing import Any, Dict, List

from langchain_core.messages import BaseMessage

from graph.workflow import build_agentic_graph
from storage.persistence import PersistenceManager

class AgenticKPNChatbot:
    def __init__(self):
        self.graph = build_agentic_graph()
        self.persistence = PersistenceManager()
        print("🤖 Agentic KPN Chatbot initialized with persistence support!")

    def chat(self, query: str, thread_id: str = "default") -> str:
        # Load past state
        self.persistence.load_state(thread_id)

        # Prepare input
        input_message = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": thread_id}}

        # Merge saved state into config (LangGraph will track it)
        response = self.graph.invoke(input_message, config)

        # Save new state (messages + results + tasks etc.)
        new_state = self._serialize_state(response)
        self.persistence.save_state(thread_id, new_state)

        # Extract last AI message (summary if completed)
        last_msg = response["messages"][-1]
        if isinstance(last_msg, BaseMessage):
            return last_msg.content
        if isinstance(last_msg, tuple) and len(last_msg) == 2:
            return str(last_msg[1])
        if isinstance(last_msg, dict):
            return str(last_msg.get("content", ""))
        return str(last_msg)

    def resume(self, thread_id: str = "default") -> dict:
        """Return the saved session state for inspection or continuation"""
        return self.persistence.load_state(thread_id)

    def reset(self, thread_id: str = "default") -> None:
        """Clear session history"""
        self.persistence.clear_state(thread_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _serialize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "messages": self._serialize_messages(state.get("messages", [])),
            "tasks": state.get("tasks", []),
            "results": state.get("results", {}),
            "intent": state.get("intent", {}),
            "current_task": state.get("current_task", 0),
        }

    @staticmethod
    def _serialize_messages(messages: List[Any]) -> List[Dict[str, str]]:
        serialized: List[Dict[str, str]] = []
        for message in messages:
            if isinstance(message, BaseMessage):
                serialized.append({"role": message.type, "content": message.content})
            elif isinstance(message, tuple) and len(message) == 2:
                role, content = message
                serialized.append({"role": str(role), "content": str(content)})
            elif isinstance(message, dict):
                role = message.get("type") or message.get("role") or "assistant"
                serialized.append({"role": str(role), "content": str(message.get("content", ""))})
            else:
                serialized.append({"role": "assistant", "content": str(message)})
        return serialized

if __name__ == "__main__":
    bot = AgenticKPNChatbot()

    # New conversation
    print(bot.chat("I need a Samsung phone under €800 with good camera", thread_id="user123"))
    print(bot.chat("Compare it with iPhone 15", thread_id="user123"))

    # Resume later
    print("\n--- Resuming Saved Session ---")
    print(bot.resume("user123"))

    # Clear state
    bot.reset("user123")
