# Chess Endgame Study CLI

A local-first Python CLI for studying chess endgames from FEN positions,
tracking progress in a local JSON file, and quitting your recall with
spaced quizzes. No game assets, no accounts, no secrets, no network.

Built by **Dylan Asdale**, registered nurse turned AI author and founder of
**Asdale Dynamics, LLC** (Indiana, formed October 2026). Asdale Dynamics
publishes beginner-friendly AI education, books and guides, and practical
tools. This chess study tool is one of those practical, local-first apps.

The Massive AI Manual and hub site dylanasdale.github.io explain AI "like a
friend would": plain English, step by step, never condescending.

## What it does

- Parse and validate Forsyth–Edwards Notation (FEN) positions
- Study curated chess endgame positions (king and queen vs king, king and
  rook vs king, king and two bishops vs king, and more)
- Quiz recall of endgame solutions, with progress tracked in a local JSON
  file (no accounts, no cloud)
- Resume where you left off; positions you know well show up less often

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

Study an endgame position by name:

```bash
chess-endgame-study study --name "King and queen vs king"
```

Quiz yourself on recall:

```bash
chess-endgame-study quiz
```

Show your progress:

```bash
chess-endgame-study progress
```

Add a custom position:

```bash
chess-endgame-study add --fen "8/8/8/8/8/8/8/KQkq w - - 0 1" \
    --name "Custom position" --solution "Qa7#" --notes "My note"
```

Run without installing:

```bash
python3 -m chess_endgame_study.cli study --name "King and rook vs king"
```

Run the test suite:

```bash
python3 -m pytest
```

or, without pytest:

```bash
python3 -m unittest discover -s tests
```

## Data format

Progress is stored in `chess_endgame_study_progress.json` in the current
working directory. Each tracked position records attempts, correct and
incorrect counts, whether it is mastered, and the last attempt timestamp.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
