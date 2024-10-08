import pygame
import chess
import random
import threading
from stockfish import Stockfish
from opening_selector import select_opening
from openings import openings

# Initialize pygame
pygame.init()

# Board and screen configurations
BOARD_SIZE = 600  # Keep the board size fixed
EXTRA_SPACE = 150  # Add extra space at the bottom for information
SIZE = (BOARD_SIZE, BOARD_SIZE + EXTRA_SPACE)
SCALING_FACTOR = 0.93  # Adjust this factor to align the board as needed

# Calculate margin and square size
MARGIN = (BOARD_SIZE - BOARD_SIZE * SCALING_FACTOR) / 2
SQUARE_SIZE = (BOARD_SIZE * SCALING_FACTOR) / 8

# Stockfish configuration
STOCKFISH_PATH = r"path/to/stockfish"  # Set the correct path to your Stockfish binary
STOCKFISH_SKILL_LEVEL = 12  # You can adjust the skill level

# Select opening before loading the main game
SELECTED_OPENING = select_opening(openings.keys())  # Choose from the available openings
OPENING_LINES = openings[SELECTED_OPENING]
SELECTED_LINE = random.choice(OPENING_LINES)  # Select one random line at the start
OPENING_MOVES = SELECTED_LINE['moves']  # Get the moves of the selected line

# Thread lock for the chessboard
BOARD_LOCK = threading.RLock()

# Initialize Stockfish
stockfish = Stockfish(STOCKFISH_PATH)
stockfish.set_skill_level(STOCKFISH_SKILL_LEVEL)

# Initialize chessboard
board = chess.Board()
