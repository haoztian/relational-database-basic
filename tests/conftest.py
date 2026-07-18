"""Pytest configuration for smoke tests.

This file is mostly empty because smoke tests don't need fixtures.
Each script is self-contained: it creates its own engine, runs its SQL,
and cleans up when it finishes. We just import the script and let it run.

If you ever need to write more complex tests (integration tests, behavioral
tests), you would add fixtures here. For now, this file is a placeholder.
"""
