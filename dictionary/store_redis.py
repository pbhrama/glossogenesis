import json
import os

import redis

from dictionary.store import Term


class RedisDictionaryStore:
    """
    Same interface as DictionaryStore (dictionary/store.py) but backed by ApsaraDB for
    Redis instead of a local JSON file -- for the cloud-deployed orchestrator running in
    Alibaba Cloud Function Compute. ApsaraDB for Redis speaks the standard Redis protocol,
    so this uses the plain `redis` package, no Alibaba-specific SDK required.

    Terms are stored as a single Redis hash (HSET), one field per term, JSON-encoded value.
    """

    def __init__(self, client: "redis.Redis", key: str = "glossogenesis:dictionary"):
        self.client = client
        self.key = key

    @classmethod
    def from_env(cls, key: str = "glossogenesis:dictionary") -> "RedisDictionaryStore":
        client = redis.Redis(
            host=os.environ["REDIS_HOST"],
            port=int(os.environ.get("REDIS_PORT", 6379)),
            password=os.environ.get("REDIS_PASSWORD") or None,
            db=int(os.environ.get("REDIS_DB", 0)),
            decode_responses=True,
            socket_connect_timeout=5,
        )
        return cls(client=client, key=key)

    @property
    def terms(self) -> dict:
        raw = self.client.hgetall(self.key)
        return {k: Term(**json.loads(v)) for k, v in raw.items()}

    def has(self, term: str) -> bool:
        return bool(self.client.hexists(self.key, term))

    def get(self, term: str):
        raw = self.client.hget(self.key, term)
        return Term(**json.loads(raw)) if raw else None

    def add(self, term: str, definition: str, coined_by: str, round_introduced: int) -> Term:
        entry = Term(term=term, definition=definition, coined_by=coined_by, round_introduced=round_introduced)
        self.client.hset(self.key, term, json.dumps(vars(entry)))
        return entry

    def as_prompt_block(self) -> str:
        terms = self.terms
        if not terms:
            return "(dictionary is empty)"
        lines = [f'- "{t.term}": {t.definition}' for t in terms.values()]
        return "\n".join(lines)
