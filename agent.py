"""
agent.py — Custom agentic loop for the Insurance AI Research Agent.

Implements a multi-step reasoning pipeline:
  1. Classify user intent
  2. Decide whether external search is needed
  3. (Optional) Generate a search query and retrieve results
  4. Synthesize a final structured response via the LLM

No external agent frameworks are used — the orchestration logic is explicit.
"""

import logging
import os
from dataclasses import dataclass, field

from openai import OpenAI

from prompts import (
    intent_classification_prompt,
    search_decision_prompt,
    search_query_prompt,
    synthesis_prompt,
    system_prompt,
)
from tools import format_search_results, search_web

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

INTENT_LABELS = {
    "QA": "General Q&A",
    "COMPARISON": "Compare Insurance",
    "RECOMMENDATION": "Policy Recommendation",
    "EXPLANATION": "Concept Explanation",
    "TREND": "Trend Analysis",
}

# Map dropdown selections back to internal labels
DROPDOWN_TO_INTENT = {v: k for k, v in INTENT_LABELS.items()}


@dataclass
class AgentResult:
    """Encapsulates every piece of output the agent produces."""
    response: str = ""
    summary: str = ""
    detailed: str = ""
    takeaways: str = ""
    intent: str = ""
    search_used: bool = False
    search_query: str = ""
    search_results: list[dict] = field(default_factory=list)
    reasoning_steps: list[str] = field(default_factory=list)
    error: str = ""


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class InsuranceAgent:
    """
    Custom agentic AI system for insurance research.

    Orchestrates intent detection → tool selection → LLM synthesis
    without relying on any external agent framework.
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        resolved_key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not resolved_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY or pass api_key."
            )
        self.client = OpenAI(api_key=resolved_key)
        self.model = model

    # ----- LLM helpers -----

    def _call_llm(self, user_msg: str, system_msg: str = "", temperature: float = 0.3) -> str:
        """Send a single request to the OpenAI chat completion endpoint."""
        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": user_msg})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    # ----- Pipeline steps -----

    def classify_intent(self, user_query: str) -> str:
        """Step 1 — determine the intent category."""
        raw = self._call_llm(intent_classification_prompt(user_query), temperature=0.0)
        # Normalize: take the first word and upper-case it
        label = raw.strip().split()[0].upper() if raw else "QA"
        if label not in INTENT_LABELS:
            label = "QA"
        return label

    def decide_search(self, user_query: str, intent: str) -> bool:
        """Step 2 — decide whether a web search is required."""
        raw = self._call_llm(
            search_decision_prompt(user_query, intent), temperature=0.0
        )
        return "SEARCH" in raw.upper() and "NO_SEARCH" not in raw.upper()

    def generate_search_query(self, user_query: str, intent: str) -> str:
        """Step 3a — create an optimised search query."""
        return self._call_llm(search_query_prompt(user_query, intent), temperature=0.0)

    def synthesize(self, user_query: str, intent: str, search_context: str) -> str:
        """Step 4 — produce the final structured answer."""
        return self._call_llm(
            synthesis_prompt(user_query, intent, search_context),
            system_msg=system_prompt(),
            temperature=0.4,
        )

    # ----- Main entry point -----

    def run(self, user_query: str, selected_intent: str | None = None) -> AgentResult:
        """
        Execute the full agent pipeline for a user query.

        Args:
            user_query: The natural-language question from the user.
            selected_intent: Optional pre-selected intent from the UI dropdown.
                             If provided, the classifier step is skipped.

        Returns:
            An AgentResult dataclass with all outputs and reasoning steps.
        """
        result = AgentResult()
        steps = result.reasoning_steps

        try:
            # ── Step 1: Intent classification ────────────────────────
            if selected_intent and selected_intent in INTENT_LABELS:
                result.intent = selected_intent
                steps.append(
                    f"✅ Intent provided by user: {INTENT_LABELS[selected_intent]}"
                )
            else:
                result.intent = self.classify_intent(user_query)
                steps.append(
                    f"🔍 Classified intent: {INTENT_LABELS[result.intent]}"
                )

            # ── Step 2: Search decision ──────────────────────────────
            needs_search = self.decide_search(user_query, result.intent)
            result.search_used = needs_search

            if needs_search:
                steps.append("🌐 Decision: Web search IS required for current data.")

                # ── Step 3: Search execution ─────────────────────────
                result.search_query = self.generate_search_query(
                    user_query, result.intent
                )
                steps.append(f"🔎 Generated search query: \"{result.search_query}\"")

                result.search_results = search_web(result.search_query)
                n = len(result.search_results)

                if n > 0:
                    steps.append(f"📄 Retrieved {n} search result(s).")
                else:
                    steps.append(
                        "⚠️ Search returned no results — proceeding with LLM knowledge."
                    )
            else:
                steps.append(
                    "📚 Decision: No search needed — answering from LLM knowledge."
                )

            # ── Step 4: Synthesis ────────────────────────────────────
            steps.append("🧠 Synthesizing final response…")

            search_context = format_search_results(result.search_results)
            full_response = self.synthesize(
                user_query, result.intent, search_context
            )
            result.response = full_response

            # ── Parse sections out of the markdown ───────────────────
            result.summary = _extract_section(full_response, "Summary")
            result.detailed = _extract_section(full_response, "Detailed Analysis")
            result.takeaways = _extract_section(full_response, "Key Takeaways")

            steps.append("✅ Response generated successfully.")

        except Exception as e:
            logger.exception("Agent pipeline error")
            result.error = str(e)
            steps.append(f"❌ Error: {e}")

        return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_section(text: str, heading: str) -> str:
    """
    Extract the content under a specific markdown ## heading.

    Returns everything between '## <heading>' and the next '##' or end-of-text.
    """
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    # Find the next ## heading (or end of string)
    end = text.find("\n## ", start)
    if end == -1:
        end = len(text)
    return text[start:end].strip()
