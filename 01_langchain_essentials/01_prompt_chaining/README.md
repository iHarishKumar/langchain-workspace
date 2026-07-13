# 01 · Prompt Chaining

> **Pattern:** Sequential LLM calls where each output feeds the next.
> **You'll learn:** LCEL pipe syntax, input/output mapping between steps, accumulating state, streaming, and error handling.

---

## 1. What is prompt chaining?

Prompt chaining is the most fundamental composition pattern in LangChain. Instead of asking a
single model call to do everything ("research this topic, outline it, and write an intro"), you
**break the work into discrete steps** and pipe the output of one step into the input of the next.

```
topic  →  [Step 1: Research angle]  →  [Step 2: Outline]  →  [Step 3: Intro paragraph]
```

Each step is a small, focused prompt. This is the LLM equivalent of the Unix philosophy: small
tools, composed together.

### Why not just one big prompt?

| One mega-prompt | Chained prompts |
|---|---|
| Model juggles many goals at once → quality drops | Each call has one clear job → higher quality |
| Hard to debug ("which part went wrong?") | Inspect the output of every step |
| Can't reuse pieces | Each sub-chain is reusable |
| One temperature / model for everything | Tune model, temperature, parsing per step |
| Failure = redo everything | Retry or cache individual steps |

The trade-off is **latency and cost**: N steps means N sequential round-trips. Chain when the
steps genuinely depend on each other. If they don't, see [Lesson 02 — Parallelization](../02_parallelization/).

---

## 2. The building blocks

Prompt chaining in modern LangChain is built on **LCEL** — the LangChain Expression Language.
LCEL lets you compose components with the `|` (pipe) operator, exactly like a shell pipeline.

### The Runnable interface

Everything in LCEL is a **Runnable** — a standard object with `.invoke()`, `.batch()`,
`.stream()`, and their async variants. Because every piece speaks the same interface, they snap
together:

```python
chain = prompt | llm | parser
```

Reading left to right: the `prompt` produces a message, the `llm` consumes it and produces an
`AIMessage`, and the `parser` converts that message into a plain string.

### The core pieces

| Component | Role |
|---|---|
| `ChatPromptTemplate` | Turns input variables into a list of chat messages |
| `init_chat_model(...)` (the LLM) | Calls the model, returns an `AIMessage` |
| `StrOutputParser` | Extracts the `.content` string from the `AIMessage` |
| `RunnablePassthrough` | Passes input through unchanged (used to keep earlier values around) |
| `\|` (pipe) | Connects two runnables — left output becomes right input |

### Initializing the model

We use `init_chat_model` rather than a provider-specific class like `ChatOpenAI`. It returns the
same chat-model interface but lets you switch providers by changing config — not code. The model is
read from `.env` in `provider:model` form, so a model swap never touches the notebook:

```python
import os
from langchain.chat_models import init_chat_model

# .env → CHAT_MODEL=openai:gpt-4o-mini  (init_chat_model reads the provider from the prefix)
llm = init_chat_model(os.environ["CHAT_MODEL"], temperature=0.7)
```

To switch to Anthropic, you'd only edit `.env` (`CHAT_MODEL=anthropic:claude-...`) and install the
matching integration package (e.g. `langchain-anthropic`).

---

## 3. Building the chain step by step

### Step 1 — Define each prompt

Each step is its own `prompt | llm | parser` sub-chain:

```python
angle_chain   = angle_prompt   | llm | parser   # topic   → angle
outline_chain = outline_prompt | llm | parser   # angle   → outline
intro_chain   = intro_prompt   | llm | parser   # outline → intro
```

The key detail: **the output variable of one step must match the input variable of the next.**
`angle_chain` produces a string that gets fed into `outline_prompt`, which expects an `{angle}`
variable.

### Step 2 — Wire them together and accumulate state

The naive way to chain is `angle_chain | outline_chain | intro_chain` — but that throws away the
intermediate results. You only get the final intro, not the angle or outline that produced it.

To **keep every intermediate value**, use `RunnablePassthrough.assign()`:

```python
from langchain_core.runnables import RunnablePassthrough

full_chain = (
    {"angle": angle_chain}                       # {topic} → {angle}
    | RunnablePassthrough.assign(outline=outline_chain)   # → {angle, outline}
    | RunnablePassthrough.assign(intro=intro_chain)       # → {angle, outline, intro}
)
```

`RunnablePassthrough.assign(key=some_chain)` runs `some_chain` and **adds** its result to the
dict under `key`, without dropping the keys already there. This is how you "accumulate" outputs
across a pipeline — the final result is a dict with all three values.

### Step 3 — Run it

```python
result = full_chain.invoke({"topic": "LangChain prompt chaining"})
result["angle"]    # → str
result["outline"]  # → str
result["intro"]    # → str
```

---

## 4. Streaming the final step

You don't have to wait for the whole chain. Run the early steps with `.invoke()`, then
`.stream()` the last one token by token — ideal for user-facing apps where the intro appears
live:

```python
intermediate = ({"angle": angle_chain}
                | RunnablePassthrough.assign(outline=outline_chain)
               ).invoke({"topic": "..."})

for chunk in intro_chain.stream({"outline": intermediate["outline"]}):
    print(chunk, end="", flush=True)
```

---

## 5. Error handling between steps

Real pipelines fail — rate limits, malformed output, timeouts. LCEL gives you two clean hooks:

**`.with_retry()`** — retry a flaky step with exponential backoff:

```python
robust_outline = outline_chain.with_retry(stop_after_attempt=3)
```

**`.with_fallbacks()`** — fall back to another runnable (e.g. a cheaper or different model) if the
primary fails:

```python
safe_intro = intro_chain.with_fallbacks([backup_intro_chain])
```

Because both return Runnables, you drop them straight back into the pipe — the rest of the chain
doesn't change.

---

## 6. When to use this pattern

✅ **Good fit**
- Multi-stage content generation (research → outline → draft → edit)
- Extract → transform → format pipelines
- Any task where step N genuinely needs the output of step N-1

❌ **Reach for something else**
- Steps are independent → [Parallelization](../02_parallelization/) (`RunnableParallel`)
- You need to pick *one of several* paths → [Routing](../03_routing/) (`RunnableBranch`)
- The model needs to decide its own steps dynamically → Agents (Lesson 06)

---

## 7. Cheat sheet

| Concept | What it does |
|---|---|
| `\|` pipe operator | Connects runnables — output of left becomes input of right |
| `StrOutputParser` | Converts `AIMessage` → plain `str` for the next step |
| `RunnablePassthrough` | Passes the current input through unchanged |
| `RunnablePassthrough.assign(key=chain)` | Runs a chain, adds its result as a new key |
| `.stream()` | Yields output tokens one by one |
| `.with_retry()` | Retries a step on failure with backoff |
| `.with_fallbacks([...])` | Swaps in a backup runnable if the primary fails |

▶️ **Run it:** open [`notebook.ipynb`](notebook.ipynb) and execute top to bottom.

**Next:** [02 · Parallelization](../02_parallelization/) — run independent steps at the same time.
