"""
prompts.py — Centralized prompt templates for the Insurance AI Research Agent.

Each function returns a formatted system or user prompt string
tailored to a specific intent classification or agent task.
"""


def system_prompt() -> str:
    """Master system prompt that defines the agent's persona and output rules."""
    return """You are an expert Insurance Research Agent. You provide accurate,
well-structured, and actionable information about insurance topics including
health, auto, home, life, and commercial insurance.

STRICT OUTPUT RULES — follow this structure for EVERY response:

## Summary
Provide a concise 2-3 sentence overview of your answer.

## Detailed Analysis
Provide a thorough, structured explanation. Use markdown formatting.
- For COMPARISONS: you MUST include a markdown table.
- For RECOMMENDATIONS: use a numbered or bulleted breakdown of factors.
- For TREND ANALYSIS: describe historical context, current state, and outlook.
- For EXPLANATIONS: use clear definitions, examples, and analogies.
- For Q&A: give a direct answer followed by supporting detail.

## Key Takeaways
Provide 3-5 bullet points summarizing the most important points.

IMPORTANT:
- If you lack exact data, clearly state your assumptions.
- Never fabricate statistics. Say "estimated" or "approximate" when uncertain.
- Cite search results when available.
- Be specific about states, policy types, and dollar amounts where possible.
"""


def intent_classification_prompt(user_query: str) -> str:
    """Prompt to classify user intent into one of five categories."""
    return f"""Classify the following user query into EXACTLY ONE of these categories:
- QA (general insurance question)
- COMPARISON (comparing policies, states, providers, or plans)
- RECOMMENDATION (asking for a policy or coverage suggestion)
- EXPLANATION (asking to explain a concept, term, or process)
- TREND (asking about trends, market changes, or risk factor analysis)

Respond with ONLY the category label (QA, COMPARISON, RECOMMENDATION, EXPLANATION, or TREND).
No other text.

User query: "{user_query}"
"""


def search_decision_prompt(user_query: str, intent: str) -> str:
    """Prompt to decide whether a web search is needed."""
    return f"""Given this user query and its classified intent, decide if a web search
is needed to answer it accurately.

A search IS needed when:
- The query asks about current rates, premiums, or prices
- The query compares data across states or providers
- The query involves recent trends, regulatory changes, or market data
- The query mentions specific years (especially current or recent)
- The query asks about specific companies or their current offerings

A search is NOT needed when:
- The query asks about general insurance concepts or definitions
- The query is about well-known insurance principles
- The query can be fully answered from general knowledge

Intent: {intent}
Query: "{user_query}"

Respond with ONLY "SEARCH" or "NO_SEARCH". No other text.
"""


def search_query_prompt(user_query: str, intent: str) -> str:
    """Generate an optimized search query for DuckDuckGo."""
    return f"""Generate a concise, effective web search query to find information for
the following insurance-related question. The search query should be optimized
for finding factual data, statistics, and current information.

Intent type: {intent}
User question: "{user_query}"

Respond with ONLY the search query string. No quotes, no explanation.
"""


def synthesis_prompt(user_query: str, intent: str, search_context: str) -> str:
    """Build the final synthesis prompt, optionally including search results."""
    context_block = ""
    if search_context:
        context_block = f"""
SEARCH RESULTS (use these to inform your answer — cite them where relevant):
{search_context}
"""

    intent_instructions = {
        "QA": "Provide a direct, factual answer with supporting details.",
        "COMPARISON": (
            "Structure your response as a detailed comparison. "
            "You MUST include a markdown table comparing the key dimensions."
        ),
        "RECOMMENDATION": (
            "Provide personalized policy recommendations with a clear "
            "bulleted breakdown of factors considered and why each recommendation fits."
        ),
        "EXPLANATION": (
            "Explain the concept clearly using definitions, real-world examples, "
            "and analogies. Assume the reader is not an insurance professional."
        ),
        "TREND": (
            "Analyze the trend with historical context, current data points, "
            "contributing factors, and a forward-looking outlook."
        ),
    }

    specific_instruction = intent_instructions.get(intent, intent_instructions["QA"])

    return f"""Answer the following insurance question.

INTENT: {intent}
SPECIFIC INSTRUCTION: {specific_instruction}
{context_block}
USER QUESTION: "{user_query}"

Remember to follow the strict output format: Summary → Detailed Analysis → Key Takeaways.
"""
