# Python Chess Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Library-Pygame-green.svg)](https://www.pygame.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A complete, modular chess engine and graphical interface developed from scratch in Python using Pygame. The project implements standard FIDE rules, strict move and check validation, a customizable chess clock system, and an Artificial Intelligence opponent powered by the Minimax algorithm with alpha-beta pruning and Piece-Square Tables.

Designed with clean software engineering principles in mind, it features strong separation of concerns, Object-Oriented Programming (OOP) paradigms, full state encapsulation for robust move undoing, and comprehensive Google-style documentation across all modules.

<p align="center">
  <img src="assets/demo/menu.png" width="48%" alt="Game mode selection menu" />
  <img src="assets/demo/gameplay.gif" width="48%" alt="Gameplay and coronation showcase" />
</p>

---

## Table of Contents

- [Key Features](#key-features)
- [Architecture & Modular Design](#architecture--modular-design)
- [Project Structure](#project-structure)
- [Prerequisites & Installation](#prerequisites--installation)
- [How to Play](#how-to-play)
- [AI Engine Details](#ai-engine-details)
- [Testing](#testing)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Key Features

- **FIDE Rules Implementation:**
  - Standard displacement and captures for all 6 piece types.
  - **Castling:** Kingside and queenside castling, ensuring neither king nor rook has moved and verifying the king does not start in check, pass through check, or land in check.
  - **En Passant:** Real-time square tracking for pawn double-steps and diagonal capture execution.
  - **Pawn Promotion:** Interactive selection modal allowing promotion to Queen, Rook, Bishop, or Knight.
- **Game State & Draw Detection:**
  - Check, Checkmate, and Stalemate are detected on the very move that causes them.
  - **50-Move Rule:** Automatic draw after 100 half-moves (50 moves per player) without pawn advances or captures.
  - **Threefold Repetition:** Automatic draw detection upon reaching identical board states three or more times under FIDE criteria.
  - **Insufficient Material:** Detection of automatic draws (K vs K, K+B vs K, K+N vs K).
  - Prevention of any move that places or leaves the player's own king in check.
- **Artificial Intelligence (Minimax + Alpha-Beta Pruning):**
  - Player vs Environment (PvE) game mode.
  - Heuristic positional scoring using **Piece-Square Tables (PST)** and piece material values.
  - Alpha-beta pruning with capture-first move ordering to minimize explored search branch space.
  - Checkmate-aware scoring: faster mates are preferred and stalemates score zero.
- **Robust Move History & Undo System:**
  - Atomic `make_move` / `undo_move` operations: each `Move` record captures the previous state *before* the move is applied, so any move (castling, en passant and promotion included) can be reverted exactly.
  - Multi-move undo capability (reverting both player and AI moves in PvE, or single turns in PvP) that completely restores board coordinates, captured pieces, moved flags, en passant targets, and clock states.
- **Clock & Timer System:**
  - Dedicated player timers with countdown updates, configurable base time, per-move increments, and timeout detection.
- **Verified Rules:** Move generation is validated against reference perft node counts (see [Testing](#testing)).
- **Retro-Styled Graphical User Interface:**
  - Rendered with Pygame, featuring square highlighting, custom pixel font typography (`PressStart2P`), interactive sidebar, scrollable move history log, and game-over dialog overlays.

---

## Architecture & Modular Design

The codebase adheres strictly to separation of concerns across 9 dedicated modules:

| Module | Responsibility |
|---|---|
| [`src/pieces.py`](src/pieces.py) | **Polymorphic Pieces:** Base `Piece` class and derived classes (`Pawn`, `Knight`, `Bishop`, `Rook`, `Queen`, `King`). Subclasses are mostly declarative (directions, sliding flag, value, Piece-Square Table); the shared move generation lives in `Piece`, and only `Pawn` and `King` (castling) extend it. |
| [`src/chessboard.py`](src/chessboard.py) | **Board Data Structure:** Encapsulates the 8x8 matrix, per-color piece tracking, king positions, and the en passant target. Executes and reverts moves (`make_move` / `undo_move`) including captures, castling, en passant and promotion. |
| [`src/game.py`](src/game.py) | **Game Rules Orchestrator:** Validates move legality against checks, manages turn alternation and clocks, tracks game-ending conditions (checkmate, stalemate, 50 moves, insufficient material, threefold repetition), and exposes `play_move` for validated moves plus `make_move` / `undo_move` for search. |
| [`src/move.py`](src/move.py) | **State Snapshot Model:** A dataclass capturing move coordinates, the moving piece, captured piece and square, castling rook move, promoted piece, and the previous en passant, moved-flag and clock values for exact undo reconstruction. |
| [`src/timers.py`](src/timers.py) | **Clock Management:** Implements countdown timers, per-move time increments, timestamp tracking, and formatted `MM:SS` display strings. |
| [`src/ai.py`](src/ai.py) | **Decision Engine:** A single recursive Minimax with alpha-beta pruning that returns both the score and the best move, plus heuristic evaluation combining material count with positional piece-square matrix weights. |
| [`src/gui.py`](src/gui.py) | **Presentation Layer:** Handles Pygame rendering, texture caching, board drawing, piece blitting, scrollable history tracking, promotion cards, and start menus. |
| [`src/utils.py`](src/utils.py) | **Notation Utilities:** Bidirectional conversions between algebraic chess notation (e.g., `'E4'`) and internal 0-indexed grid coordinates `(4, 4)` with strict validation. |
| [`src/main.py`](src/main.py) | **Application Controller:** `ChessApp` entry point wiring the game, the AI and the GUI: event dispatch (menu, promotion, sidebar, board), AI turns, clock checks, and the capped-FPS main loop. |

---

## Project Structure

```text
python-chess-engine/
├── assets/
│   ├── demo/               # Gameplay demonstrations and screenshots
│   │   ├── gameplay.gif
│   │   └── menu.png
│   ├── fonts/              # Custom typography
│   │   └── PressStart2P.ttf
│   └── images/             # High-resolution piece PNG textures
│       ├── BBishop.png, BKing.png, BKnight.png, ...
│       └── WBishop.png, WKing.png, WRook.png, ...
├── src/
│   ├── ai.py               # Minimax & alpha-beta engine
│   ├── chessboard.py       # 8x8 Grid and board state
│   ├── game.py             # Rule validation, turns & draws
│   ├── gui.py              # Pygame UI and event processing
│   ├── main.py             # Application entry point
│   ├── move.py             # Move dataclass and state snapshot
│   ├── pieces.py           # Piece hierarchy & PST tables
│   ├── test_perft.py       # Perft and game-flow tests
│   ├── timers.py           # Countdown clocks and increments
│   └── utils.py            # Algebraic coordinate conversions
├── LICENSE                 # MIT License
├── README.md               # Project documentation
├── pyproject.toml          # Project metadata and dependencies (uv)
└── uv.lock                 # Locked dependency versions (generated by `uv sync`)
```

---

## Prerequisites & Installation

### Requirements

- **Python:** 3.10 or higher (uv can install it for you)
- **[uv](https://docs.astral.sh/uv/):** package and environment manager
- **Pygame:** 2.5+ (installed automatically from `pyproject.toml`)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/samuelminambres/python-chess-engine.git
   cd python-chess-engine
   ```

2. **Install uv** (skip if you already have it; see the [uv docs](https://docs.astral.sh/uv/getting-started/installation/) for other methods):
   ```bash
   # macOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Windows (PowerShell)
   # powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Create the environment and install dependencies:**
   ```bash
   uv sync
   ```
   This creates a `.venv` folder, downloads a compatible Python if needed, and installs the exact versions pinned in `uv.lock`.

4. **Run the game:**
   ```bash
   uv run src/main.py
   ```

---

## How to Play

1. **Mode Selection:**
   - Launch the game to open the start menu. Choose between **vs AI** (single-player vs bot) or **1vs1** (local two-player).
2. **Making Moves:**
   - **Click** on a friendly piece to select it. The selected square will be highlighted in blue.
   - **Click** on a valid destination square to complete your move. If you click another friendly piece, the selection will switch to that piece.
3. **Pawn Promotion:**
   - When a pawn reaches the opposite back rank, a card menu will appear. Click on Queen, Rook, Bishop, or Knight to promote.
4. **Sidebar Controls:**
   - **Clock:** Displays the current player's remaining time.
   - **History:** Scroll through past moves using the mouse wheel.
   - **UNDO Button:** Reverts the last move (reverts 2 plies in AI mode to return to your turn, or 1 ply in 1v1 mode).
   - **RESTART Button:** Resets the board, timers, and history to start a new match.

---

## AI Engine Details

The bot uses the **Minimax** adversarial search algorithm enhanced with **Alpha-Beta Pruning**:

- **Search Depth:** Default search depth of 3 plies, configurable from 1 to 5 in `ChessAI`. Depth 3 answers almost instantly and depth 4 takes roughly a second on a typical machine; the search runs on the main thread, so the window is unresponsive while the bot thinks.
- **Terminal Positions:** Checkmate scores `±(10000 + remaining depth)` so the engine prefers the fastest mate; stalemate scores 0.
- **Move Ordering:** Captures are searched first to trigger earlier alpha-beta cutoffs.
- **Positional Evaluation:**
  Evaluates White material and square values minus Black material and square values:
  $$\text{Score} = \sum_{\text{White}} \left( \text{Value}(p) + \text{PST}(p, x, y) \right) - \sum_{\text{Black}} \left( \text{Value}(p) + \text{PST}(p, x, 7-y) \right)$$
- **Piece-Square Tables (PST):** Each piece type has tailored 8x8 matrices encouraging strategic fundamentals:
  - Pawns advancing towards promotion and controlling central squares.
  - Knights avoiding borders and dominating central outposts.
  - Kings castling and staying shielded behind pawn structures during the middlegame.

---

## Testing

`src/test_perft.py` uses only the standard library (`unittest`), so no extra test dependencies are needed. It checks:

- **Move generation** with [perft](https://www.chessprogramming.org/Perft) node counts up to depth 3 on four reference positions (the starting position, "Kiwipete", and two positions stressing en passant pins, promotions and castling rights).
- **Make/undo integrity:** exploring the whole move tree leaves the position, history and half-move clock untouched, and castling rights survive legal-move generation.
- **Game flow:** checkmate is reported on the mating move (Scholar's Mate), and the AI finds a mate in one without altering the game.

```bash
uv run python -m unittest discover -s src -v
```

---

## Future Improvements

- [ ] **Non-Blocking AI:** Run the search in a worker thread so the interface stays responsive at higher depths.
- [ ] **Bitboard Representation:** Accelerate move generation and bitwise operations to allow deeper search depths.
- [ ] **Transposition Tables & Zobrist Hashing:** Cache previously analyzed positions to prevent redundant evaluations.
- [ ] **FEN / PGN Support:** Import and export standard chess notation strings and complete game records.
- [ ] **Opening Book:** Integrate polyglot opening books for fast and varied opening play.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more information.
