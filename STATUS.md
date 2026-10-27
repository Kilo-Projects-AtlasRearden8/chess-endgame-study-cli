# STATUS

## What was built

A local-first Python CLI for studying chess endgames from FEN positions,
tracking progress in a local JSON file, and quizzing recall. No game
assets, no accounts, no network, no secrets.

Built for Dylan Asdale / Asdale Dynamics, LLC (Indiana, formed October
2026). Credit: Asdale Dynamics, LLC. Licensed under the MIT License
(Copyright (c) 2026 Asdale Dynamics, LLC).

## What it does

- Parses and validates Forsyth-Edwards Notation (FEN) positions strictly
  (6 fields, 8 ranks of 8 squares, valid pieces, active color, castling,
  en passant, halfmove clock, fullmove number).
- Ships 6 curated beginner endgame positions: king and queen vs king,
  king and rook vs king, king and two bishops vs king, king, bishop and
  knight vs king, king and pawn vs king, and a Lucena-style rook pawn
  endgame. Each has a name, solution move to recall, and study notes.
- `study` shows a position with an ASCII board, solution, and notes.
- `quiz` runs an interactive recall quiz, prioritizing unmastered and
  weaker positions, and records results.
- `progress` shows attempts, correct/incorrect counts, accuracy, and
  mastery per position.
- `add` tracks a custom FEN position; `validate` and `rebuild` check
  FEN validity and round-trip stability.
- Progress is stored in `chess_endgame_study_progress.json` in the
  current working directory (local JSON, gitignored).

## Project layout

```
chess_endgame_study/   package
  __init__.py          version
  cli.py               argparse CLI (main entry point)
  fen.py               FEN parsing and validation
  progress.py          local JSON progress store
  quiz.py              quiz recall and board rendering
  endgames.py          curated endgame position database
tests/
  test_fen.py          18 tests for FEN parsing/validation
LICENSE                MIT License, Copyright (c) 2026 Asdale Dynamics, LLC
README.md              usage and credits (credits Asdale Dynamics, LLC)
pyproject.toml         packaging + console script entry point
.gitignore
STATUS.md              this file
```

## How to run it

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode (provides the `chess-endgame-study` command)
pip install -e .

# List available endgames
chess-endgame-study study

# Study one position
chess-endgame-study study --name "King and queen vs king"

# Run a recall quiz (10 questions by default)
chess-endgame-study quiz
chess-endgame-study quiz -n 5

# Show progress
chess-endgame-study progress

# Validate a FEN
chess-endgame-study validate "4k3/8/8/8/8/8/8/4KQ2 w - - 0 1"

# Run without installing
python3 -m chess_endgame_study.cli study --name "King and rook vs king"

# Run the test suite
python3 -m unittest discover -s tests
```

## Verification results

- Python 3.13.5
- `python3 -m unittest discover -s tests`: 18 tests, OK (exit 0)
  - 12 valid-FEN tests (start position, black to move, castling variants,
    en passant, all 6 shipped endgame FENs, occupied squares)
  - 3 round-trip tests (parse then rebuild matches the original FEN)
  - 3 invalid-input tests (not a string, wrong field count, ... plus 8 more
    invalid cases: rank count, rank width, bad piece, bad active color,
    bad castling char, duplicate castling, bad en passant, bad halfmove,
    fullmove zero)
- All shipped endgame FENs parse and validate on import.
- CLI verified manually: `study`, `study --name`, `quiz` (with piped
  input), `progress`, `add`, `validate` (valid and invalid), `--help`,
  `--version` all run without errors.

## Known gaps

- Move validation is recall-based (the user types the solution move; it is
  compared to the annotated solution). No SAN/legal-move engine is
  included, so any reasonable answer string is accepted as long as it
  matches the stored solution exactly (case-insensitive).
- Quiz selection is simple (unmastered first, then by accuracy/attempts);
  it is not a full spaced-repetition algorithm.
- Positions are fixed at ship time; `add` tracks a custom FEN for progress
  only (it is not added to the curated endgame list).
- Pure standard library; no external dependencies and no packaging of test
  data beyond the source tree.
- Unicode chess symbols are used for board rendering; rendering depends on
  terminal font support.
