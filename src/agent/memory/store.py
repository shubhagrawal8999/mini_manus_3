from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(slots=True)
class MemoryRecord:
    id: int
    user_id: str
    kind: str
    text: str
    vector: list[float]
    salience: float
    created_at: str


def _simple_embed(text: str, dim: int = 16) -> list[float]:
    vec = [0.0] * dim
    for i, ch in enumerate(text.lower()):
        vec[i % dim] += (ord(ch) % 97) / 97.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class MemoryStore:
    def __init__(self, db_path: str = "agent.db") -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                text TEXT NOT NULL,
                vector_json TEXT NOT NULL,
                salience REAL NOT NULL DEFAULT 0.5,
                created_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def add(self, user_id: str, kind: str, text: str, salience: float = 0.7) -> int:
        vector = _simple_embed(text)
        created_at = datetime.now(timezone.utc).isoformat()
        cur = self.conn.execute(
            "INSERT INTO memories(user_id, kind, text, vector_json, salience, created_at) VALUES(?,?,?,?,?,?)",
            (user_id, kind, text, json.dumps(vector), salience, created_at),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def retrieve(self, user_id: str, query: str, top_k: int = 5, kind: str | None = None) -> list[MemoryRecord]:
        qv = _simple_embed(query)
        params = [user_id]
        where = "WHERE user_id = ?"
        if kind:
            where += " AND kind = ?"
            params.append(kind)

        rows = self.conn.execute(
            f"SELECT * FROM memories {where} ORDER BY id DESC LIMIT 200", params
        ).fetchall()
        scored: list[tuple[float, sqlite3.Row]] = []
        for row in rows:
            vec = json.loads(row["vector_json"])
            sim = _cosine(qv, vec)
            score = 0.75 * sim + 0.25 * float(row["salience"])
            scored.append((score, row))
        scored.sort(key=lambda x: x[0], reverse=True)

        out: list[MemoryRecord] = []
        for _, row in scored[:top_k]:
            out.append(
                MemoryRecord(
                    id=int(row["id"]),
                    user_id=row["user_id"],
                    kind=row["kind"],
                    text=row["text"],
                    vector=json.loads(row["vector_json"]),
                    salience=float(row["salience"]),
                    created_at=row["created_at"],
                )
            )
        return out
