# 08 · Conversation Memory Patterns

> **Pattern:** The transcript grows every turn — decide what the model actually *sees*: everything, a window, a token budget, or a summary.
> **You'll learn:** why "append forever" fails, `trim_messages` (message- and token-based), the summarization pattern, and how to combine them.

---

## 1. The problem: history grows, windows don't

[Lesson 07](../07_checkpointer_vs_store/) gave agents a persistent transcript. Great — until you
notice what that implies. **Every turn appends**, and the whole history is re-sent on every call, so:

- **Cost grows linearly** — turn 50 pays for turns 1–49 again.
- **Latency grows** with input size.
- **Quality degrades** — models get distracted by long, stale context ("lost in the middle").
- Eventually you **exceed the context window** and the call just fails.

The fix is *not* to store less — storage is cheap and you may need the full log. The fix is to
separate two things:

```
   what you STORE  (the full raw transcript — checkpointer, lesson 07)
   what the model SEES  (a curated view built per call — this lesson)
```

Three classic ways to build that view: **windowing**, **token trimming**, **summarization**.

---

## 2. Windowing: keep the last N messages

The simplest view: recent turns only. LangChain's `trim_messages` does this with `token_counter=len`
(each message counts as 1):

```python
from langchain_core.messages import trim_messages

view = trim_messages(
    history,
    strategy="last",        # keep the most recent...
    token_counter=len,      # ...counting messages, not tokens
    max_tokens=6,           # keep 6 messages
    include_system=True,    # never drop the system prompt
    start_on="human",       # the view must start with a human turn
)
```

Those last two flags matter more than they look:

- `include_system=True` — the system prompt carries your instructions; losing it changes behaviour.
- `start_on="human"` — providers reject histories that open with an `AIMessage` (or a dangling
  `ToolMessage` whose call was trimmed away). `trim_messages` cuts on valid boundaries for you.

**Weakness:** anything outside the window is gone. The user's name from turn 1 has vanished by turn 20.

---

## 3. Token trimming: respect a real budget

Messages vary wildly in size — 6 messages could be 200 tokens or 20,000. Budget in **tokens**
instead by passing a token counter (the model itself, or any custom callable):

```python
view = trim_messages(
    history,
    strategy="last",
    token_counter=count_tokens,   # e.g. the llm, or your own fn(messages) -> int
    max_tokens=1000,              # a real token budget
    include_system=True,
    start_on="human",
)
```

This is the same pattern production stacks use: reserve the context window like a budget — system
prompt + tools + retrieved docs + *bounded* history + room for the answer.

---

## 4. Summarization: compress, don't discard

Trimming *forgets*. Summarization **compresses**: fold the older turns into a short summary message,
keep the recent turns verbatim:

```
[system] [msg1..msg8] [msg9] [msg10]
             │
             ▼  summarize once, cheaply
[system] [summary of msgs 1–8] [msg9] [msg10]
```

```python
summary = summarizer.invoke({"conversation": older_turns})
view = [SystemMessage(f"Summary of the conversation so far:\n{summary}")] + recent_turns
```

Now the fact from turn 1 *survives* — compressed, but recallable. The trade-offs: an extra LLM call
(run it every K turns, not every turn), and lossy compression (the summary keeps what the summarizer
thought mattered).

---

## 5. The hybrid that most assistants actually run

```
view = system prompt
     + running summary          (updated every K turns)
     + last N turns verbatim    (token-budgeted window)
```

Recent context stays exact (that's where pronouns like "it" resolve), old context stays cheap.
ChatGPT-style assistants, support bots, and copilots almost all converge on this shape.

**Where does this code live?** In a hand-rolled loop, you apply it before each call. Inside a
`create_agent`, the same logic plugs in as **middleware** (e.g. LangChain's built-in
`SummarizationMiddleware`) so it runs automatically before the model each turn — the pattern is
identical, only the mounting point changes.

---

## 6. Choosing

| Pattern | Keeps | Cost | When |
|---|---|---|---|
| Full history | Everything, exact | Grows every turn | Short-lived chats, demos |
| Window (last N) | Recent only | Flat | Task-focused bots where old turns don't matter |
| Token trim | Recent, budget-exact | Flat | Anything production — pair with a real budget |
| Summarization | Gist of everything | Flat + periodic LLM call | Long-running assistants |
| **Hybrid (summary + window)** | Gist + exact recent | Flat + periodic call | The default for serious chatbots |

---

## 7. Cheat sheet

| Concept | What it does |
|---|---|
| `trim_messages(strategy="last", ...)` | Keep the most recent slice of history |
| `token_counter=len` | Count messages → windowing |
| `token_counter=llm` / custom fn | Count tokens → real budgets |
| `include_system=True` | Never trim away the system prompt |
| `start_on="human"` | Cut on valid boundaries (no orphaned AI/tool messages) |
| Summary + recent window | The hybrid most assistants run |
| Store what happened, show what matters | The core principle |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) — watch the cost curve, then window, trim, summarize, and combine.

**Next:** [09 · RAG — naive to advanced](../09_rag/) — memory for *documents*: retrieval instead of transcripts.
