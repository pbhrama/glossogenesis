import json
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Term:
    term: str
    definition: str
    coined_by: str
    round_introduced: int


@dataclass
class DictionaryStore:
    path: str
    terms: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: str) -> "DictionaryStore":
        if os.path.exists(path):
            with open(path) as f:
                raw = json.load(f)
            terms = {k: Term(**v) for k, v in raw.items()}
            return cls(path=path, terms=terms)
        return cls(path=path, terms={})

    def save(self) -> None:
        if not self.path:
            return  # in-memory only (e.g. a fresh per-run demo dictionary)
        raw = {k: vars(v) for k, v in self.terms.items()}
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(raw, f, indent=2)

    def has(self, term: str) -> bool:
        return term in self.terms

    def get(self, term: str) -> Optional[Term]:
        return self.terms.get(term)

    def add(self, term: str, definition: str, coined_by: str, round_introduced: int) -> Term:
        entry = Term(term=term, definition=definition, coined_by=coined_by, round_introduced=round_introduced)
        self.terms[term] = entry
        self.save()
        return entry

    def as_prompt_block(self) -> str:
        if not self.terms:
            return "(dictionary is empty)"
        lines = [f'- "{t.term}": {t.definition}' for t in self.terms.values()]
        return "\n".join(lines)
