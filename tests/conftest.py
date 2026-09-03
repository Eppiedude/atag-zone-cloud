"""Shared synthetic test helpers."""

from collections import deque

import pytest


class FakeResponse:
    def __init__(self, status, payload):
        self.status = status
        self.payload = payload

    async def json(self, content_type=None):
        return self.payload


class FakeSession:
    def __init__(self, *responses):
        self.responses = deque(responses)
        self.calls = []

    async def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.responses.popleft()


@pytest.fixture
def credentials():
    return ("user@example.com", "p@ss word&more", "YOUR_SYSTEM_ID")
