# 07 · Checkpointer vs. Store

> **Pattern:** Give an agent two kinds of memory — a *transcript* of the current conversation (checkpointer) and *facts that outlive it* (store).
> **You'll learn:** why agents are stateless by default, thread-scoped memory with a checkpointer, cross-thread memory with a store, and how tools read/write the store.

---

## 1. Agents are goldfish

Every `agent.invoke(...)` starts from a blank slate. Tell it your name, ask for it back in the next
call, and it has no idea — nothing carried over. That's by design: an agent run is a pure function
of its input messages.

Real applications need two very different kinds of memory:

```
                    ┌────────────────────────────────────────────────┐
                    │                  CHECKPOINTER                  │
 thread "alice-1" ──►  msg, msg, msg, ...   (the running transcript) │   short-term,
 thread "alice-2" ──►  msg, msg, ...        (a separate transcript)  │   per-thread
                    └────────────────────────────────────────────────┘
                    ┌────────────────────────────────────────────────┐
                    │                     STORE                      │
   any thread ────►│  ("memories","alice") → {fact: "prefers km"}   │   long-term,
   any thread ────►│  ("memories","alice") → {fact: "vegetarian"}   │   cross-thread
                    └────────────────────────────────────────────────┘
```

| | **Checkpointer** | **Store** |
|---|---|---|
| Analogy | The chat transcript | The user-profile database |
| Scope | One thread (`thread_id`) | Shared across all threads |
| Holds | Full graph state (messages, etc.) | Namespaced key→value documents |
| Typical use | Multi-turn conversation, resume, undo | Preferences, learned facts, user data |
| Written by | The framework, automatically | Your code / your tools, explicitly |

---

## 2. Checkpointer: thread-scoped memory

A **checkpointer** saves the agent's entire state after every step, keyed by a `thread_id` you pass
in the config. Same thread → the conversation continues. New thread → clean slate.

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(llm, tools, checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "alice-1"}}
agent.invoke({"messages": [("human", "Hi, I'm Alice!")]}, config)
agent.invoke({"messages": [("human", "What's my name?")]}, config)   # → "Alice"
```

Note what you did **not** do: manage a message list. You send *only the new message*; the
checkpointer loads the prior state, appends, runs, and saves.

You can inspect (or rewind) what's saved:

```python
state = agent.get_state(config)
len(state.values["messages"])     # the full transcript so far
```

> **Beyond memory.** Because the checkpointer snapshots state at *every step* (not just per turn),
> it's also the foundation for resuming crashed runs, time-travel debugging, and human-in-the-loop
> interrupts — you get all of that for free by turning it on.

> **Production:** `InMemorySaver` vanishes with the process. Swap in a persistent one —
> `SqliteSaver` (`langgraph-checkpoint-sqlite`) or `PostgresSaver` (`langgraph-checkpoint-postgres`)
> — same interface, one-line change.

---

## 3. Store: cross-thread memory

A **store** is a key-value document store organised by **namespaces** (tuples, like folder paths).
It's not tied to any thread — anything written in one conversation is readable from every other.

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
store.put(("memories", "alice"), "pref-units", {"fact": "prefers metric units"})

store.get(("memories", "alice"), "pref-units").value   # {'fact': 'prefers metric units'}
store.search(("memories", "alice"))                    # everything known about alice
```

The namespace convention `("memories", <user_id>)` keeps each user's facts isolated — same store,
per-user shelves.

---

## 4. Tools that remember: the store inside the agent

Pass `store=` to `create_agent` and any tool can grab it at runtime with `get_store()` — this is how
an agent *decides* to remember something and recalls it days later in a brand-new thread:

```python
from langgraph.config import get_store

@tool
def save_memory(fact: str) -> str:
    """Save a fact about the user so it can be recalled in future conversations."""
    get_store().put(("memories", "user"), str(uuid4()), {"fact": fact})
    return f"Saved: {fact}"

agent = create_agent(llm, [save_memory, recall_memories],
                     checkpointer=InMemorySaver(), store=InMemoryStore())
```

Now the flow works across threads:

```
thread A: "Remember that I prefer metric units."  → agent calls save_memory(...)
thread B: "What units do I prefer?"               → agent calls recall_memories() → "metric"
```

The checkpointer alone could never do this — thread B's transcript is empty.

---

## 5. Choosing (and combining)

Use **both**, they answer different questions:

- *"What were we just talking about?"* → checkpointer.
- *"What do I know about this user, ever?"* → store.

A production agent typically runs with a Postgres checkpointer **and** a Postgres store: the
transcript gives coherence within a session; the store gives continuity across sessions.

One caveat: a checkpointer means transcripts **grow forever** — every turn appends. Managing what
the model actually *sees* from that history is its own craft: that's [Lesson 08](../08_conversation_memory/).

---

## 6. Cheat sheet

| Concept | What it does |
|---|---|
| `checkpointer=InMemorySaver()` | Auto-save agent state per step, keyed by thread |
| `{"configurable": {"thread_id": ...}}` | Which conversation to load/continue |
| `agent.get_state(config)` | Inspect the saved transcript/state |
| `store=InMemoryStore()` | Cross-thread key-value memory with namespaces |
| `store.put(ns, key, value)` / `.get` / `.search` | Write / read / list memories |
| `get_store()` (inside a tool) | Access the agent's store at runtime |
| `SqliteSaver` / `PostgresSaver` | Same API, survives restarts |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) — a forgetful agent, then thread memory, then an agent that remembers you across conversations.

**Next:** [08 · Conversation memory patterns](../08_conversation_memory/) — the transcript grows forever; what should the model actually *see*?
