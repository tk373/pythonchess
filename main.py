import sys
import pygame
import chess
import chess.svg
import io
import time
from cairosvg import svg2png
from threading import Thread
from config import (
    BOARD_SIZE,
    EXTRA_SPACE,
    SIZE,
    MARGIN,
    SQUARE_SIZE,
    board,
    stockfish,
    BOARD_LOCK,
    OPENING_MOVES,
    SELECTED_LINE,
    SELECTED_OPENING,  # Import SELECTED_OPENING from config
    SCALING_FACTOR,
)

# Initialize other global variables
white_eval = None
black_eval = None
opening_index = 0  # Index for the current move within the selected line 

# Set up the display
screen = pygame.display.set_mode(SIZE, pygame.DOUBLEBUF)
pygame.display.set_caption('Chess Opening')

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
    with BOARD_LOCK:
        analyze_with_stockfish()
        global board_surface
        board_surface = render_board_surface()
        draw_board()

# Pre-render the board surface
def render_board_surface():
    svg_data = chess.svg.board(board, size=BOARD_SIZE, coordinates=True)
    png_data = svg2png(bytestring=svg_data.encode('utf-8'))
    image = pygame.image.load(io.BytesIO(png_data))
    return pygame.transform.scale(image, (int(BOARD_SIZE), int(BOARD_SIZE)))

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
            center_x = int(MARGIN + target_col * SQUARE_SIZE + SQUARE_SIZE / 2)
            center_y = int(MARGIN + target_row * SQUARE_SIZE + SQUARE_SIZE / 2)
            pygame.draw.circle(screen, (128, 128, 128), (center_x, center_y), SQUARE_SIZE // 6)

    if dragging_piece is not None and mouse_pos is not None:
       piece = board.piece_at(dragging_piece)
       if piece:
           piece_svg = chess.svg.piece(piece, size=SQUARE_SIZE)
           piece_png = svg2png(bytestring=piece_svg.encode('utf-8'))
           piece_image = pygame.image.load(io.BytesIO(piece_png))
           piece_image = pygame.transform.scale(piece_image, (int(SQUARE_SIZE), int(SQUARE_SIZE)))
           screen.blit(piece_image, (mouse_pos[0] - SQUARE_SIZE // 2, mouse_pos[1] - SQUARE_SIZE // 2))

    # Add space for additional information at the bottom
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, BOARD_SIZE, SIZE[0], EXTRA_SPACE))

    # Draw the evaluation bar
    eval_bar_height = 30  # Height of the evaluation bar
    eval_bar_width = BOARD_SIZE  # Full width of the board
    eval_bar_x = 0  # Start at the left edge
    eval_bar_y = BOARD_SIZE  # Position it just below the board 

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
    current_line = SELECTED_LINE['name']
    remaining_moves = len(OPENING_MOVES) - opening_index
    opening_text = f"Opening: {SELECTED_OPENING} - {current_line} (Moves Left: {remaining_moves})"
    opening_surface = font.render(opening_text, True, (0, 0, 0))
    screen.blit(opening_surface, (10, BOARD_SIZE + eval_bar_height + 10))

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
        screen.blit(status_surface, (10, BOARD_SIZE + eval_bar_height + 50))

    pygame.display.flip()

# Main game loop
running = True
selected_square = None
dragging = False
dragged_piece = None
possible_moves = None
board_needs_update = False

def handle_stockfish_move():
    with BOARD_LOCK:
        if board.turn != chess.BLACK:
            print("It's not Black's turn, returning early.")
            return  # Stockfish should only move for Black

        # Set the FEN position and verify
        fen_position = board.fen()
        stockfish.set_fen_position(fen_position)

        time.sleep(1)  # Introduce a short delay
        best_move = stockfish.get_best_move()

        print(f"Stockfish best move: {best_move}")

        # Ensure that Stockfish is only making moves for Black
        if best_move and board.turn == chess.BLACK:
            move = chess.Move.from_uci(best_move)

            if move in board.legal_moves:
                board.push(move)

                dragged_piece = None
                possible_moves = None
                
                global board_surface

                board_surface = render_board_surface()
                draw_board()

                analyze_with_stockfish_and_render()

                # Ensure Stockfish continues to move if it's still Black's turn
                if board.turn == chess.BLACK:
                    handle_stockfish_move()
            else:
                print(f"Illegal move by Stockfish: {best_move} in {board.fen()}")
        else:
            print("Stockfish did not return a valid move or attempted to move White's pieces.")

def process_player_move(uci_move):
    global opening_index, selected_square, possible_moves, board_surface

    move = chess.Move.from_uci(uci_move)

    with BOARD_LOCK:

        if board.turn != chess.WHITE:
            print("It's not White's turn, returning early.")
            return  # Only process the player's move if it's White's turn

        if opening_index < len(SELECTED_LINE['moves']):
            expected_move = SELECTED_LINE['moves'][opening_index]

            if uci_move == expected_move:
                board.push(chess.Move.from_uci(uci_move))
                opening_index += 1

                selected_square = None
                possible_moves = None

                # Update the board surface and render it immediately
                board_surface = render_board_surface()
                draw_board(selected_square)

                if opening_index < len(SELECTED_LINE['moves']):
                    expected_move = SELECTED_LINE['moves'][opening_index]
                    board.push_uci(expected_move)
                    opening_index += 1

                    # Analyze the position immediately
                    analyze_with_stockfish_and_render()

                    if board.turn == chess.BLACK:
                        print("Opening phase ended, Black's turn, triggering Stockfish...")
                        handle_stockfish_move()
                else:
                    print("Opening sequence completed. Switching to Stockfish control.")
                    if board.turn == chess.BLACK:
                        handle_stockfish_move()
            else:
                print(f"Incorrect move. Expected: {expected_move}, but got: {uci_move}")
        else:
            if uci_move in [move.uci() for move in board.legal_moves]:
                if board.piece_at(move.from_square).piece_type == chess.PAWN and chess.square_rank(move.to_square) in [0, 7]:
                    move.promotion = chess.QUEEN  # Promote to queen by default
                board.push(chess.Move.from_uci(uci_move))

                # Immediate board update after move
                board_surface = render_board_surface()
                draw_board(selected_square)

                # Analyze and move for Black immediately after the player's move
                analyze_with_stockfish_and_render()

                if board.turn == chess.BLACK:
                    time.sleep(1)  # Introduce a delay before Stockfish makes its move
                    best_move = stockfish.get_best_move()
                    if best_move and board.turn == chess.BLACK:
                        board.push_uci(best_move)
                        analyze_with_stockfish_and_render()
                    else:
                        print("No valid move returned by Stockfish or Stockfish tried to move White's pieces.")
            else:
                print(f"Move {uci_move} is illegal. Ignoring.")

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
            if MARGIN <= x < SIZE[0] - MARGIN and MARGIN <= y < BOARD_SIZE - MARGIN:
                col = int((x - MARGIN) // SQUARE_SIZE)
                row = int(7 - (y - MARGIN) // SQUARE_SIZE)
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
                col = int((x - MARGIN) // SQUARE_SIZE)
                row = int(7 - (y - MARGIN) // SQUARE_SIZE)
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
                col = int((x - MARGIN) // SQUARE_SIZE)
                row = int(7 - (y - MARGIN) // SQUARE_SIZE)
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
