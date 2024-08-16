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
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Chess Opening')

# Stockfish setup
stockfish_path = r"C:\Users\silvan.hegner\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"  # Set the correct path to your Stockfish binary
stockfish = Stockfish(stockfish_path)
stockfish.set_skill_level(8)  # You can adjust the skill level

# Calculate square size based on the board size (assuming 5% margin for the coordinates)
margin = (board_size - board_size * 0.95) / 2
square_size = board_size * 0.95 // 8

white_eval = None
black_eval = None

def analyze_with_stockfish():
    global white_eval, black_eval
    stockfish.set_fen_position(board.fen())
    evaluation = stockfish.get_evaluation()

    if evaluation['type'] == 'cp':
        white_eval = evaluation['value'] / 100.0
        black_eval = -white_eval
    elif evaluation['type'] == 'mate':
        if evaluation['value'] > 0:
            white_eval = f"M{evaluation['value']}"
            black_eval = f"M{-evaluation['value']}"
        else:
            white_eval = f"M{-evaluation['value']}"
            black_eval = f"M{evaluation['value']}"
    else:
        white_eval = 0.0  # Neutral value for initial load
        black_eval = 0.0

    # Log the evaluation
    print(f"Stockfish Evaluation: White: {white_eval}, Black: {black_eval}")

def analyze_position():
    # Run the evaluation in a separate thread
    threading.Thread(target=analyze_with_stockfish).start()

# Function to draw the board
def draw_board(selected_square=None, dragging_piece=None, mouse_pos=None, possible_moves=None, next_move_hint=None):
    # Convert SVG to PNG and load it into pygame
    svg_data = chess.svg.board(board, size=board_size, coordinates=True)
    png_data = svg2png(bytestring=svg_data.encode('utf-8'))
    image = pygame.image.load(io.BytesIO(png_data))

    # Scale and draw the image to the screen
    image = pygame.transform.scale(image, (int(board_size), int(board_size)))
    screen.blit(image, (0, 0))

    # Draw possible moves if a square is selected
    if possible_moves is not None:
        for target_square in possible_moves:
            target_col = chess.square_file(target_square)
            target_row = 7 - chess.square_rank(target_square)
            center_x = int(margin + target_col * square_size + square_size / 2)
            center_y = int(margin + target_row * square_size + square_size / 2)
            pygame.draw.circle(screen, (128, 128, 128), (center_x, center_y), square_size // 6)

    # Draw the dragging piece if dragging
    if dragging_piece is not None and mouse_pos is not None:
        piece = board.piece_at(dragging_piece)
        if piece:
            piece_svg = chess.svg.piece(piece, size=square_size)
            piece_png = svg2png(bytestring=piece_svg.encode('utf-8'))
            piece_image = pygame.image.load(io.BytesIO(piece_png))
            piece_image = pygame.transform.scale(piece_image, (square_size, square_size))
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

while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if margin <= x < size[0] - margin and margin <= y < board_size - margin:
                col = int((x - margin) * 8 // board_size)
                row = int(7 - (y - margin) * 8 // board_size)
                square = chess.square(col, row)
                
                if possible_moves and square in possible_moves:
                    move = chess.Move(selected_square, square)
                    if move:
                        uci_move = move.uci()
                        if board.turn == chess.WHITE:
                            # Stick to the selected line throughout the opening sequence
                            if opening_index < len(selected_line['moves']):
                                if uci_move == selected_line['moves'][opening_index]:
                                    board.push(move)
                                    opening_index += 1
                                    selected_square = None
                                    possible_moves = None  # Reset possible moves after a successful move

                                    # Call the threaded analysis
                                    analyze_position()

                                    # Handle Stockfish's response if within the opening line
                                    if board.turn == chess.BLACK and opening_index < len(selected_line['moves']):
                                        expected_move = selected_line['moves'][opening_index]
                                        board.push_uci(expected_move)
                                        opening_index += 1
                                        # Call the threaded analysis
                                        analyze_position()
                                    elif board.turn == chess.BLACK and opening_index >= len(selected_line['moves']):
                                        # If the opening sequence is over, let Stockfish take over
                                        stockfish.set_fen_position(board.fen())
                                        best_move = stockfish.get_best_move()
                                        board.push_uci(best_move)
                                        # Call the threaded analysis
                                        analyze_position()
                                else:
                                    print("Incorrect move for the opening. Expected move:", selected_line['moves'][opening_index])
                                    # Reset the selection
                                    selected_square = None
                                    possible_moves = None
                            else:
                                # Opening sequence is done, transition to normal gameplay
                                board.push(move)
                                selected_square = None
                                possible_moves = None  # Reset possible moves after a successful move
                                # Call the threaded analysis
                                analyze_position()

                                if board.turn == chess.BLACK:
                                    stockfish.set_fen_position(board.fen())
                                    best_move = stockfish.get_best_move()
                                    board.push_uci(best_move)
                                    # Call the threaded analysis
                                    analyze_position()
                    else:
                        # If move was not legal or something went wrong
                        selected_square = None
                        possible_moves = None
                elif board.piece_at(square) is not None:
                    if board.piece_at(square).color == chess.WHITE and board.turn == chess.WHITE:
                        dragging = True
                        dragged_piece = square
                        selected_square = square
                        # Calculate possible moves for the selected piece
                        possible_moves = [move.to_square for move in board.legal_moves if move.from_square == selected_square]
                else:
                    selected_square = None
                    possible_moves = None
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                x, y = event.pos
                col = int((x - margin) * 8 // board_size)
                row = int(7 - (y - margin) * 8 // board_size)
                square = chess.square(col, row)
                if square == dragged_piece:
                    # Retain the selected square and show possible moves
                    selected_square = square
                else:
                    move = chess.Move(dragged_piece, square)
                    if move:
                        uci_move = move.uci()
                        if move in board.legal_moves:
                            if board.turn == chess.WHITE:
                                # Stick to the selected line throughout the opening sequence
                                if opening_index < len(selected_line['moves']):
                                    if uci_move == selected_line['moves'][opening_index]:
                                        board.push(move)
                                        opening_index += 1
                                        selected_square = None
                                        possible_moves = None  # Reset possible moves after a successful move

                                        # Call the threaded analysis
                                        analyze_position()

                                        # Handle Stockfish's response
                                        if board.turn == chess.BLACK and opening_index < len(selected_line['moves']):
                                            expected_move = selected_line['moves'][opening_index]
                                            board.push_uci(expected_move)
                                            opening_index += 1
                                            # Call the threaded analysis
                                            analyze_position()
                                        elif board.turn == chess.BLACK and opening_index >= len(selected_line['moves']):
                                            # If the opening sequence is over, let Stockfish take over
                                            stockfish.set_fen_position(board.fen())
                                            best_move = stockfish.get_best_move()
                                            board.push_uci(best_move)
                                            # Call the threaded analysis
                                            analyze_position()
                                    else:
                                        print("Incorrect move for the opening. Expected move:", selected_line['moves'][opening_index])
                                        # Reset the selection
                                        selected_square = None
                                        possible_moves = None
                                else:
                                    # Opening sequence is done, transition to normal gameplay
                                    board.push(move)
                                    selected_square = None
                                    possible_moves = None  # Reset possible moves after a successful move
                                    # Call the threaded analysis
                                    analyze_position()

                                    if board.turn == chess.BLACK:
                                        stockfish.set_fen_position(board.fen())
                                        best_move = stockfish.get_best_move()
                                        board.push_uci(best_move)
                                        # Call the threaded analysis
                                        analyze_position()
                            else:
                                # Ignore player's moves on Black's turn
                                pass
                        else:
                            selected_square = None
                            possible_moves = None
                    else:
                        selected_square = None
                        possible_moves = None
                dragging = False
                dragged_piece = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                selected_square = None  # Stop highlighting the original square while dragging

    # Optionally, provide next move hint
    next_move_hint = None
    if opening_index < len(selected_line['moves']) and board.turn == chess.WHITE:
        next_move_hint = selected_line['moves'][opening_index]

    draw_board(selected_square, dragged_piece, mouse_pos, possible_moves, next_move_hint)

pygame.quit()
