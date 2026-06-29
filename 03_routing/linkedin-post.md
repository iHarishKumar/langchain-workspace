Most LLM apps answer every question with the same prompt.

A refund request and an app crash report get the exact same treatment.

That's a mistake. The fix is routing — picking the RIGHT chain for each input.

query → router → billing | technical | general

Three ways to build the router, trading cost for smarts:

𝟭. 𝗙𝘂𝗻𝗰𝘁𝗶𝗼𝗻 𝗿𝗼𝘂𝘁𝗲𝗿 — a Python if/else returning a chain.
Free and instant. But "my card got hit twice" has no keyword → wrong route.

𝟮. 𝗟𝗟𝗠 𝗰𝗹𝗮𝘀𝘀𝗶𝗳𝗶𝗲𝗿 + 𝗥𝘂𝗻𝗻𝗮𝗯𝗹𝗲𝗕𝗿𝗮𝗻𝗰𝗵 — a model labels the query, then you branch.
Handles messy language. Costs one extra LLM call.

𝟯. 𝗦𝗲𝗺𝗮𝗻𝘁𝗶𝗰 𝗿𝗼𝘂𝘁𝗶𝗻𝗴 — the one most people skip.
Embed a few examples per route. Route each query to the nearest one by cosine similarity.
No keywords. No classifier LLM. Just one cheap embedding call.

"Reverse the duplicate payment" has zero billing keywords — but its embedding lands right next to the billing examples. Routed correctly.

In production you layer them:
function router → semantic → LLM classifier for the truly ambiguous.

Full write-up + a notebook with all three on one support-desk example. Link in comments. 👇

Article 3 of a LangChain series. That's the foundation trio done — next: orchestration.

#LangChain #LLM #AIEngineering #Python #GenAI
