<div align="center">

# 🛡️ Insurance AI Research Agent

**Agentic AI System for Insurance Research**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![DuckDuckGo](https://img.shields.io/badge/DuckDuckGo-DE5833?style=for-the-badge&logo=duckduckgo&logoColor=white)](https://duckduckgo.com)

A production-quality, end-to-end **agentic AI system** built with a fully custom agent loop — no LangChain, no CrewAI, no external frameworks.

Uses **OpenAI** for reasoning, **DuckDuckGo** for live web search, and **Streamlit** for an interactive UI.

---

</div>

## ✨ What It Does

| Capability | Description |
|:---|:---|
| 🔹 **General Q&A** | Answer any insurance-related question with structured detail |
| 🔹 **Compare Insurance** | Side-by-side comparison of policies, states, or providers with tables |
| 🔹 **Policy Recommendation** | Personalized coverage suggestions based on user profiles |
| 🔹 **Concept Explanation** | Plain-language breakdowns of insurance terms and processes |
| 🔹 **Trend Analysis** | Market trends, risk factor analysis, and forward-looking outlooks |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI (app.py)                     │
│   ┌─────────────┐  ┌───────────────┐  ┌───────────────────┐  │
│   │  Query Type  │  │  Text Input   │  │  Submit Button    │  │
│   └─────────────┘  └───────────────┘  └───────────────────┘  │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                CUSTOM AGENT LOOP (agent.py)                   │
│                                                               │
│   Step 1 ──▶  Classify Intent         (LLM call)             │
│   Step 2 ──▶  Decide: Search needed?  (LLM call)             │
│   Step 3 ──▶  Generate search query   (LLM call, if needed)  │
│          ──▶  Execute DuckDuckGo search (tools.py)            │
│   Step 4 ──▶  Synthesize response     (LLM call)             │
│                                                               │
└────────────────────────────┬─────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
     ┌───────────────────┐     ┌────────────────────┐
     │    OpenAI API     │     │    DuckDuckGo      │
     │   (prompts.py)    │     │   Search (tools.py) │
     └───────────────────┘     └────────────────────┘
```

---

## 📁 Project Structure

```
📦 insurance-ai-research-agent
├── 🎯 app.py              → Streamlit UI — input, output sections, reasoning display
├── 🧠 agent.py            → Custom agent loop — orchestrates the full pipeline
├── 🔧 tools.py            → DuckDuckGo search integration
├── 📝 prompts.py          → All LLM prompt templates (system, intent, search, synthesis)
├── 📋 requirements.txt    → Python dependencies
└── 📖 README.md           → You are here
```

---

## 🔄 Agent Workflow

```
          ┌───────────────┐
          │  User Input    │
          └───────┬───────┘
                  ▼
       ┌─────────────────────┐
       │  Intent              │  → QA / Comparison / Recommendation
       │  Classification      │    / Explanation / Trend
       └──────────┬──────────┘
                  ▼
       ┌─────────────────────┐
       │  Search Decision     │  → SEARCH or NO_SEARCH
       │  (LLM decides)       │
       └──────────┬──────────┘
                  ▼
           ┌──────┴──────┐
      Yes  │   SEARCH?   │  No
           └──┬───────┬──┘
              ▼       ▼
     ┌──────────┐  ┌──────────────┐
     │ DuckDuck │  │ Skip search  │
     │ Go Search│  │              │
     └────┬─────┘  └──────┬───────┘
          └───────┬───────┘
                  ▼
       ┌─────────────────────┐
       │  LLM Synthesis       │  → Structured response
       │  (Summary + Detail   │     with citations
       │   + Takeaways)       │
       └──────────┬──────────┘
                  ▼
       ┌─────────────────────┐
       │  Streamlit UI        │
       │  (sections + steps)  │
       └─────────────────────┘
```

> 💡 **Every reasoning step** (intent detected, search decision, query used, results found) is logged and displayed in the UI for full explainability.

---

## 🔍 DuckDuckGo Integration

The agent uses `duckduckgo-search` as its **only external data source** — no Google API key needed.

```python
from duckduckgo_search import DDGS

def search_web(query, max_results=5):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return results
```

Results are normalized to `{title, snippet, url}` and injected into the LLM's synthesis prompt for grounded, citable responses.

---

## 🚀 Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/insurance-ai-research-agent.git
cd insurance-ai-research-agent
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set your OpenAI API key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

> ⚠️ Add `.env` to your `.gitignore` to keep your key safe.

### 5️⃣ Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 💬 Example Queries & Expected Outputs

| # | Query | Intent | Search? | Output Format |
|:---:|:---|:---|:---:|:---|
| 1 | *What does umbrella insurance cover?* | Q&A | ❌ | Summary → Detailed scope → Takeaways |
| 2 | *Compare auto insurance rates in California vs Texas* | Comparison | ✅ | Summary → **Comparison table** → Takeaways |
| 3 | *Recommend health insurance for a 30-year-old freelancer earning $60k* | Recommendation | ✅ | Summary → Bulleted plan options → Takeaways |
| 4 | *Explain what an insurance deductible is* | Explanation | ❌ | Summary → Definition + examples → Takeaways |
| 5 | *What are the trends in cyber insurance for 2025–2026?* | Trend Analysis | ✅ | Summary → Historical context + outlook → Takeaways |

---

## 🎯 Key Design Decisions

| Decision | Rationale |
|:---|:---|
| **Custom agent loop** | Full control over reasoning steps; no framework lock-in |
| **Intent classification via LLM** | More flexible than keyword matching; handles nuanced queries |
| **LLM-driven search decision** | Avoids unnecessary API calls for conceptual questions |
| **DuckDuckGo (not Google)** | Free, no API key required, privacy-respecting |
| **Structured output format** | Every response follows Summary → Analysis → Takeaways |
| **Visible reasoning steps** | Explainable AI — users see exactly what the agent did |

---

## 🧰 Tech Stack

<div align="center">

| Technology | Role |
|:---:|:---|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) | Core language |
| ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) | Interactive web UI |
| ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white) | LLM reasoning (GPT-4o-mini default) |
| ![DuckDuckGo](https://img.shields.io/badge/DuckDuckGo-DE5833?style=flat-square&logo=duckduckgo&logoColor=white) | Web search — no API key needed |

</div>

---

## ✅ What This Project Demonstrates

- 🧠 **Agentic AI system design** — fully custom orchestration loop with multi-step reasoning
- 🏥 **Real-world insurance domain** — Q&A, comparisons, recommendations, trend analysis
- 🔌 **External tool integration** — DuckDuckGo as a live data source
- 🚀 **End-to-end deployable app** — production-quality Streamlit UI
- 🔍 **Explainable AI** — every decision step is visible and traceable

---

<div align="center">

**Built with ❤️ using Python · OpenAI · DuckDuckGo · Streamlit**

</div>
