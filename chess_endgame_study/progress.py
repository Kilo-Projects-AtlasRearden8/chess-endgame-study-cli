"""Local JSON progress tracking for endgame study.

Progress is stored in a single JSON file next to the package. Each tracked
position records attempts, correct/incorrect counts, mastery state, and the
last attempt timestamp. No accounts, no cloud, no network.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

DEFAULT_PROGRESS_FILE = "chess_endgame_study_progress.json"


@dataclass
class PositionProgress:
    """Progress for a single endgame position."""

    fen: str
    name: str
    attempts: int = 0
    correct: int = 0
    incorrect: int = 0
    mastered: bool = False
    last_attempt: Optional[str] = None

    @property
    def accuracy(self) -> float:
        if self.attempts == 0:
            return 0.0
        return 100.0 * self.correct / self.attempts

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "PositionProgress":
        return PositionProgress(
            fen=data.get("fen", ""),
            name=data.get("name", ""),
            attempts=int(data.get("attempts", 0)),
            correct=int(data.get("correct", 0)),
            incorrect=int(data.get("incorrect", 0)),
            mastered=bool(data.get("mastered", False)),
            last_attempt=data.get("last_attempt"),
        )


class ProgressStore:
    """Thread-unsafe, single-process JSON store for study progress."""

    def __init__(self, path: str = DEFAULT_PROGRESS_FILE) -> None:
        self.path = path
        self._positions: Dict[str, PositionProgress] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
        except (json.JSONDecodeError, OSError):
            return
        if not isinstance(raw, dict):
            return
        for key, value in raw.items():
            if isinstance(value, dict):
                try:
                    self._positions[key] = PositionProgress.from_dict(value)
                except (TypeError, ValueError):
                    continue

    def _save(self) -> None:
        data = {key: pos.to_dict() for key, pos in self._positions.items()}
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
        os.replace(tmp, self.path)

    def _key(self, fen: str) -> str:
        return fen

    def get(self, fen: str) -> Optional[PositionProgress]:
        self._load()
        return self._positions.get(self._key(fen))

    def upsert(self, progress: PositionProgress) -> None:
        self._load()
        self._positions[self._key(progress.fen)] = progress
        self._save()

    def record_result(self, fen: str, name: str, correct: bool) -> PositionProgress:
        self._load()
        progress = self._positions.get(self._key(fen))
        if progress is None:
            progress = PositionProgress(fen=fen, name=name)
        progress.attempts += 1
        if correct:
            progress.correct += 1
        else:
            progress.incorrect += 1
        progress.last_attempt = datetime.now(timezone.utc).isoformat()
        # Mastered after 3 correct in a row with at least 3 attempts.
        if progress.attempts >= 3 and progress.correct >= 3 and progress.incorrect == 0:
            progress.mastered = True
        elif progress.incorrect > 0 and progress.correct < progress.attempts:
            progress.mastered = False
        self._positions[self._key(fen)] = progress
        self._save()
        return progress

    def all_progress(self) -> Dict[str, PositionProgress]:
        self._load()
        return dict(self._positions)

    def unmastered(self) -> Dict[str, PositionProgress]:
        self._load()
        return {
            key: pos for key, pos in self._positions.items() if not pos.mastered
        }

    def reset(self) -> None:
        self._load()
        self._positions.clear()
        self._save()
