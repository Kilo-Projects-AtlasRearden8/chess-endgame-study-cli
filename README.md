# Chess Endgame Study CLI

A warm, local-first Python CLI for studying chess endgames from FEN
positions, tracking your progress in a local JSON file, and quizzing your
recall. No game assets, no accounts, no secrets, no network. Everything
stays on your machine.

Built by **Dylan Asdale**, registered nurse turned AI author and founder of
**Asdale Dynamics, LLC** (Indiana, formed October 2026). Asdale Dynamics
publishes beginner-friendly AI education, books and guides, and practical
tools that the LLC can share or sell. This chess study tool is one of those
practical, local-first apps — built to be clear, tested, and friendly to
beginners.

The Massive AI Manual and hub site dylanasdale.github.io explain AI "like a
friend would": plain English, step by step, never condescending. This tool
follows that same spirit.

## Who this is for

Anyone learning chess endgames who wants a simple, private way to practice:
- Beginners working through elementary mates (queen vs king, rook vs king,
  two bishops vs king, bishop and knight vs king)
- Players who want to track what they know and what still needs work
- Anyone who prefers local, account-free tools with no cloud and no tracking

## What it does

- **Parse and validate** Forsyth–Edwards Notation (FEN) positions, with
  clear error messages when a FEN is malformed
- **Study** six curated beginner endgame positions, each with an ASCII
  board, the solution move to recall, and plain-English notes
- **Quiz** your recall interactively; positions you know well show up less
  often, and weaker ones come up more
- **Track progress** in `chess_endgame_study_progress.json` (local JSON,
  gitignored) — attempts, correct/incorrect counts, accuracy, and mastery
- **Add** your own custom FEN position to track
- **Validate** any FEN string, or round-trip rebuild one to check it

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

List all available endgames:

```bash
chess-endgame-study study
```

Study one position (shows the board, solution, and notes):

```bash
chess-endgame-study study --name "King and queen vs king"
```

Quiz yourself on recall:

```bash
chess-endgame-study quiz
chess-endgame-study quiz -n 5        # fewer questions
chess-endgame-study quiz --include-mastered
```

Show your progress:

```bash
chess-endgame-study progress
```

Add a custom position to track:

```bash
chess-endgame-study add --fen "8/8/8/8/8/8/8/KQkq w - - 0 1" \
    --name "Custom position"
```

Validate a FEN string:

```bash
chess-endgame-study validate "4k3/8/8/8/8/8/8/4KQ2 w - - 0 1"
```

Run without installing:

```bash
python3 -m chess_endgame_study.cli study --name "King and rook vs king"
```

## Run the tests

```bash
python3 -m unittest discover -s tests
```

## Data format

Progress is stored in `chess_endgame_study_progress.json` in your current
working directory. Each tracked position records attempts, correct and
incorrect counts, accuracy, mastery, a correct-answer streak, and the last
attempt timestamp. A position is considered mastered after three correct
answers in a row; one wrong answer resets the streak.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
