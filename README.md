# 🛡️ Insurance AI Research Agent

A production-quality, end-to-end **agentic AI system** for insurance research — built with a custom agent loop, OpenAI for reasoning, DuckDuckGo for live web data, and Streamlit for the interactive UI.

---

## Project Overview

This application demonstrates a fully custom AI agent (no LangChain, no CrewAI, no external agent frameworks) that can:

| Capability | Description |
|---|---|
| **General Q&A** | Answer any insurance-related question with structured detail |
| **Compare Insurance** | Side-by-side comparison of policies, states, or providers with tables |
| **Policy Recommendation** | Personalized coverage suggestions based on user profiles |
| **Concept Explanation** | Plain-language breakdowns of insurance terms and processes |
| **Trend Analysis** | Market trends, risk factor analysis, and forward-looking outlooks |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                  │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Query Type │  │  Text Input  │  │  Submit Button   │  │
│  └────────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│               Custom Agent Loop (agent.py)               │
│                                                          │
│  Step 1 ──▶ Classify Intent (LLM call)                   │
│  Step 2 ──▶ Decide: Search needed? (LLM call)            │
│  Step 3 ──▶ Generate search query (LLM call, if needed)  │
│         ──▶ Execute DuckDuckGo search (tools.py)         │
│  Step 4 ──▶ Synthesize final response (LLM call)         │
│                                                          │
└──────────────────────────┬───────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌──────────────────┐     ┌───────────────────┐
   │  OpenAI API      │     │  DuckDuckGo       │
   │  (prompts.py)    │     │  Search (tools.py) │
   └──────────────────┘     └───────────────────┘
```

### File Structure

```
project/
├── app.py              # Streamlit UI — input, output sections, reasoning display
├── agent.py            # Custom agent loop — orchestrates the full pipeline
├── tools.py            # DuckDuckGo search integration
├── prompts.py          # All LLM prompt templates (system, intent, search, synthesis)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Agent Workflow

```
User Input
    │
    ▼
┌─────────────────┐
│ Intent           │  → QA / COMPARISON / RECOMMENDATION / EXPLANATION / TREND
│ Classification   │     (LLM-powered or user-selected via dropdown)
└────────┬────────┘
         ▼
┌─────────────────┐
│ Search Decision  │  → SEARCH or NO_SEARCH
│                  │     (LLM decides based on query recency / specificity)
└────────┬────────┘
         ▼
   ┌─────┴─────┐
   │  SEARCH?  │
   └─────┬─────┘
    Yes  │  No
    ▼    │   ▼
┌────────┐ ┌──────────────┐
│ DDG    │ │ Skip search  │
│ Search │ │              │
└───┬────┘ └──────┬───────┘
    │             │
    └──────┬──────┘
           ▼
┌─────────────────┐
│ LLM Synthesis   │  → Structured response with Summary, Analysis, Takeaways
└────────┬────────┘
         ▼
   Streamlit UI
   (sections + reasoning steps)
```

---

## DuckDuckGo Integration

The agent uses `duckduckgo-search` as its **only external data source**. Implementation in `tools.py`:

```python
from duckduckgo_search import DDGS

def search_web(query, max_results=5):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return results
```

Search results are normalized to `{title, snippet, url}` dicts, then formatted into a text block and injected into the LLM's synthesis prompt so it can cite real sources.

---

## Setup Instructions

### 1. Clone / download the project

```bash
cd project
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your OpenAI API key

```bash
export OPENAI_API_KEY="sk-..."          # macOS / Linux
set OPENAI_API_KEY=sk-...               # Windows CMD
$env:OPENAI_API_KEY="sk-..."            # PowerShell
```

Or paste it into the sidebar text box when the app launches.

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Example Queries & Expected Outputs

### 1. General Q&A
**Query:** "What does umbrella insurance cover?"
- **Intent detected:** QA
- **Search:** Not required
- **Output:** Summary definition → detailed coverage scope → key takeaways

### 2. Comparison
**Query:** "Compare auto insurance rates in California vs Texas"
- **Intent detected:** COMPARISON
- **Search:** Required (current rates)
- **Output:** Summary → markdown comparison table (avg premiums, minimum coverage, factors) → takeaways

### 3. Recommendation
**Query:** "Recommend health insurance for a 30-year-old freelancer earning $60k"
- **Intent detected:** RECOMMENDATION
- **Search:** Required (current marketplace data)
- **Output:** Summary → bulleted plan options with reasoning → takeaways

### 4. Explanation
**Query:** "Explain what an insurance deductible is"
- **Intent detected:** EXPLANATION
- **Search:** Not required
- **Output:** Summary → plain-language definition with examples and analogies → takeaways

### 5. Trend Analysis
**Query:** "What are the trends in cyber insurance for 2025-2026?"
- **Intent detected:** TREND
- **Search:** Required (recent data)
- **Output:** Summary → historical context, current state, outlook → takeaways

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Custom agent loop** | Full control over reasoning steps; no framework lock-in |
| **Intent classification via LLM** | More flexible than keyword matching; handles nuanced queries |
| **LLM-driven search decision** | Avoids unnecessary API calls for conceptual questions |
| **DuckDuckGo (not Google)** | Free, no API key required, privacy-respecting |
| **Structured output format** | Every response follows Summary → Analysis → Takeaways |
| **Visible reasoning steps** | Explainable AI — users see exactly what the agent did |

---

## Technologies

- **Python 3.10+**
- **Streamlit** — interactive web UI
- **OpenAI API** — GPT-4o-mini (default) for all reasoning and synthesis
- **duckduckgo-search** — web search with no API key needed
- **Custom agent architecture** — no LangChain, no CrewAI, no AutoGen

---

