"""Curated chess endgame positions for study.

Each entry is a validated FEN plus a name, the solution move to recall,
and study notes. Positions are beginner-friendly and cover the most common
elementary endgames: king and queen vs king, king and rook vs king, king
and two bishops vs king, king and pawn vs king, rook-pawn endgames, and
bishop-and-knight vs king.

All FEN strings are validated at import time so a malformed position fails
fast instead of mid-study.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .fen import FENError, parse_fen

_RAW_POSITIONS = [
    {
        "name": "King and queen vs king",
        "fen": "4k3/8/8/8/8/8/8/4KQ2 w - - 0 1",
        "solution": "Qd2+",
        "notes": "Centralize the queen and use your king to support the mate.",
        "category": "Elementary checkmate",
    },
    {
        "name": "King and rook vs king",
        "fen": "4k3/8/8/8/8/8/8/4KR2 w - - 0 1",
        "solution": "Rd2+",
        "notes": "Use the rook to cut off the black king and bring your king up.",
        "category": "Elementary checkmate",
    },
    {
        "name": "King and two bishops vs king",
        "fen": "4k3/8/8/8/8/8/8/2BBK3 w - - 0 1",
        "solution": "Bd2",
        "notes": "Two bishops can force mate, but they need the king to help.",
        "category": "Elementary checkmate",
    },
    {
        "name": "King, bishop and knight vs king",
        "fen": "4k3/8/8/8/8/8/8/2BNK3 w - - 0 1",
        "solution": "Nf2",
        "notes": "The hardest elementary mate; coordinate all three pieces.",
        "category": "Elementary checkmate",
    },
    {
        "name": "King and pawn vs king",
        "fen": "4k3/8/8/8/8/4P3/4K3/8 w - - 0 1",
        "solution": "Ke3",
        "notes": "Take the opposition. The pawn queens if you keep the black king out.",
        "category": "Pawn endgame",
    },
    {
        "name": "Rook pawn endgame (Lucena-style)",
        "fen": "7k/P7/8/8/8/8/R7/K7 w - - 0 1",
        "solution": "Ra8+",
        "notes": "Build a bridge with the rook so the pawn can queen safely.",
        "category": "Rook endgame",
    },
]


@dataclass(frozen=True)
class EndgamePosition:
    """A single study position."""

    name: str
    fen: str
    solution: str
    notes: str
    category: str

    def __post_init__(self) -> None:
        parse_fen(self.fen)  # validate on construction


def _build() -> List[EndgamePosition]:
    positions: List[EndgamePosition] = []
    for entry in _RAW_POSITIONS:
        positions.append(
            EndgamePosition(
                name=entry["name"],
                fen=entry["fen"],
                solution=entry["solution"],
                notes=entry["notes"],
                category=entry["category"],
            )
        )
    return positions


POSITIONS: List[EndgamePosition] = _build()
BY_NAME: Dict[str, EndgamePosition] = {p.name: p for p in POSITIONS}


def list_endgames() -> List[EndgamePosition]:
    """Return all endgame positions in study order."""
    return list(POSITIONS)


def get_endgame(name: str) -> EndgamePosition:
    """Return a position by name, raising KeyError if unknown."""
    if name not in BY_NAME:
        raise KeyError(f"Unknown endgame: {name!r}")
    return BY_NAME[name]


def all_fens() -> List[str]:
    """Return the FEN string of every position."""
    return [p.fen for p in POSITIONS]
