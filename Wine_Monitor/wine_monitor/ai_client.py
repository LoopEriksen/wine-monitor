"""Client for communicating with the local AI wine‑expert server.

The server is expected to expose a JSON‑over‑HTTP endpoint that accepts a POST
request of the form ``{"question": "..."}`` and returns a JSON response
``{"answer": "..."}``.

The default URL points to ``http://127.0.0.1:5000/ask`` – this is the
endpoint that will be implemented on the Raspberry Pi in Phase 2.
"""

from __future__ import annotations

import json
import requests
from typing import Any

DEFAULT_URL = "http://127.0.0.1:5000/ask"

def query_ai(question: str, *, url: str = DEFAULT_URL, timeout: int = 10) -> str:
    """Send *question* to the AI server and return the answer.

    Parameters
    ----------
    question:
        The user's question.
    url:
        Endpoint of the AI server.
    timeout:
        Timeout for the HTTP request.

    Raises
    ------
    requests.RequestException
        If the HTTP request fails.
    ValueError
        If the response JSON does not contain the expected ``answer`` field.
    """

    payload = {"question": question}
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover – network errors
        raise requests.RequestException(f"Failed to reach AI server: {exc}")

    try:
        data: Any = resp.json()
    except ValueError as exc:  # pragma: no cover – invalid JSON
        raise ValueError(f"Non‑JSON response from AI server: {exc}")

    if "answer" not in data:
        raise ValueError("AI server response missing 'answer' field")
    return str(data["answer"])  # Ensure string

