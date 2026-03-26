"""
app.py — Streamlit front-end for the Insurance AI Research Agent.

Provides a clean, sectioned interface that surfaces the agent's
reasoning steps alongside the structured response.
"""

import os

import streamlit as st

from agent import DROPDOWN_TO_INTENT, INTENT_LABELS, InsuranceAgent

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Insurance AI Research Agent",
    page_icon="🛡️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS for a polished look
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Main header */
    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #6b7280;
        font-size: 1.05rem;
        margin-top: -0.5rem;
    }

    /* Section cards */
    .section-card {
        background: var(--background-color, #ffffff);
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }
    .section-card h3 {
        margin-top: 0;
        font-size: 1.1rem;
    }

    /* Reasoning steps */
    .reasoning-step {
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 0.85rem;
        padding: 0.3rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>🛡️ Insurance AI Research Agent</h1>
        <p>Agentic AI system for insurance research — powered by OpenAI + DuckDuckGo search</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ---------------------------------------------------------------------------
# Sidebar — configuration
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
   
    model = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0,
    )
    st.divider()
    st.markdown("### 📋 Example Queries")
    examples = [
        "What is the difference between HMO and PPO plans?",
        "Compare auto insurance rates in California vs Texas",
        "Recommend health insurance for a 30-year-old freelancer",
        "Explain what an insurance deductible is",
        "What are the trends in cyber insurance for 2025–2026?",
    ]
    for ex in examples:
        st.markdown(f"- {ex}")

# ---------------------------------------------------------------------------
# Input area
# ---------------------------------------------------------------------------
with st.form("query_form"):
    col1, col2 = st.columns([1, 2])

    with col1:
        query_type = st.selectbox(
            "Query Type",
            list(INTENT_LABELS.values()),
            index=0,
        )

    with col2:
        user_query = st.text_input(
            "Your Question",
            placeholder="e.g. Compare home insurance in Florida vs Texas",
        )

    submit = st.form_submit_button("🚀 Submit", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Run the agent
# ---------------------------------------------------------------------------
if submit:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY not found. Set it in your .env file or environment.")
        st.stop()

    if not user_query.strip():
        st.warning("Please enter a question.")
        st.stop()

    # Resolve the dropdown label to an internal intent code
    selected_intent = DROPDOWN_TO_INTENT.get(query_type)

    try:
        agent = InsuranceAgent(api_key=api_key, model=model)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    # Progress indicator while the pipeline runs
    with st.spinner("Agent is thinking…"):
        result = agent.run(user_query, selected_intent=selected_intent)

    if result.error:
        st.error(f"Agent encountered an error: {result.error}")

    # ── Agent Reasoning Steps ────────────────────────────────────
    with st.expander("🧠 Agent Reasoning Steps", expanded=True):
        for step in result.reasoning_steps:
            st.markdown(f"<div class='reasoning-step'>{step}</div>", unsafe_allow_html=True)

        if result.search_used and result.search_results:
            st.markdown("**Search Results Used:**")
            for i, sr in enumerate(result.search_results, 1):
                st.markdown(f"  {i}. **{sr['title']}** — {sr['snippet'][:120]}…")

    # ── Summary ──────────────────────────────────────────────────
    if result.summary:
        st.subheader("📌 Summary")
        st.info(result.summary)

    # ── Detailed Response ────────────────────────────────────────
    if result.detailed:
        st.subheader("📝 Detailed Analysis")
        st.markdown(result.detailed, unsafe_allow_html=True)
    elif result.response:
        # Fallback: show the full response if section parsing failed
        st.subheader("📝 Response")
        st.markdown(result.response, unsafe_allow_html=True)

    # ── Key Takeaways ────────────────────────────────────────────
    if result.takeaways:
        st.subheader("🎯 Key Takeaways")
        st.success(result.takeaways)

    # ── Meta footer ──────────────────────────────────────────────
    meta_cols = st.columns(3)
    meta_cols[0].metric("Intent", INTENT_LABELS.get(result.intent, result.intent))
    meta_cols[1].metric("Search Used", "Yes" if result.search_used else "No")
    meta_cols[2].metric("Sources", len(result.search_results))
