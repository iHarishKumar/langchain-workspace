# LangChain Workspace

A hands-on tutorial series on building with **LangChain** and **LangGraph** — one lesson per pattern, from foundational prompt chaining all the way to multi-agent systems and production observability.

Each lesson lives in its own folder and contains:

| File | Purpose |
|---|---|
| `README.md` | The deep-dive concept doc — the full lesson: explanation, diagrams, and worked examples |
| `notebook.ipynb` | A runnable demonstration with minimal prose — the code does the talking |

---

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
cp .env.example .env             # then edit .env and paste your OpenAI key

# 4. Launch Jupyter
jupyter lab                      # or: jupyter notebook
```

All notebooks load credentials from `.env` via `python-dotenv`. Models are created with LangChain's
provider-agnostic `init_chat_model` / `init_embeddings`, defaulting to OpenAI's `gpt-4o-mini` — swap
the provider in the setup cell of any notebook (the matching integration package must be installed).

---

## Lessons

### Foundation patterns
| # | Lesson | Status |
|---|---|---|
| 01 | [Prompt chaining](01_prompt_chaining/) — sequential LLM calls with LCEL | ✅ |
| 02 | [Parallelization](02_parallelization/) — concurrent chains with `RunnableParallel` | ✅ |
| 03 | [Routing](03_routing/) — rule-based and semantic routing | ✅ |

### Orchestration patterns
| # | Lesson | Status |
|---|---|---|
| 04 | [Orchestrator–worker](04_orchestrator_worker/) — a planner delegates subtasks to workers | ✅ |
| 05 | [Evaluator–optimizer](05_evaluator_optimizer/) — generate → score → refine loop | ✅ |
| 06 | [Agents and tool calling](06_agents_tool_calling/) — ReAct agents with `create_agent` | ✅ |

### Coming next
| # | Lesson |
|---|---|
| 07 | Checkpointer vs. store |
| 08 | Conversation memory patterns |
| 09 | RAG — naive to advanced |
| 10 | Multi-agent and subgraph patterns |
| 11 | Streaming and async |
| 12 | Tracing and evaluation with LangSmith |

---

## Suggested sequencing

| Phase | Lessons | Notes |
|-------|---------|-------|
| Foundation | 01 → 02 → 03 | Read in order — each builds on the last |
| Orchestration | 04 → 05 → 06 | Independent after the foundation |
| State & memory | 07 + 08 | Best read together |
| RAG | 09 | Slots in any time after lesson 03 |
| Multi-agent | 10 | Escalation from lesson 04 |
| Production | 11 → 12 | Series closer — applies to everything before |
