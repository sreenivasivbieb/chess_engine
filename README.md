# Chess Engine with Alpha-Beta Pruning

A chess engine built in Python from scratch with minimax search, alpha-beta pruning, Zobrist hashing, transposition tables, and iterative deepening.

## Project Overview

This is my chess engine project that implements game tree search algorithms. The engine can search hundreds of thousands of positions per second and plays decent chess.

## Features

### Search Algorithm
- **Minimax with Alpha-Beta Pruning** - searches the game tree efficiently by cutting off bad branches
- **Iterative Deepening** - searches deeper and deeper until time runs out
- **Move Ordering** - looks at good moves first (captures, center control)

### Optimizations
- **Zobrist Hashing** - fast way to hash board positions
- **Transposition Tables** - remember positions we already evaluated
- **Piece-Square Tables** - bonus points for putting pieces in good squares

### Other Stuff
- Full move generation including castling and en passant
- Position evaluation (material + position)
- Benchmarks to test performance
- CLI to play against the engine

## Getting Started

### Requirements
- Python 3.7+
- No external libraries needed!

### How to Run

Just run:
```bash
python main.py
```

## Usage

### Playing Against the Engine

Run the main program and select option 1:
```bash
python main.py
```

Choose your color and difficulty level:
- **Easy**: Depth 3, 3 seconds per move
- **Medium**: Depth 4, 5 seconds per move  
- **Hard**: Depth 5, 8 seconds per move
- **Expert**: Depth 6, 15 seconds per move

Enter moves in algebraic notation (e.g., `e2e4`, `g1f3`). Type `legal` to see all legal moves or `quit` to exit.

### Running Benchmarks

Select option 3 from the main menu to run comprehensive performance benchmarks:
```bash
python benchmark.py
```

This will test:
- Search performance at various depths
- Transposition table effectiveness
- Move ordering and pruning efficiency
- Nodes per second throughput
- Iterative deepening behavior

### Engine vs Engine

Watch the engine play against itself by selecting option 2 from the main menu.

## Performance

Results on my machine:

- **Nodes Per Second**: 100k - 500k+ positions/second
- **Search Depth**: 5-6 moves ahead
- **Transposition Table Hit Rate**: 40-70%
- **Alpha-Beta Cutoff Rate**: 30-50%
- **Branching Factor**: reduced from ~35 to ~6

## Project Structure

```
chess-engine/
├── chess_board.py      # Board and move generation
├── evaluation.py       # Position evaluation
├── chess_engine.py     # Search algorithm
├── benchmark.py        # Performance tests
├── main.py            # CLI to play
└── README.md
```

### Core Components

#### ChessBoard (`chess_board.py`)
- 8x8 array-based board representation
- Complete move generation for all piece types
- Legal move validation (including check detection)
- Special move handling (castling, en passant, promotion)

#### Evaluator (`evaluation.py`)
- Material counting (pawn=100, knight=320, bishop=330, rook=500, queen=900)
- Piece-square tables for positional evaluation
- Mobility bonuses
- King safety evaluation
- Endgame detection and specialized king tables

#### ChessEngine (`chess_engine.py`)
- Minimax search with alpha-beta pruning
- Zobrist hashing for position identification
- Transposition table with replacement scheme
- Iterative deepening with time management
- Move ordering (captures, promotions, center control)

## 🧪 Testing

Run the benchmark suite to verify engine performance:
```bash
python benchmark.py
```

Expected output includes:
- Nodes searched at each depth
- Search time and nodes per second
- Transposition table statistics
- Alpha-beta pruning effectiveness
- Move ordering efficiency

## What I Learned

This project taught me about:
- Alpha-Beta Pruning - cuts search space in half
- Transposition Tables - cache to avoid recomputing positions
- Zobrist Hashing - fast position hashing
- Iterative Deepening - search deeper progressively
- Move Ordering - look at good moves first
- Piece-Square Tables - positional evaluation

Key results:
- Alpha-beta pruning reduces nodes from O(b^d) to O(b^(d/2))
- Transposition tables give 40-70% cache hit rate
- Move ordering boosts cutoffs from 0% to 30-50%
- Iterative deepening adds only ~10-15% overhead

## Customization

You can change engine strength in the code:
```python
# Make transposition table bigger
engine = ChessEngine(tt_size_mb=256)

# Search deeper
best_move, score = engine.search(board, max_depth=6, max_time=10.0)
```

Change piece values in `evaluation.py` if you want.

## Future Ideas

Things I might add later:
- Opening book
- Endgame tablebases
- Parallel search
- Better move ordering (killer moves, history)
- Null move pruning
- Quiescence search

## Note

This is a student project for learning about search algorithms and optimization. It's not going to beat Stockfish but it plays pretty decent chess!

Built with Python, no external libraries needed.
