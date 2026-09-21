"""Minimal TypeSafe System One client. No SDK required.

One POST per item. Every question in a request is answered in that one call, so
batch questions per item rather than making a call per question.

Endpoint and shapes verified against https://docs.typesafe.ai/api.md on 2026-09-21.
"""
import json
import os
import time
import urllib.error
import urllib.request

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"


class JevError(RuntimeError):
    pass


def _key():
    k = os.environ.get("TYPESAFE_API_KEY")
    if not k:
        raise JevError(
            "TYPESAFE_API_KEY is not set. Export it before running this skill."
        )
    return k


def ask(state, questions, model=MODEL, retries=3, timeout=120):
    """Evaluate one state against a map of typed questions.

    state     -- str | dict | list, the thing being judged
    questions -- {id: {"type": "noul"|"choice"|"score",
                       "instructions": str|dict,
                       "criteria": ...}}

    Returns (answers, usage). `answers` is keyed by your question ids.
    Raises JevError after `retries` failed attempts.
    """
    body = json.dumps(
        {"state": state, "model": model, "questions": questions}
    ).encode()
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(
            ENDPOINT,
            data=body,
            headers={
                "Authorization": f"Bearer {_key()}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read())
            return d.get("answers", {}), d.get("usage", {})
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:400]
            # 4xx other than 429 is a bad request; retrying will not help.
            if e.code != 429 and 400 <= e.code < 500:
                raise JevError(f"HTTP {e.code}: {detail}") from e
            last = f"HTTP {e.code}: {detail}"
        except Exception as e:  # noqa: BLE001 - network shapes vary
            last = f"{type(e).__name__}: {e}"
        time.sleep(2 ** attempt)
    raise JevError(f"failed after {retries} attempts: {last}")


def value(answer, default=None):
    """Pull the scalar out of an answer, whatever its primitive.

    noul   -> {"type":"noul","noul":0.98}                     float 0..1
    choice -> {"type":"choice","choice":"a","confidence":..}  the chosen key
    score  -> {"type":"score","score":1.92,"legend":{..}}     probability-weighted
              level INDEX, 0..len(criteria)-1, not a 0..1 fraction
    """
    if not isinstance(answer, dict):
        return default
    for k in ("noul", "choice", "score", "value"):
        if k in answer:
            return answer[k]
    return default


def confidence(answer, default=None):
    if isinstance(answer, dict):
        for k in ("confidence", "certainty"):
            if k in answer:
                return answer[k]
    return default
