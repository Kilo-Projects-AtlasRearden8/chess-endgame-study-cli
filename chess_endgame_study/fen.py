"""Forsyth-Edwards Notation (FEN) parsing and validation.

A FEN string describes a single chess position using six fields:

    piece_placement active_color castling en_passant halfmove_clock fullmove_number

Example:

    rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

This module is dependency-free (stdlib only) and validates strictly so the
rest of the application never has to guess about malformed positions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

PIECES = frozenset("PNBRQKpnbrqk")
FILES = "abcdefgh"
RANKS = "12345678"


class FENError(ValueError):
    """Raised when a FEN string is malformed or invalid."""


@dataclass(frozen=True)
class FENPosition:
    """A parsed, validated chess position."""

    fen: str
    board: Dict[str, Optional[str]] = field(repr=False)
    side_to_move: str = ""
    castling: str = ""
    en_passant: Optional[str] = None
    halfmove_clock: int = 0
    fullmove_number: int = 1

    def piece_at(self, square: str) -> Optional[str]:
        """Return the piece on ``square`` (e.g. ``"e4"``), or None if empty."""
        return self.board.get(square)

    def occupied(self) -> Dict[str, str]:
        """Return only the occupied squares as {square: piece}."""
        return {sq: pc for sq, pc in self.board.items() if pc is not None}


def _parse_board(piece_placement: str) -> Dict[str, Optional[str]]:
    ranks = piece_placement.split("/")
    if len(ranks) != 8:
        raise FENError(
            f"piece placement must have 8 ranks, found {len(ranks)}"
        )

    board: Dict[str, Optional[str]] = {}
    # FEN ranks are given from rank 8 down to rank 1.
    for rank_index, rank in enumerate(ranks):
        rank_number = 8 - rank_index
        file_index = 0
        for ch in rank:
            if ch in PIECES:
                if file_index >= 8:
                    raise FENError(
                        f"rank {rank_number} has more than 8 squares"
                    )
                square = FILES[file_index] + str(rank_number)
                board[square] = ch
                file_index += 1
            elif ch in "12345678":
                file_index += int(ch)
            else:
                raise FENError(
                    f"invalid character {ch!r} in rank {rank_number}"
                )
        if file_index != 8:
            raise FENError(
                f"rank {rank_number} covers {file_index} squares, expected 8"
            )

    # Ensure every square exists on the board (empty squares default to None).
    for file_char in FILES:
        for rank_char in RANKS:
            board.setdefault(file_char + rank_char, None)
    return board


def _validate_castling(value: str) -> None:
    if value == "-":
        return
    allowed = frozenset("KQkq")
    seen = set()
    for ch in value:
        if ch not in allowed:
            raise FENError(f"invalid castling character {ch!r}")
        if ch in seen:
            raise FENError(f"duplicate castling right {ch!r}")
        seen.add(ch)


def _validate_en_passant(value: str) -> Optional[str]:
    if value == "-":
        return None
    if len(value) != 2:
        raise FENError(f"invalid en passant square {value!r}")
    file_char, rank_char = value[0], value[1]
    if file_char not in FILES or rank_char not in RANKS:
        raise FENError(f"invalid en passant square {value!r}")
    return value


def _validate_nonnegative_int(value: str, name: str) -> int:
    if not value.isdigit():
        raise FENError(f"{name} must be a non-negative integer, got {value!r}")
    return int(value)


def _validate_positive_int(value: str, name: str) -> int:
    if not value.isdigit() or int(value) < 1:
        raise FENError(f"{name} must be a positive integer, got {value!r}")
    return int(value)


def parse_fen(fen: str) -> FENPosition:
    """Parse and validate a FEN string.

    Raises:
        FENError: if the FEN is malformed.
    """
    if not isinstance(fen, str):
        raise FENError(f"FEN must be a string, got {type(fen).__name__}")

    fields = fen.split()
    if len(fields) != 6:
        raise FENError(
            f"FEN must have exactly 6 fields, found {len(fields)}: {fen!r}"
        )

    piece_placement, active_color, castling, en_passant, halfmove, fullmove = (
        fields
    )

    board = _parse_board(piece_placement)

    if active_color not in ("w", "b"):
        raise FENError(
            f"active color must be 'w' or 'b', got {active_color!r}"
        )
    _validate_castling(castling)
    ep = _validate_en_passant(en_passant)
    halfmove_clock = _validate_nonnegative_int(halfmove, "halfmove clock")
    fullmove_number = _validate_positive_int(fullmove, "fullmove number")

    return FENPosition(
        fen=fen,
        board=board,
        side_to_move=active_color,
        castling=castling,
        en_passant=ep,
        halfmove_clock=halfmove_clock,
        fullmove_number=fullmove_number,
    )


def fen_from_board(
    board: Dict[str, Optional[str]],
    side_to_move: str = "w",
    castling: str = "-",
    en_passant: Optional[str] = None,
    halfmove_clock: int = 0,
    fullmove_number: int = 1,
) -> str:
    """Build a FEN string from a board dict (inverse of parse_fen)."""
    if side_to_move not in ("w", "b"):
        raise FENError(
            f"active color must be 'w' or 'b', got {side_to_move!r}"
        )
    _validate_castling(castling)
    if en_passant is not None:
        _validate_en_passant(en_passant)
    if halfmove_clock < 0:
        raise FENError("halfmove clock must be non-negative")
    if fullmove_number < 1:
        raise FENError("fullmove number must be positive")

    ranks = []
    for rank_number in range(8, 0, -1):
        rank_chars = []
        empty_run = 0
        for file_char in FILES:
            piece = board.get(file_char + str(rank_number))
            if piece is None:
                empty_run += 1
            else:
                if empty_run:
                    rank_chars.append(str(empty_run))
                    empty_run = 0
                rank_chars.append(piece)
        if empty_run:
            rank_chars.append(str(empty_run))
        ranks.append("".join(rank_chars) if rank_chars else "8")

    ep_field = en_passant if en_passant is not None else "-"
    return (
        "/".join(ranks)
        + " "
        + side_to_move
        + " "
        + castling
        + " "
        + ep_field
        + " "
        + str(halfmove_clock)
        + " "
        + str(fullmove_number)
    )
