"""Async utility helpers for concurrent OpenAI requests."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Iterable, List, TypeVar

T = TypeVar("T")


async def _bounded_sem_task(semaphore: asyncio.Semaphore, coro: Awaitable[T]) -> T:
    async with semaphore:
        return await coro


def gather_with_concurrency(limit: int, coros: Iterable[Awaitable[T]]) -> List[T]:
    """Run awaitables with concurrency limit.

    Wrapper around `asyncio.run` for GUI-friendly usage.
    """
    async def _runner():
        sem = asyncio.Semaphore(limit)
        wrapped = [_bounded_sem_task(sem, c) for c in coros]
        return await asyncio.gather(*wrapped)

    return asyncio.run(_runner())
