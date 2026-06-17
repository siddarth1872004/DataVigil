"""
security/huggingface_guard.py — Hugging Face-powered prompt injection guard.

Uses a specialized text classification model (e.g. protectai/deberta-v3-base-prompt-injection-v2)
hosted on Hugging Face Serverless Inference to analyze the user's natural language input
for prompt injection attacks before passing it to any generative LLM nodes.
"""

import logging
from huggingface_hub import InferenceClient
from security.query_guard import QueryGuardError
import config

logger = logging.getLogger(__name__)


def huggingface_guard(query: str) -> None:
    """
    Check the user query for prompt injection using a Hugging Face text classification model.
    Raises QueryGuardError if a potential injection is detected.
    """
    if not config.HUGGINGFACE_API_KEY:
        logger.warning(
            "[huggingface_guard] HUGGINGFACE_API_KEY is not set. Skipping prompt injection check."
        )
        return

    logger.info("[huggingface_guard] Checking user query for prompt injection...")
    try:
        client = InferenceClient(token=config.HUGGINGFACE_API_KEY)
        res = client.text_classification(query, model=config.HF_INJECTION_MODEL)

        injection_score = 0.0
        for item in res:
            label = str(item.get("label", "")).upper()
            score = float(item.get("score", 0.0))
            # Handle standard labels like INJECTION, LABEL_1, etc.
            if "INJECTION" in label or label == "LABEL_1" or "MALICIOUS" in label:
                injection_score = max(injection_score, score)

        logger.info("[huggingface_guard] Injection check score: %.4f", injection_score)

        if injection_score > 0.70:
            logger.warning(
                "[huggingface_guard] Prompt injection blocked! Score: %.4f Query: '%s'",
                injection_score,
                query,
            )
            raise QueryGuardError(
                f"Possible prompt injection attempt detected (confidence: {injection_score:.2f}). "
                "Query blocked for security reasons."
            )
    except QueryGuardError:
        raise
    except Exception as exc:
        # Fail open with log alert in case Hugging Face API is down to preserve availability
        logger.warning(
            "[huggingface_guard] API call failed: %s. Skipping check to maintain service availability.",
            exc,
        )
