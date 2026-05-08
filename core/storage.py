from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from core.constants import DATA_ROOT


class Storage:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or (DATA_ROOT / "cyberrecon.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                status TEXT NOT NULL,
                summary TEXT
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                module TEXT NOT NULL,
                title TEXT NOT NULL,
                severity TEXT NOT NULL,
                endpoint TEXT,
                score REAL,
                data TEXT,
                FOREIGN KEY(scan_id) REFERENCES scans(id)
            )
            """
        )
        self.conn.commit()

    def create_scan(self, target: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO scans(target, started_at, status, summary) VALUES (?, ?, ?, ?)",
            (target, datetime.utcnow().isoformat(), "running", ""),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def complete_scan(self, scan_id: int, summary: str) -> None:
        self.conn.execute(
            "UPDATE scans SET ended_at=?, status=?, summary=? WHERE id=?",
            (datetime.utcnow().isoformat(), "completed", summary, scan_id),
        )
        self.conn.commit()

    def add_finding(self, scan_id: int, finding: dict[str, Any]) -> None:
        self.conn.execute(
            "INSERT INTO findings(scan_id, module, title, severity, endpoint, score, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                scan_id,
                finding.get("module"),
                finding.get("title"),
                finding.get("severity"),
                finding.get("endpoint"),
                finding.get("score", 0),
                json.dumps(finding),
            ),
        )
        self.conn.commit()

    def recent_scans(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT id, target, started_at, ended_at, status, summary FROM scans ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            {
                "id": row[0],
                "target": row[1],
                "started_at": row[2],
                "ended_at": row[3],
                "status": row[4],
                "summary": row[5],
            }
            for row in rows
        ]

    def scan_findings(self, scan_id: int) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT data FROM findings WHERE scan_id = ? ORDER BY score DESC",
            (scan_id,),
        ).fetchall()
        return [json.loads(row[0]) for row in rows]
