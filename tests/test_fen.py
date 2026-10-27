"""Tests for FEN parsing and validation (chess_endgame_study.fen)."""

import unittest

from chess_endgame_study.fen import (
    FENError,
    FENPosition,
    fen_from_board,
    parse_fen,
)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class TestParseValid(unittest.TestCase):
    def test_start_position(self):
        pos = parse_fen(START_FEN)
        self.assertIsInstance(pos, FENPosition)
        self.assertEqual(pos.fen, START_FEN)
        self.assertEqual(pos.side_to_move, "w")
        self.assertEqual(pos.castling, "KQkq")
        self.assertIsNone(pos.en_passant)
        self.assertEqual(pos.halfmove_clock, 0)
        self.assertEqual(pos.fullmove_number, 1)
        self.assertEqual(pos.piece_at("e1"), "K")
        self.assertEqual(pos.piece_at("e8"), "k")
        self.assertIsNone(pos.piece_at("d4"))

    def test_black_to_move(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
        pos = parse_fen(fen)
        self.assertEqual(pos.side_to_move, "b")

    def test_castling_variants(self):
        for castling in ("KQkq", "K", "q", "-", "KQ"):
            fen = f"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w {castling} - 0 1"
            pos = parse_fen(fen)
            self.assertEqual(pos.castling, castling)

    def test_en_passant(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq e3 0 1"
        pos = parse_fen(fen)
        self.assertEqual(pos.en_passant, "e3")

    def test_endgame_fens_parse(self):
        fens = [
            "4k3/8/8/8/8/8/8/4KQ2 w - - 0 1",
            "4k3/8/8/8/8/8/8/4KR2 w - - 0 1",
            "4k3/8/8/8/8/8/8/2BBK3 w - - 0 1",
            "4k3/8/8/8/8/8/8/2BNK3 w - - 0 1",
            "4k3/8/8/8/8/4P3/4K3/8 w - - 0 1",
            "7k/P7/8/8/8/8/R7/K7 w - - 0 1",
        ]
        for fen in fens:
            with self.subTest(fen=fen):
                pos = parse_fen(fen)
                self.assertEqual(pos.fen, fen)

    def test_occupied(self):
        pos = parse_fen(START_FEN)
        occupied = pos.occupied()
        self.assertEqual(len(occupied), 32)
        self.assertEqual(occupied["a1"], "R")


class TestRoundTrip(unittest.TestCase):
    def test_parse_then_rebuild_matches(self):
        fens = [START_FEN] + [
            "4k3/8/8/8/8/8/8/4KQ2 w - - 0 1",
            "7k/P7/8/8/8/8/R7/K7 w - - 0 1",
        ]
        for fen in fens:
            with self.subTest(fen=fen):
                pos = parse_fen(fen)
                full_board = {sq: pos.board[sq] for sq in pos.board}
                rebuilt = fen_from_board(
                    full_board,
                    side_to_move=pos.side_to_move,
                    castling=pos.castling,
                    en_passant=pos.en_passant,
                    halfmove_clock=pos.halfmove_clock,
                    fullmove_number=pos.fullmove_number,
                )
                self.assertEqual(rebuilt, fen)


class TestParseInvalid(unittest.TestCase):
    def assert_invalid(self, fen):
        with self.assertRaises(FENError):
            parse_fen(fen)

    def test_not_string(self):
        with self.assertRaises(FENError):
            parse_fen(None)  # type: ignore[arg-type]

    def test_wrong_field_count(self):
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0")
        self.assert_invalid("rnbqkbnr pppppppp 8 8 8 8 PPPPPPPP RNBQKBNR w KQkq - 0 1")

    def test_not_8_ranks(self):
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 extra")
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP w KQkq - 0 1")

    def test_rank_not_8_squares(self):
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPP/RNBQKBNR w KQkq - 0 1")

    def test_invalid_piece_character(self):
        self.assert_invalid("Xnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def test_bad_active_color(self):
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR x KQkq - 0 1")

    def test_bad_castling_char(self):
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkx - 0 1")

    def test_duplicate_castling(self):
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KK - 0 1")

    def test_bad_en_passant(self):
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq i3 0 1")
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq e9 0 1")

    def test_halfmove_not_digit(self):
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - -1 1")
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - ab 1")

    def test_fullmove_zero(self):
        self.assert_invalid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0")


if __name__ == "__main__":
    unittest.main()
