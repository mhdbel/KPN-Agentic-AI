from graph.workflow import build_agentic_graph
from storage.persistence import PersistenceManager

class AgenticKPNChatbot:
    def __init__(self):
        self.graph = build_agentic_graph()
        self.persistence = PersistenceManager()
        print("🤖 Agentic KPN Chatbot initialized with persistence support!")

    def chat(self, query: str, thread_id: str = "default") -> str:
        # Load past state
        saved_state = self.persistence.load_state(thread_id)

        # Prepare input
        input_message = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": thread_id}}

        # Merge saved state into config (LangGraph will track it)
        response = self.graph.invoke(input_message, config)

        # Save new state (messages + results + tasks etc.)
        new_state = {
            "messages": response.get("messages", []),
            "tasks": response.get("tasks", []),
            "results": response.get("results", {}),
            "intent": response.get("intent", {}),
            "current_task": response.get("current_task", 0),
        }
        self.persistence.save_state(thread_id, new_state)

        # Extract last AI message (summary if completed)
        last_msg = response["messages"][-1]
        return last_msg[1] if isinstance(last_msg, tuple) else str(last_msg)

    def resume(self, thread_id: str = "default") -> dict:
        """Return the saved session state for inspection or continuation"""
        return self.persistence.load_state(thread_id)

    def reset(self, thread_id: str = "default") -> None:
        """Clear session history"""
        self.persistence.clear_state(thread_id)

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
