# Roadmap

The repo is organised as **series → lessons**: each series gets a numbered top-level folder, each
lesson a numbered folder inside it, always with the same two files (`README.md` deep dive +
`notebook.ipynb` runnable demo).

```
01_langchain_essentials/        ✅ complete (12 lessons)
02_langgraph_deep_dive/         🔜 next — planned below
03_production_rag/              🗺 outlined
04_agent_evals/                 🗺 outlined
```

---

## Series 02 · LangGraph Deep Dive — *next up*

**Why this one:** Series 01 used LangGraph the whole time — but always through prebuilts.
`create_agent` (lesson 06), checkpointers and stores (07), subgraphs (10) all sat on machinery we
never opened. This series opens the box: build the graphs yourself, then the production features
that only raw graphs unlock (human-in-the-loop, durable execution, time travel).

**Format:** same as series 01 — one folder per lesson, deep-dive README + minimal-prose notebook,
10 lessons, `gpt-4.1-nano`-friendly examples.

| # | Lesson (planned folder) | What it teaches |
|---|---|---|
| 01 | `01_graphs_from_scratch` | `StateGraph`, nodes, edges, compile/invoke — why graphs beat chains once state and cycles appear |
| 02 | `02_state_and_reducers` | Designing state schemas: `TypedDict`, `add_messages`, custom reducers, multiple state keys and who writes them |
| 03 | `03_control_flow` | Conditional edges, `Command(goto=..., update=...)`, loops and recursion limits — routing decided *inside* the graph |
| 04 | `04_rebuild_create_agent` | The capstone demystifier: rebuild lesson 06's agent from raw nodes (model node → tool node → should-continue edge) |
| 05 | `05_human_in_the_loop` | `interrupt()` and `Command(resume=...)`: approval gates, editing state mid-run, why this needs the checkpointer |
| 06 | `06_production_persistence` | `SqliteSaver`/`PostgresSaver`, time travel, forking a thread from an old checkpoint, state inspection in anger |
| 07 | `07_streaming_graph_runs` | Stream modes beyond agents, `get_stream_writer` for custom progress events, building a live progress UI |
| 08 | `08_parallelism_send_api` | `Send` for dynamic fan-out — series 01's orchestrator–worker (lesson 04) rebuilt as a proper map-reduce graph |
| 09 | `09_multi_agent_architectures` | Supervisor and handoff patterns from scratch; subgraph state mapping — what agents-as-tools (lesson 10) was hiding |
| 10 | `10_durability_and_deployment` | Retry policies, node caching, durable execution semantics, and serving a graph (FastAPI / LangGraph Server) |

**Callbacks to series 01:** lessons 04, 08 and 09 deliberately rebuild things series 01 did with
prebuilts — same behaviour, visible machinery. That contrast *is* the pedagogy.

---

## Series 03 · Production RAG — *outlined*

Series 01 lesson 09 ended at query rewriting, thresholds and citations. This series is everything
between that notebook and a RAG system users trust:

1. **Ingestion pipelines** — loaders, chunking strategies compared (fixed/recursive/semantic/markdown-aware), metadata design
2. **Hybrid search** — BM25 + vectors, reciprocal rank fusion, when keywords beat embeddings
3. **Rerankers** — cross-encoders re-ordering the top-k; measuring the gain
4. **Query understanding** — routing question types, decomposition of multi-hop questions
5. **RAG evaluation** — faithfulness, answer relevance, context recall; building the eval set from real queries (uses series 01 lesson 12 tooling)
6. **Agentic RAG** — retrieval as a tool, self-correcting retrieval loops
7. **Cost & latency** — embedding caches, semantic caching of answers, index update strategies
8. **Serving** — streaming RAG endpoints, citations in the UI

## Series 04 · Agent Evals — *outlined*

The newest, least-covered niche — measuring whether agents actually work:

1. **Datasets from traces** — mining production failures into test cases
2. **Trajectory evaluation** — judging the *path* (tool choices, order, efficiency), not just the answer
3. **Tool-call accuracy** — right tool, right arguments, per-step scoring
4. **Calibrating the LLM judge** — agreement with human labels, judge bias traps
5. **Regression gates** — evals in CI: block the prompt change that breaks five cases
6. **Online evaluation** — sampling live traffic, feedback loops, drift detection

---

## Decision log & cadence

- **Order of series 03 vs. 04** gets confirmed by audience response to series 01's finale post
  (it explicitly asks: LangGraph? Production RAG? Agent evals?). Series 02 is committed.
- **Publishing cadence:** 2 lessons/week (Tue + Thu, ~7 PM IST), matching series 01.
- Lesson lists above are plans, not contracts — lessons may split or merge as they're written, but
  folder naming and the README+notebook format are fixed.
