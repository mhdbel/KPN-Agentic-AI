# KPN Agentic AI – Pipeline and Data Model Assessment

## 1. System Overview
- `AgenticKPNChatbot` wires LangGraph workflow execution with a JSON file persistence layer, persisting every conversation run after each `graph.invoke` call.【F:KPN Agentic AI/main.py†L4-L33】
- The LangGraph state tracks aggregated chat messages, extracted intent, the planner's task list, the index of the current task, and a dictionary intended to hold structured tool outputs.【F:KPN Agentic AI/graph/workflow.py†L18-L59】

## 2. What Works Today
- The intent, planner, product search, deal, and summary agents each encapsulate a clear prompt and return format, so the orchestration skeleton is in place.【F:KPN Agentic AI/agents/intent.py†L4-L36】【F:KPN Agentic AI/agents/planner.py†L4-L31】【F:KPN Agentic AI/agents/product_search.py†L4-L24】【F:KPN Agentic AI/agents/deals.py†L1-L7】【F:KPN Agentic AI/agents/summary.py†L4-L31】
- The summary agent already expects a structured `results` dictionary, which is the right direction for composing multi-tool answers.【F:KPN Agentic AI/agents/summary.py†L21-L31】

## 3. Critical Gaps Preventing a Working RAG Loop
- All RAG helpers reference a `vector_store_manager` object that is never defined or imported, so every tool call raises a `NameError` before it can search any documents.【F:KPN Agentic AI/tools/search_tools.py†L5-L135】
- There is no ingestion routine or static dataset in the repository to populate FAISS stores, leaving the data model for KPN devices undefined. Without a normalized schema (e.g., `product_name`, `brand`, `price`, `contract_type`, `kpn_exclusive`), the downstream prompts cannot ground their responses.
- Planner output is parsed with `eval`, which is unsafe and brittle when the LLM returns anything but a clean Python literal; invalid responses silently collapse to a hard-coded default task list.【F:KPN Agentic AI/agents/planner.py†L25-L29】

## 4. Orchestration & State Management Issues
- Task iteration never advances because `task_done` returns a dictionary but is passed to `add_edge(..., condition=...)`, which expects a boolean predicate; as a result the planner will re-emit the same first task indefinitely.【F:KPN Agentic AI/graph/workflow.py†L63-L69】
- The comparison and deal agents read `state["messages"][-1].content`, which will usually be the previous tool's output (not the user query), so later tasks end up comparing the planner's instructions instead of the customer's request.【F:KPN Agentic AI/agents/comparison.py†L3-L7】【F:KPN Agentic AI/agents/deals.py†L3-L7】
- Only the product search agent records its structured output in `state["results"]`; comparison and deal findings never reach the summary aggregator, so the final response cannot include those sections even when the tools succeed.【F:KPN Agentic AI/agents/product_search.py†L20-L24】【F:KPN Agentic AI/agents/comparison.py†L3-L7】【F:KPN Agentic AI/agents/deals.py†L3-L7】
- Persisting LangGraph `messages` via `json.dump` is likely to fail because the response contains LangChain message objects that are not JSON serializable.【F:KPN Agentic AI/main.py†L21-L33】【F:KPN Agentic AI/storage/persistence.py†L13-L20】

## 5. Recommendations to Stabilize the Pipeline
1. **Stand up the data layer**
   - Implement a `VectorStoreManager` that loads curated KPN catalog data plus competitive market data into FAISS indexes at start-up, and inject it into `search_tools`.
   - Define a canonical product schema (brand, handset, price, plan type, exclusivity flag, camera specs, etc.) and ensure every ingestion source conforms to it before indexing.

2. **Harden agent interactions**
   - Replace `eval` with strict JSON parsing for planner outputs and validate each task name against the supported set.
   - Have every downstream agent return both a human-readable message and a structured payload merged into `state["results"]` so the summary agent receives consistent inputs.
   - Feed the raw user intent (or dedicated state fields) into comparison and deal lookups rather than relying on the last message.

3. **Fix workflow control flow**
   - Increment `current_task` inside each task agent’s return payload and remove the misused `condition` parameter so the planner progresses through the task list deterministically.【F:KPN Agentic AI/graph/workflow.py†L63-L69】
   - Reset `current_task` when the planner emits a fresh plan to avoid reusing stale indices between conversations.

4. **Make persistence robust**
   - Serialize LangGraph messages via their `.to_dict()` representation (or store only lightweight summaries) before writing to disk, and apply the same transformation on load.
   - Persist tool `results`, planner task lists, and intent snapshots in a schema that matches the vector-store product model so that sessions can be resumed reliably.

By implementing the data layer and tightening the orchestration contracts, the RAG chatbot will be able to ground its reasoning in a well-defined catalog and consistently guide shoppers through KPN’s offerings.
