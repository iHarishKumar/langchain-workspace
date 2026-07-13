# Series 01 · LangChain Essentials

**Status: ✅ complete — 12/12 lessons.**

Twelve patterns, one arc: from a single `invoke()` to multi-agent systems with memory, retrieval,
streaming, and observability. Each lesson folder contains:

| File | Purpose |
|---|---|
| `README.md` | The deep-dive concept doc — the full lesson: explanation, diagrams, and worked examples |
| `notebook.ipynb` | A runnable demonstration with minimal prose — the code does the talking |

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

### State & memory
| # | Lesson | Status |
|---|---|---|
| 07 | [Checkpointer vs. store](07_checkpointer_vs_store/) — thread-scoped vs. cross-thread agent memory | ✅ |
| 08 | [Conversation memory patterns](08_conversation_memory/) — windowing, trimming, summarization | ✅ |

### Retrieval
| # | Lesson | Status |
|---|---|---|
| 09 | [RAG — naive to advanced](09_rag/) — the pipeline, then query rewriting, thresholds, citations | ✅ |

### Scaling up
| # | Lesson | Status |
|---|---|---|
| 10 | [Multi-agent and subgraph patterns](10_multi_agent/) — specialists, supervisors, agents-as-tools | ✅ |

### Production
| # | Lesson | Status |
|---|---|---|
| 11 | [Streaming and async](11_streaming_async/) — feel fast (stream) and be fast (async) | ✅ |
| 12 | [Tracing and evaluation with LangSmith](12_langsmith/) — see inside, measure quality | ✅ |

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

**Next series:** [02 · LangGraph Deep Dive](../ROADMAP.md) — everything this series used through
prebuilts (`create_agent`, checkpointers, subgraphs), rebuilt from raw graphs. See the
[roadmap](../ROADMAP.md).
