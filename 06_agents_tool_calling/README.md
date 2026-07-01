# 06 · Agents and Tool Calling

> **Pattern:** Give the model tools and let *it* decide which to call, with what arguments, and when it's done.
> **You'll learn:** the `@tool` decorator, tool schemas, `create_agent`, the LangGraph agent loop, and tool error handling.

---

## 1. From fixed flow to decided flow

Every pattern so far had a control flow *you* designed — chain, parallel, route, plan. An **agent**
inverts that: you provide tools and a goal, and the **model** drives the loop. This is the **ReAct**
pattern (Reason + Act):

```
question ─► [LLM reasons] ─► [call a tool] ─► [observe result] ─► ... ─► final answer
                 ▲───────────────────────────────────────────┘
```

The model reasons about what it needs, calls a tool, reads the result, and repeats until it can
answer. It might call zero tools, or five, or the same tool three times — decided at runtime.

---

## 2. Tools: the docstring *is* the API

The `@tool` decorator turns a function into something the model can call. Crucially, the model never
sees your code — it sees the **name, docstring, and type hints**. Those are the schema:

```python
from langchain_core.tools import tool

@tool
def get_stock_price(ticker: str) -> str:
    """Get the latest price for a stock ticker symbol (e.g. 'AAPL')."""
    ...
```

Inspect what the model actually receives:

```python
get_stock_price.name         # 'get_stock_price'
get_stock_price.description  # the docstring
get_stock_price.args         # {'ticker': {'type': 'string', ...}}  ← from type hints
```

**Write docstrings and type hints for the model.** A vague description ("does stuff with a ticker")
leads to wrong or skipped calls. Name the parameters, give an example, state units and formats.

---

## 3. Build the agent

LangChain's `create_agent` assembles the whole loop — model, tools, state, and the
observe-and-repeat logic — into one runnable:

```python
from langchain.agents import create_agent

agent = create_agent(llm, tools)          # `llm` can also be a string, e.g. "openai:gpt-4o-mini"

result = agent.invoke({"messages": [("human", "What is 23.5 times 8?")]})
result["messages"][-1].content     # the final answer
```

Input and output are a **list of messages** (`human`, `ai`, `tool`). The final answer is the last
message; everything before it is the reasoning trace.

> **Version note.** `create_agent` (in `langchain.agents`) is the LangChain 1.x prebuilt agent. It
> replaces the older `langgraph.prebuilt.create_react_agent` — same idea, but the import and the
> system-prompt argument (`system_prompt=`, not `prompt=`) changed. It's still built on LangGraph
> under the hood.

> **Why not a bare loop?** You *could* hand-roll `while` around `llm.bind_tools(...)`. `create_agent`
> gives you managed state, streaming, error handling, checkpointing hooks (Lesson 07), and
> interruptibility for free — the things that matter once an agent leaves your notebook.

---

## 4. Observability: stream the loop

An agent's control flow is opaque unless you watch it. Stream every step to see each reason →
tool-call → observation:

```python
for step in agent.stream({"messages": [("human", "Price of AAPL, times 10?")]},
                         stream_mode="values"):
    step["messages"][-1].pretty_print()
```

You'll see the model call `get_stock_price('AAPL')`, observe `$214.30`, then call
`multiply(214.30, 10)` — **chaining tools it chose itself.** This trace is your primary debugging
tool (and a preview of [Lesson 12 — LangSmith](../README.md)).

---

## 5. Tool error handling

Tools fail: bad arguments, network errors, unknown inputs. By default, when a tool **raises**,
LangGraph catches it and feeds the error back to the model as a `ToolMessage` — the agent can then
retry with different arguments or explain the failure, instead of your program crashing:

```python
@tool
def get_stock_price(ticker: str) -> str:
    """..."""
    if ticker.upper() not in prices:
        raise ValueError(f"Unknown ticker '{ticker}'.")   # becomes a ToolMessage, not a crash
```

For production you'll want to tune this — validating inputs, customizing the error message the model
sees, or failing hard on certain errors. But the default (surface the error to the model) is the
right starting point.

---

## 6. Steering behaviour

Pass a `prompt` (system message) to shape persona and tool discipline:

```python
agent = create_agent(llm, tools,
    system_prompt="Always use tools for arithmetic and prices instead of guessing.")
```

This is how you stop an agent from hallucinating an answer it should have looked up.

---

## 7. When to use an agent (and when not to)

✅ **Good fit** — open-ended tasks where the needed steps depend on intermediate results:
research, multi-step Q&A over tools/APIs, "do X using whatever tools apply."

❌ **Overkill** — if you already know the steps, a chain/router is cheaper, faster, and more
predictable. Agents trade control for flexibility: more LLM calls, more variance, more ways to go
wrong. Don't reach for an agent when a `RunnableBranch` would do.

---

## 8. Cheat sheet

| Concept | What it does |
|---|---|
| `@tool` | Function → tool; **docstring + type hints = schema** |
| `tool.name` / `.description` / `.args` | Exactly what the model reads |
| `create_agent(llm, tools)` | Prebuilt ReAct loop with managed state |
| messages in / messages out | I/O is a message list; final answer = last message |
| `stream_mode="values"` | Watch each reason→act→observe step |
| Raising tool → `ToolMessage` | Errors go back to the model, not a crash |
| `system_prompt=...` | Steer persona and when to use tools |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) — three tools, tool-chaining, error recovery, and streaming.

**Next:** [07 · Checkpointer vs. store](../README.md) — short-term vs. long-term memory for agents. *(Coming soon.)*
