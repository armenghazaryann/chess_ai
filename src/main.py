import chess

from algorithms import get_best_move_alpha_beta, monte_carlo


def main():
    board = chess.Board()
    move_limit = 20
    for move_number in range(move_limit):
        print(f"Move {move_number + 1}:")
        print(board)
        if board.is_game_over():
            print("Game over!")
            break
        if board.turn == chess.WHITE:
            print("Alpha-Beta pruning (White) is thinking...")
            move = get_best_move_alpha_beta(board, depth=5)
        else:
            print("Monte Carlo (Black) is thinking...")
            move = monte_carlo(board, simulations=15, depth=25)
        board.push(move)
    print("Final Board:")
    print(board)
    print("Game Result:", board.result())

if __name__ == "__main__":
    main()