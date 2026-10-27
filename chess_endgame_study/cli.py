"""Command-line interface for the chess endgame study tool."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .endgames import EndgamePosition, get_endgame, list_endgames
from .fen import FENError, fen_from_board, parse_fen
from .progress import DEFAULT_PROGRESS_FILE, PositionProgress, ProgressStore
from .quiz import render_board, run_quiz, select_positions


def _store_from_args(args: argparse.Namespace) -> ProgressStore:
    return ProgressStore(getattr(args, "progress_file", DEFAULT_PROGRESS_FILE))


def _print_position(pos: EndgamePosition) -> None:
    position = parse_fen(pos.fen)
    print(f"\n{pos.name} [{pos.category}]")
    print(f"FEN: {position.fen}")
    print(render_board(position))
    print(f"Solution: {pos.solution}")
    print(f"Notes: {pos.notes}")


def cmd_study(args: argparse.Namespace) -> int:
    store = _store_from_args(args)
    if args.name:
        try:
            pos = get_endgame(args.name)
        except KeyError as exc:
            print(f"Error: {exc}")
            print("Available: " + ", ".join(p.name for p in list_endgames()))
            return 1
        _print_position(pos)
        prog = store.get(pos.fen)
        if prog:
            print(f"Progress: {prog.correct}/{prog.attempts} correct "
                  f"({prog.accuracy:.0f}%), mastered={prog.mastered}")
        else:
            print("Progress: not yet studied")
    else:
        positions = list_endgames()
        print(f"{len(positions)} endgame positions available:")
        for pos in positions:
            prog = store.get(pos.fen)
            mark = "X" if (prog and prog.mastered) else " "
            print(f"  [{mark}] {pos.name}  [{pos.category}]")
    return 0


def cmd_quiz(args: argparse.Namespace) -> int:
    store = _store_from_args(args)
    summary = run_quiz(store, limit=args.limit,
                       include_mastered=args.include_mastered)
    print("\n" + "=" * 60)
    print(f"Quiz complete: {summary['correct']}/{summary['asked']} correct")
    return 0


def cmd_progress(args: argparse.Namespace) -> int:
    store = _store_from_args(args)
    progress = store.all_progress()
    if not progress:
        print("No progress recorded yet. Run 'study' or 'quiz' first.")
        return 0
    print(f"\nProgress file: {store.path}")
    print(f"{'Position':<32} {'Attempts':<9} {'Correct':<8} {'Accuracy':<9} {'Mastered'}")
    print("-" * 76)
    for key in sorted(progress, key=lambda k: progress[k].name.lower()):
        prog = progress[key]
        mastered = "yes" if prog.mastered else "no"
        print(f"{prog.name:<32} {prog.attempts:<9} {prog.correct:<8} "
              f"{prog.accuracy:<8.0f}% {mastered}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    store = _store_from_args(args)
    try:
        position = parse_fen(args.fen)
    except FENError as exc:
        print(f"Invalid FEN: {exc}")
        return 1
    progress = PositionProgress(fen=position.fen, name=args.name)
    store.upsert(progress)
    print(f"Added '{args.name}' to progress tracking.")
    print(f"FEN: {position.fen}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        position = parse_fen(args.fen)
    except FENError as exc:
        print(f"Invalid FEN: {exc}")
        return 1
    print("Valid FEN.")
    print(f"  Side to move: {'White' if position.side_to_move == 'w' else 'Black'}")
    print(f"  Castling: {position.castling or '-'}")
    print(f"  En passant: {position.en_passant or '-'}")
    print(f"  Halfmove clock: {position.halfmove_clock}")
    print(f"  Fullmove number: {position.fullmove_number}")
    print(f"  Occupied squares: {len(position.occupied())}")
    return 0


def cmd_rebuild(args: argparse.Namespace) -> int:
    """Rebuild a FEN from its components (round-trip check)."""
    # Minimal: accept a full FEN, re-emit it to confirm round-trip stability.
    try:
        position = parse_fen(args.fen)
    except FENError as exc:
        print(f"Invalid FEN: {exc}")
        return 1
    board = {sq: pc for sq, pc in position.board.items() if pc is not None}
    # Rebuild full board including empties for fen_from_board.
    full_board = {sq: position.board[sq] for sq in position.board}
    rebuilt = fen_from_board(
        full_board,
        side_to_move=position.side_to_move,
        castling=position.castling,
        en_passant=position.en_passant,
        halfmove_clock=position.halfmove_clock,
        fullmove_number=position.fullmove_number,
    )
    print(f"Original: {args.fen}")
    print(f"Rebuilt:  {rebuilt}")
    print("Round-trip stable." if rebuilt == args.fen else "Note: canonical spacing differs.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chess-endgame-study",
        description="Study chess endgames from FEN positions, track progress "
        "in local JSON, and quiz recall.",
    )
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("--progress-file", default=DEFAULT_PROGRESS_FILE,
                        help="Path to the local JSON progress file.")

    sub = parser.add_subparsers(dest="command", required=True)

    p_study = sub.add_parser("study", help="Show an endgame position.")
    p_study.add_argument("--name", help="Endgame name to study.")
    p_study.set_defaults(func=cmd_study)

    p_quiz = sub.add_parser("quiz", help="Quiz yourself on endgame recall.")
    p_quiz.add_argument("-n", "--limit", type=int, default=10,
                        help="Max number of questions.")
    p_quiz.add_argument("--include-mastered", action="store_true",
                        help="Include already-mastered positions.")
    p_quiz.set_defaults(func=cmd_quiz)

    p_progress = sub.add_parser("progress", help="Show study progress.")
    p_progress.set_defaults(func=cmd_progress)

    p_add = sub.add_parser("add", help="Track a custom FEN position.")
    p_add.add_argument("--fen", required=True, help="FEN string.")
    p_add.add_argument("--name", required=True, help="Position name.")
    p_add.set_defaults(func=cmd_add)

    p_validate = sub.add_parser("validate", help="Validate a FEN string.")
    p_validate.add_argument("fen", help="FEN string to validate.")
    p_validate.set_defaults(func=cmd_validate)

    p_rebuild = sub.add_parser("rebuild", help="Round-trip rebuild a FEN.")
    p_rebuild.add_argument("fen", help="FEN string to rebuild.")
    p_rebuild.set_defaults(func=cmd_rebuild)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
