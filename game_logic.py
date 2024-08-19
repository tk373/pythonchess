import chess
import time
from config import board, stockfish, BOARD_LOCK, SELECTED_LINE
from rendering import render_board_surface, draw_board

# Game-related state variables
white_eval = None
black_eval = None
opening_index = 0

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

def analyze_with_stockfish_and_render(screen, board_surface):
    with BOARD_LOCK:
        analyze_with_stockfish()
        board_surface = render_board_surface()
        draw_board(screen, board_surface, white_eval=white_eval, black_eval=black_eval, opening_index=opening_index)

def handle_stockfish_move(screen, board_surface):
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

                board_surface = render_board_surface()
                draw_board(screen, board_surface, white_eval=white_eval, black_eval=black_eval, opening_index=opening_index)

                analyze_with_stockfish_and_render(screen, board_surface)

                # Ensure Stockfish continues to move if it's still Black's turn
                if board.turn == chess.BLACK:
                    handle_stockfish_move(screen, board_surface)
            else:
                print(f"Illegal move by Stockfish: {best_move} in {board.fen()}")
        else:
            print("Stockfish did not return a valid move or attempted to move White's pieces.")

def process_player_move(uci_move, screen, board_surface, selected_square=None, possible_moves=None):
    global opening_index

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
                draw_board(screen, board_surface, selected_square, white_eval=white_eval, black_eval=black_eval, opening_index=opening_index)

                if opening_index < len(SELECTED_LINE['moves']):
                    expected_move = SELECTED_LINE['moves'][opening_index]
                    board.push_uci(expected_move)
                    opening_index += 1

                    # Analyze the position immediately
                    analyze_with_stockfish_and_render(screen, board_surface)

                    if board.turn == chess.BLACK:
                        print("Opening phase ended, Black's turn, triggering Stockfish...")
                        handle_stockfish_move(screen, board_surface)
                else:
                    print("Opening sequence completed. Switching to Stockfish control.")
                    if board.turn == chess.BLACK:
                        handle_stockfish_move(screen, board_surface)
            else:
                print(f"Incorrect move. Expected: {expected_move}, but got: {uci_move}")
        else:
            if uci_move in [move.uci() for move in board.legal_moves]:
                if board.piece_at(move.from_square).piece_type == chess.PAWN and chess.square_rank(move.to_square) in [0, 7]:
                    move.promotion = chess.QUEEN  # Promote to queen by default
                board.push(chess.Move.from_uci(uci_move))

                # Immediate board update after move
                board_surface = render_board_surface()
                draw_board(screen, board_surface, selected_square, white_eval=white_eval, black_eval=black_eval, opening_index=opening_index)

                # Analyze and move for Black immediately after the player's move
                analyze_with_stockfish_and_render(screen, board_surface)

                if board.turn == chess.BLACK:
                    time.sleep(1)  # Introduce a delay before Stockfish makes its move
                    best_move = stockfish.get_best_move()
                    if best_move and board.turn == chess.BLACK:
                        board.push_uci(best_move)
                        analyze_with_stockfish_and_render(screen, board_surface)
                    else:
                        print("No valid move returned by Stockfish or Stockfish tried to move White's pieces.")
            else:
                print(f"Move {uci_move} is illegal. Ignoring.")
