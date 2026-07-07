# Chess Opening Trainer

This is a chess opening trainer that supports 4 openings with 5 lines each. After completing the openings, Stockfish takes over and plays against you at an ELO of about 1300.

## Features
- Interactive chess board with drag-and-drop piece movement
- Opening training with multiple variations
- Stockfish integration for post-opening play
- Real-time position evaluation
- Opening and line selection interface

## Requirements
- [uv](https://docs.astral.sh/uv/) (manages Python and dependencies)
- Stockfish chess engine (you need to provide the path to your Stockfish binary in config.py)

## Setup

1. Install dependencies (uv creates the virtual environment automatically):
```bash
uv sync
```

2. Edit `config.py` and set the path to your Stockfish binary:
```python
STOCKFISH_PATH = "/path/to/your/stockfish"
```

3. Run the program:
```bash
uv run python main.py
```

## Controls
- Click and drag pieces to move them
- Use the dropdown menus to select different openings and lines
- Click "Reset Position" to start over

## System Requirements
- For Ubuntu: No additional system packages required
- For macOS: No additional system packages required
- For Windows: No additional system packages required

The program now uses PyQt5 for the interface, which provides better cross-platform compatibility and performance compared to the previous Pygame implementation.

## Troubleshooting

### `qt.qpa.plugin: Could not find the Qt platform plugin "cocoa" in ""`

This means the `.venv`'s PyQt5 install is corrupted or partial (e.g. a plugin file like `libqcocoa.dylib` or `QtCore.abi3.so` is missing or was extracted inconsistently). Rebuild the virtual environment from scratch, bypassing uv's cache in case that's corrupted too:

```bash
rm -rf .venv
uv sync --reinstall --no-cache
```