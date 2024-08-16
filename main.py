import sys
import pygame
import chess
import chess.svg
import io
from cairosvg import svg2png
from stockfish import Stockfish
import threading
from opening_selector import select_opening
from openings import openings
import random

# Initialize pygame
pygame.init()

# Select opening before loading the main game
selected_opening = select_opening(openings.keys())  # Choose from the available openings
opening_lines = openings[selected_opening]
selected_line = random.choice(opening_lines)  # Select one random line at the start
opening_moves = selected_line['moves']  # Get the moves of the selected line

# Load chessboard
board = chess.Board()

# Set up the display
board_size = 600  # Keep the board size fixed
extra_space = 150  # Add extra space at the bottom for information
size = (board_size, board_size + extra_space)
screen = pygame.display.set_mode(size, pygame.DOUBLEBUF)
pygame.display.set_caption('Chess Opening')

# Stockfish setup
stockfish_path = r"C:\Users\silvan.hegner\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"  # Set the correct path to your Stockfish binary
stockfish = Stockfish(stockfish_path)
stockfish.set_skill_level(7)  # You can adjust the skill level

# Use a consistent scaling factor for both margin and square size calculation
scaling_factor = 0.93  # Adjust this factor to align the board as needed

# Recalculate margin and square size
margin = (board_size - board_size * scaling_factor) / 2
square_size = (board_size * scaling_factor) / 8

white_eval = None
black_eval = None

def analyze_with_stockfish():
    global white_eval, black_eval
    stockfish.set_fen_position(board.fen())
    
    try:
        evaluation = stockfish.get_evaluation()
    except Exception as e:
        print(f"Error during Stockfish evaluation: {e}")
        evaluation = {'type': 'cp', 'value': 0}

    if 'type' in evaluation and evaluation['type'] == 'cp':
        white_eval = evaluation['value'] / 100.0
        black_eval = -white_eval
    elif 'type' in evaluation and evaluation['type'] == 'mate':
        if evaluation['value'] > 0:
            white_eval = f"M{evaluation['value']}"
            black_eval = f"M{-evaluation['value']}"
        else:
            white_eval = f"M{-evaluation['value']}"
            black_eval = f"M{evaluation['value']}"
    else:
        white_eval = 0.0  # Neutral value for initial load
        black_eval = 0.0

def analyze_with_stockfish_and_render():
    analyze_with_stockfish()
    global board_surface
    board_surface = render_board_surface()

def handle_stockfish_move():
    def move_and_evaluate():
        stockfish.set_fen_position(board.fen())
        best_move = stockfish.get_best_move()
        if best_move:
            board.push_uci(best_move)
            analyze_with_stockfish()

    # If it's black's turn, let Stockfish play in a separate thread
    if board.turn == chess.BLACK:
        threading.Thread(target=move_and_evaluate).start()

# Pre-render the board surface
def render_board_surface():
    svg_data = chess.svg.board(board, size=board_size, coordinates=True)
    png_data = svg2png(bytestring=svg_data.encode('utf-8'))
    image = pygame.image.load(io.BytesIO(png_data))
    return pygame.transform.scale(image, (int(board_size), int(board_size)))

board_surface = render_board_surface()

# Function to draw the board
def draw_board(selected_square=None, dragging_piece=None, mouse_pos=None, possible_moves=None):
    # Draw the cached board surface
    screen.blit(board_surface, (0, 0))

    # Draw possible moves if a square is selected
    if possible_moves is not None:
        for target_square in possible_moves:
            target_col = chess.square_file(target_square)
            target_row = 7 - chess.square_rank(target_square)
            center_x = int(margin + target_col * square_size + square_size / 2)
            center_y = int(margin + target_row * square_size + square_size / 2)
            pygame.draw.circle(screen, (128, 128, 128), (center_x, center_y), square_size // 6)

    if dragging_piece is not None and mouse_pos is not None:
       piece = board.piece_at(dragging_piece)
       if piece:
           piece_svg = chess.svg.piece(piece, size=square_size)
           piece_png = svg2png(bytestring=piece_svg.encode('utf-8'))
           piece_image = pygame.image.load(io.BytesIO(piece_png))
           piece_image = pygame.transform.scale(piece_image, (int(square_size), int(square_size)))
           screen.blit(piece_image, (mouse_pos[0] - square_size // 2, mouse_pos[1] - square_size // 2))

    # Add space for additional information at the bottom
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, board_size, size[0], extra_space))

    # Draw the evaluation bar
    eval_bar_height = 30  # Height of the evaluation bar
    eval_bar_width = board_size  # Full width of the board
    eval_bar_x = 0  # Start at the left edge
    eval_bar_y = board_size  # Position it just below the board 

    if white_eval is None:
        white_eval_value = 0.0
    else:
        white_eval_value = white_eval

    if isinstance(white_eval_value, str):
        if white_eval_value.startswith('M'):
            white_ratio = 1.0 if white_eval_value[1] == '-' else 0.0
        else:
            white_ratio = 0.5
    else:
        max_eval = 10
        min_eval = -10
        white_ratio = max(min((white_eval_value + max_eval) / (max_eval - min_eval), 1.0), 0.0)
    
    black_ratio = 1.0 - white_ratio

    # Draw white part of the bar
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(eval_bar_x, eval_bar_y, eval_bar_width * white_ratio, eval_bar_height))

    # Draw black part of the bar horizontally
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(eval_bar_x + eval_bar_width * white_ratio, eval_bar_y, eval_bar_width * black_ratio, eval_bar_height))

    # Draw the outline of the eval bar
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(eval_bar_x, eval_bar_y, eval_bar_width, eval_bar_height), 2)

    # Display the current opening and line
    font = pygame.font.Font(None, 20)
    current_line = selected_line['name']
    remaining_moves = len(opening_moves) - opening_index
    opening_text = f"Opening: {selected_opening} - {current_line} (Moves Left: {remaining_moves})"
    opening_surface = font.render(opening_text, True, (0, 0, 0))
    screen.blit(opening_surface, (10, board_size + eval_bar_height + 10))

    # Display important game information
    game_status_text = ""
    if board.is_checkmate():
        game_status_text = "Checkmate"
    elif board.is_check():
        game_status_text = "Check"
    elif board.is_stalemate():
        game_status_text = "Stalemate"

    if game_status_text:
        status_surface = font.render(game_status_text, True, (255, 0, 0))
        screen.blit(status_surface, (10, board_size + eval_bar_height + 50))

    pygame.display.flip()


# Initialize opening move index
opening_index = 0  # Index for the current move within the selected line 

# Main game loop
running = True
selected_square = None
dragging = False
dragged_piece = None
possible_moves = None

# Main game loop
running = True
selected_square = None
dragging = False
dragged_piece = None
possible_moves = None
board_needs_update = False

def process_player_move(uci_move):
    global opening_index, selected_square, possible_moves, board_surface
    
    # Check if we are still in the opening sequence
    if opening_index < len(selected_line['moves']):
        expected_move = selected_line['moves'][opening_index]

        # If the player's move matches the expected move in the opening sequence
        if uci_move == expected_move:
            board.push(chess.Move.from_uci(uci_move))
            opening_index += 1
            
            # Clear selection after a valid move
            selected_square = None
            possible_moves = None

            # Check if the opening sequence is finished
            if opening_index < len(selected_line['moves']):
                # Play the next move in the opening line automatically
                expected_move = selected_line['moves'][opening_index]
                board.push_uci(expected_move)
                opening_index += 1

                # Analyze the new position after the move in a separate thread
                threading.Thread(target=analyze_with_stockfish_and_render).start()
            else:
                # Opening sequence is finished, evaluate and re-render
                threading.Thread(target=analyze_with_stockfish_and_render).start()

                # If it's Black's turn, let Stockfish make a move immediately
                if board.turn == chess.BLACK:
                    best_move = stockfish.get_best_move()
                    if best_move:
                        board.push_uci(best_move)
                        threading.Thread(target=analyze_with_stockfish_and_render).start()
        else:
            print(f"Incorrect move. Expected: {expected_move}")
    else:
        # If the opening sequence is over, allow normal play
        if uci_move in [move.uci() for move in board.legal_moves]:
            board.push(chess.Move.from_uci(uci_move))
            threading.Thread(target=analyze_with_stockfish_and_render).start()
            # After White's move, let Stockfish (Black) play
            if board.turn == chess.BLACK:
                best_move = stockfish.get_best_move()
                if best_move:
                    board.push_uci(best_move)
                    threading.Thread(target=analyze_with_stockfish_and_render).start()

    # Clear selection and possible moves after processing any move
    selected_square = None
    possible_moves = None




dragging = False
clicking = False  # New flag to distinguish between clicking and dragging
dragged_piece = None
selected_square = None
possible_moves = None
click_start_pos = None

while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Start the click action
            x, y = event.pos
            if margin <= x < size[0] - margin and margin <= y < board_size - margin:
                col = int((x - margin) // square_size)
                row = int(7 - (y - margin) // square_size)
                square = chess.square(col, row)

                piece = board.piece_at(square)
                
                if piece is not None and piece.color == chess.WHITE and board.turn == chess.WHITE:
                    # If the clicked square has a piece, select it and show possible moves
                    selected_square = square
                    possible_moves = [move.to_square for move in board.legal_moves if move.from_square == selected_square]
                    clicking = True
                    click_start_pos = (x, y)
                elif selected_square is not None and square in possible_moves:
                    # If a piece is selected and the clicked square is a valid move, make the move
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        uci_move = move.uci()
                        process_player_move(uci_move)
                        selected_square = None
                        possible_moves = None
                else:
                    # Deselect if clicking on an empty square or invalid square
                    selected_square = None
                    possible_moves = None

        elif event.type == pygame.MOUSEMOTION:
            if clicking:
                # Detect if movement exceeds a threshold, then switch to dragging
                if click_start_pos and (abs(event.pos[0] - click_start_pos[0]) > 10 or abs(event.pos[1] - click_start_pos[1]) > 10):
                    dragging = True
                    dragged_piece = selected_square
                    clicking = False  # Cancel clicking when dragging starts

        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                # Calculate the destination square
                x, y = event.pos
                col = int((x - margin) // square_size)
                row = int(7 - (y - margin) // square_size)
                destination_square = chess.square(col, row)

                move = chess.Move(dragged_piece, destination_square)
                if move in board.legal_moves:
                    uci_move = move.uci()
                    process_player_move(uci_move)

                dragging = False
                dragged_piece = None

            elif clicking and selected_square is not None:
                # Handle click-to-move when releasing the mouse button
                x, y = event.pos
                col = int((x - margin) // square_size)
                row = int(7 - (y - margin) // square_size)
                target_square = chess.square(col, row)

                if target_square in possible_moves:
                    move = chess.Move(selected_square, target_square)
                    if move in board.legal_moves:
                        uci_move = move.uci()
                        process_player_move(uci_move)

            # Reset dragging and clicking state
            dragging = False
            clicking = False
            dragged_piece = None

    # Draw the board and any other UI elements
    draw_board(selected_square, dragged_piece, mouse_pos, possible_moves)

pygame.quit()