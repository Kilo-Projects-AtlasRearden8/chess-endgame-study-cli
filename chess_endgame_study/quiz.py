"""Quiz recall for endgame positions.

Presents a position (FEN + ASCII board), asks the player for the solution
move, checks it against the recorded solution, and writes the result to the
local JSON progress store.
"""

from __future__ import annotations

from typing import List, Optional

from .endgames import EndgamePosition, list_endgames
from .fen import FENPosition, parse_fen
from .progress import PositionProgress, ProgressStore

PIECE_SYMBOLS = {
    "K": "\u2654",
    "Q": "\u2655",
    "R": "\u2656",
    "B": "\u2657",
    "N": "\u2658",
    "P": "\u2659",
    "k": "\u265A",
    "q": "\u265B",
    "r": "\u265C",
    "b": "\u265D",
    "n": "\u265E",
    "p": "\u265F",
}

EMPTY = "\u25A1"  # white square placeholder for empty


def normalize_move(move: str) -> str:
    """Normalize a typed move for comparison (strip, uppercase)."""
    return move.strip().upper()


def render_board(position: FENPosition) -> str:
    """Render an ASCII board for a parsed position."""
    lines: List[str] = ["    a   b   c   d   e   f   g   h", "  +---+---+---+---+---+---+---+---+"]
    for rank_number in range(8, 0, -1):
        cells = []
        for file in "abcdefgh":
            piece = position.board.get(file + str(rank_number))
            cells.append(PIECE_SYMBOLS.get(piece, EMPTY))
        line = f"{rank_number} | " + " | ".join(cells) + " | " + f"{rank_number}"
        lines.append(line)
        lines.append("  +---+---+---+---+---+---+---+---+")
    lines.append("    a   b   c   d   e   f   g   h")
    side = "White" if position.side_to_move == "w" else "Black"
    lines.append(f"Side to move: {side}")
    return "\n".join(lines)


def select_positions(
    store: ProgressStore,
    limit: Optional[int] = None,
    include_mastered: bool = False,
) -> List[EndgamePosition]:
    """Pick positions to quiz, prioritizing unmastered and weak ones."""
    all_positions = list_endgames()
    progress = store.all_progress()

    def sort_key(pos: EndgamePosition):
        prog = progress.get(pos.fen)
        if prog is None:
            return (0, 0.0, 0)  # never studied: highest priority
        mastered = 0 if prog.mastered else 1
        # Lower accuracy and fewer attempts first.
        return (mastered, prog.accuracy, prog.attempts)

    unmastered = [p for p in all_positions if not progress.get(p.fen, PositionProgress(p.fen, p.name)).mastered]
    pool = unmastered if unmastered else all_positions
    if not include_mastered and unmastered:
        pool = unmastered
    pool_sorted = sorted(pool, key=sort_key)
    if limit is not None:
        pool_sorted = pool_sorted[:limit]
    return pool_sorted


def run_quiz(
    store: ProgressStore,
    limit: Optional[int] = 10,
    include_mastered: bool = False,
) -> dict:
    """Run an interactive quiz. Returns a summary dict."""
    positions = select_positions(store, limit=limit, include_mastered=include_mastered)
    if not positions:
        return {"asked": 0, "correct": 0, "incorrect": 0, "positions": []}

    correct = 0
    incorrect = 0
    results = []

    for index, pos in enumerate(positions, start=1):
        position = parse_fen(pos.fen)
        print("\n" + "=" * 60)
        print(f"Question {index} of {len(positions)}: {pos.name}")
        print(f"Category: {pos.category}")
        print(position.fen)
        print(render_board(position))
        answer = input("Best move? ").strip()
        normalized = normalize_move(answer)
        is_correct = normalized == normalize_move(pos.solution)
        prog = store.record_result(pos.fen, pos.name, is_correct)
        if is_correct:
            correct += 1
            print(f"Correct! The solution is {pos.solution}. "
                  f"Mastered: {prog.mastered}")
        else:
            incorrect += 1
            print(f"Incorrect. The solution is {pos.solution}.")
        print(f"Notes: {pos.notes}")
        print(f"Progress: {prog.correct}/{prog.attempts} correct "
              f"({prog.accuracy:.0f}%)")
        results.append({
            "name": pos.name,
            "fen": pos.fen,
            "answer": answer,
            "solution": pos.solution,
            "correct": is_correct,
        })

    return {
        "asked": len(positions),
        "correct": correct,
        "incorrect": incorrect,
        "positions": results,
    }
