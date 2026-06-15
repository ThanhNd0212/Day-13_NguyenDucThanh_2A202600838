"""YOUR mitigation + observability layer. The simulator calls mitigate() around the
opaque agent (a REAL LLM) for every request. This is the ONLY place observability can
live -- the agent is silent. Legal moves: retry / cache / route / guardrail / sanitize
/ fallback / session-reset / PROMPT ROUTING, plus your own logging/tracing/metrics.
Illegal: hardcoding answers, importing the agent internals, reading instructor files,
network exfiltration.

  call_next(question, config) -> result   # the only way to reach the black box
  context = {"session_id","turn_index","qid","cache": <shared dict>, "cache_lock": <Lock>}
  result  = {"answer","status","steps","trace","meta":{latency_ms,usage,...}}

PROMPT ROUTING: you can override the agent's system prompt PER REQUEST by setting it in
the config you pass to call_next, e.g.:
    conf = dict(config); conf["system_prompt"] = my_better_prompt
    result = call_next(question, conf)
(Or just edit solution/prompt.txt for a single static prompt used on every request.)
"""
from __future__ import annotations
import re


_PII_PATTERNS = [
    re.compile(r'\b[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}\b'),      # email
    re.compile(r'\b(?:\+84|0)\d{9,10}\b'),                   # phone VN
]


def _strip_pii(text: str) -> str:
    for pat in _PII_PATTERNS:
        text = pat.sub('', text)
    return ' '.join(text.split())


def mitigate(call_next, question, config, context):
    clean_q = _strip_pii(question)

    # Try with current config (self_consistency=2 for correctness)
    for _ in range(2):
        result = call_next(clean_q, config)
        if result.get("answer") is not None:
            return result
        if result.get("status") != "ok":
            return result

    # Fall back to self_consistency=1 to resolve null from disagreement
    conf1 = dict(config)
    conf1["self_consistency"] = 1
    return call_next(clean_q, conf1)
