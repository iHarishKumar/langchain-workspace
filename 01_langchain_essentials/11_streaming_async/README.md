# 11 · Streaming and Async

> **Pattern:** Two different performance problems, two different tools — *feel* fast with streaming, *be* fast with async concurrency.
> **You'll learn:** token streaming through chains, agent stream modes, `ainvoke`/`astream`/`abatch`, and concurrency with `asyncio.gather`.

---

## 1. Two axes of "fast"

An LLM call takes seconds. Users experience that two ways, and each has its own fix:

| Problem | Symptom | Fix |
|---|---|---|
| **Perceived latency** | User stares at a spinner for 8s | **Streaming** — show tokens as they generate |
| **Throughput** | 20 calls take 20× as long | **Async** — run them concurrently |

Streaming doesn't make generation faster — first token just arrives in ~300ms instead of the whole
answer in 8s. That difference is most of why chat UIs feel instant. Async doesn't speed up any
single call — it stops calls from *waiting in line* when they don't depend on each other.

---

## 2. Streaming

Every Runnable has `.stream()` — the same interface from Lesson 01, one letter away from `.invoke()`:

```python
for chunk in llm.stream("Explain LCEL in two sentences."):
    print(chunk.content, end="", flush=True)
```

**Chains stream end-to-end.** In `prompt | llm | StrOutputParser()`, the parser transforms chunks
*as they pass through*, so `chain.stream(...)` yields clean strings token by token. This is a
designed-in property of LCEL: components declare how to handle streams, and the pipe just works.
(One blocking step — like a non-streaming parser — turns the tap off from there on.)

### Streaming agents

Agents stream at three granularities via `stream_mode`:

| Mode | Yields | Use for |
|---|---|---|
| `"values"` | Full state after each step | Debugging traces (Lesson 06) |
| `"updates"` | Just each step's delta | Progress indicators — "calling tool X..." |
| `"messages"` | (token, metadata) pairs | Chat-UI token streaming of agent answers |

```python
for token, meta in agent.stream({"messages": [...]}, stream_mode="messages"):
    if token.content:
        print(token.content, end="", flush=True)
```

---

## 3. Async

Every sync method has an `a`-prefixed twin: `ainvoke`, `astream`, `abatch`. Same arguments, same
results — they just *await* instead of block, so one Python process can have many calls in flight.

```python
result = await llm.ainvoke("...")           # top-level await works in notebooks

async for chunk in chain.astream({...}):    # async + streaming compose
    ...
```

### Concurrency: the whole point

```python
# Sequential: 5 calls ≈ 5 × latency
for q in questions:
    llm.invoke(q)

# Concurrent: 5 calls ≈ 1 × latency (the slowest one)
results = await asyncio.gather(*(llm.ainvoke(q) for q in questions))
```

The speedup is nearly N× because the time is **network wait, not CPU** — exactly what async excels
at. Results come back in input order, regardless of finish order.

### `batch` vs `gather` vs `abatch`

| Call | Mechanism | When |
|---|---|---|
| `.batch(inputs)` | Thread pool | Scripts/notebooks; sync code (Lesson 02) |
| `asyncio.gather(*coros)` | Event loop | Mixed workloads — different chains/calls in flight |
| `.abatch(inputs)` | Event loop | Same runnable, many inputs, inside async code |

In a script, `.batch()` is fine. In a **server** (FastAPI et al.), async is the difference between
"handles hundreds of concurrent users" and "one request blocks the worker" — that's where the `a`
methods earn their keep. Add `max_concurrency` to be kind to rate limits:

```python
await chain.abatch(inputs, config={"max_concurrency": 5})
```

---

## 4. Putting both together

A production chat endpoint typically does both at once: `astream` the answer to the user
(perceived speed) while `gather`-ing side work — logging, memory writes, a title-generation call
(throughput). Everything in Lessons 01–10 was built from Runnables, so **everything you've built so
far already supports all of this** — same chains, one letter different.

---

## 5. Cheat sheet

| Concept | What it does |
|---|---|
| `.stream()` / `.astream()` | Yield output chunks as they generate |
| LCEL streams through | Parsers transform chunks in-flight; pipes stay streaming |
| `stream_mode="updates"` / `"messages"` | Agent progress events / token-level agent output |
| `ainvoke` / `abatch` | Awaitable twins of `invoke` / `batch` |
| `asyncio.gather(*coros)` | Independent calls concurrently; ~N× on network-bound work |
| `config={"max_concurrency": n}` | Throttle to respect rate limits |
| Streaming = feels fast; async = is fast | Different axes — production uses both |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) — watch tokens flow, then race sequential vs. concurrent with a stopwatch.

**Next:** [12 · Tracing and evaluation with LangSmith](../12_langsmith/) — see inside everything you've built, and measure whether it's any good. *(Series finale.)*
