"""
Financial AI assistant powered by Perplexity Sonar API.
Handles prompt construction and LLM interaction.
"""

import os
from openai import OpenAI
from financial_analyzer import YearlyMetrics, build_context

PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
DEFAULT_MODEL = "sonar"

SYSTEM_PROMPT_TEMPLATE = """\
You are a precise financial analyst assistant. Your job is to answer questions \
about a company's financial performance based EXCLUSIVELY on the data provided below.

CRITICAL RULES:
1. NEVER invent, estimate, or assume any numbers not explicitly present in the data.
2. When you perform calculations, show the formula and the exact values used.
3. Always cite the specific year(s) and metric(s) you refer to.
4. Structure your answers clearly: lead with the direct answer, then provide supporting detail.
5. Respond in the same language the user writes in.
6. If a question cannot be answered from the available data, say so explicitly.

--- COMPANY FINANCIAL DATA (2005–2024) ---
{context}
--- END OF DATA ---
"""


class FinancialAssistant:
    def __init__(
        self,
        metrics: list[YearlyMetrics],
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
    ):
        self._model = model
        self._context = build_context(metrics)
        self._system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=self._context)
        self._history: list[dict] = []

        resolved_key = api_key or os.environ.get("PERPLEXITY_API_KEY")
        if not resolved_key:
            raise ValueError(
                "Perplexity API key is required. "
                "Set PERPLEXITY_API_KEY in your environment or pass api_key= explicitly."
            )
        self._client = OpenAI(api_key=resolved_key, base_url=PERPLEXITY_BASE_URL)

    def ask(self, question: str) -> str:
        """Send a question and return the assistant's answer. Maintains conversation history."""
        self._history.append({"role": "user", "content": question})

        messages = [{"role": "system", "content": self._system_prompt}] + self._history

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.2,   # low temperature — we want factual, grounded answers
        )

        answer = response.choices[0].message.content
        self._history.append({"role": "assistant", "content": answer})
        return answer

    def reset_history(self) -> None:
        """Clear conversation history (start a new session)."""
        self._history.clear()
