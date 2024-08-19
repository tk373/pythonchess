import pygame
import chess
import chess.svg
import io
from cairosvg import svg2png
from config import (
    BOARD_SIZE,
    MARGIN,
    SQUARE_SIZE,
    SIZE,
    EXTRA_SPACE,
    board,
    SELECTED_LINE,
    OPENING_MOVES,
    SELECTED_OPENING,
)

# Pre-render the board surface
def render_board_surface():
    svg_data = chess.svg.board(board, size=BOARD_SIZE, coordinates=True)
    png_data = svg2png(bytestring=svg_data.encode('utf-8'))
    image = pygame.image.load(io.BytesIO(png_data))
    return pygame.transform.scale(image, (int(BOARD_SIZE), int(BOARD_SIZE)))

# Function to draw the board
def draw_board(screen, board_surface, selected_square=None, dragging_piece=None, mouse_pos=None, possible_moves=None, white_eval=None, black_eval=None, opening_index=0):
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
