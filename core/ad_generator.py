"""OpenAI-powered advertisement generation utilities."""
from __future__ import annotations

from typing import Iterable, List, Tuple

import asyncio
from openai import OpenAI

from config import api_keys
from utils.async_utils import gather_with_concurrency
from prompts.base_prompts import BASE_PROMPT
from prompts.tone_prompts import TONES

__all__ = ["generate_batch"]


def _build_prompt(name: str, description: str, tone: str) -> str:
    """Return a fully formatted prompt string in Georgian."""
    tone_descriptor = TONES.get(tone, tone)
    return BASE_PROMPT.format(name=name, description=description, tone=tone_descriptor)


async def _generate_single(name: str, description: str, tone: str, *, max_tokens: int, temperature: float, model: str) -> str:
    """Asynchronously call OpenAI chat completion and return advertisement text."""

    prompt = _build_prompt(name, description, tone)

    # Use `asyncio.to_thread` because client.chat.completions.create is blocking.
    def _call_api() -> str:
        client = OpenAI(api_key=api_keys.load_api_key())
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "შენ ხარ ქართველი მარკეტინგის ასისტენტი და კოპირაიტერი.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    return await asyncio.to_thread(_call_api)


def generate_batch(
    data_pairs: Iterable[Tuple[str, str]],
    tone: str,
    *,
    max_tokens: int,
    temperature: float,
    model: str,
    concurrency: int = 3,
) -> List[str]: 
    """Generate advertisement texts for a batch of *data_pairs*.

    Parameters
    ----------
    data_pairs : Iterable[Tuple[str, str]]
        Iterable of ``(product_name, product_description)`` pairs.
    tone : str
        Tone keyword present in ``prompts.tone_prompts.TONES``.
    concurrency : int, optional
        Maximum number of concurrent OpenAI requests, by default 3.
    """

    coroutines = [_generate_single(name, description, tone, max_tokens=max_tokens, temperature=temperature, model=model)
                  for name, description in data_pairs]
    return gather_with_concurrency(concurrency, coroutines)
