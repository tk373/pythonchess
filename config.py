import chess
import random
import threading
from opening_selector import select_opening
from openings import openings
from stockfish_settings import get_stockfish_instance

# Board and screen configurations
BOARD_SIZE = 600  # Keep the board size fixed
EXTRA_SPACE = 150  # Add extra space at the bottom for information
SIZE = (BOARD_SIZE, BOARD_SIZE + EXTRA_SPACE)

# chess.svg.board() renders coordinates=True boards as a 15-unit margin plus
# eight 45-unit squares (390 units total), scaled to fit BOARD_SIZE. Mirroring
# that exact ratio here keeps mouse-to-square math pixel-aligned with what's
# actually drawn, instead of an eyeballed approximation.
_SVG_MARGIN = 15
_SVG_SQUARE = 45
_SVG_FULL_SIZE = 2 * _SVG_MARGIN + 8 * _SVG_SQUARE
MARGIN = BOARD_SIZE * _SVG_MARGIN / _SVG_FULL_SIZE
SQUARE_SIZE = BOARD_SIZE * _SVG_SQUARE / _SVG_FULL_SIZE

# Stockfish configuration
STOCKFISH_SKILL_LEVEL = 12  # You can adjust the skill level

# Select opening before loading the main game
SELECTED_OPENING = select_opening(openings.keys())  # Choose from the available openings
OPENING_LINES = openings[SELECTED_OPENING]
SELECTED_LINE = random.choice(OPENING_LINES)  # Select one random line at the start
OPENING_MOVES = openings  # Store all openings

# Thread lock for the chessboard
BOARD_LOCK = threading.RLock()

# Initialize Stockfish (prompts for the binary path on first run, then remembers it)
stockfish = get_stockfish_instance(STOCKFISH_SKILL_LEVEL)

# Initialize chessboard
board = chess.Board()
