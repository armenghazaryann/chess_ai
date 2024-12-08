import chess
import chess.pgn
from algorithms import get_best_move_alpha_beta
import os
from datetime import datetime
from dotenv import load_dotenv
from monte_carlo import MCTS

load_dotenv()
engine_path = os.getenv("ENGINE_PATH")
weights_path = os.getenv("WEIGHTS_PATH")
save_dir = os.getenv("SAVE_DIR")

def main(game_index, save_directory):
    mcts_simulations = 1000
    mcts_max_depth = 35

    board = chess.Board()
    move_limit = 22
    game_moves = []
    with chess.engine.SimpleEngine.popen_uci([engine_path, f"--weights={os.path.expanduser(weights_path)}"]) as engine:
        mcts = MCTS(board.copy(), simulations=mcts_simulations, lc0_engine=engine, max_depth=mcts_max_depth)

        start_time = datetime.now()

        for move_number in range(1, move_limit + 1):
            print(f"Move {move_number}:")
            print(board)
            if board.is_game_over():
                print("Game over!")
                break
            if board.turn == chess.WHITE:
                print(f"Alpha-Beta pruning (White) is thinking with depth {4}...")
                move = get_best_move_alpha_beta(board.copy(), depth=4)
            else:
                print(f"Running MCTS for Black with {mcts_simulations} simulations and max depth {mcts_max_depth}...")
                mcts.update_current_node(board.copy(), board.peek())

                best_move = mcts.run()
                if best_move is None:
                    break
                print(f"Black plays: {best_move}")

                move = best_move
            board.push(move)
            game_moves.append(move)

        print("Final Board:")
        print(board)
        print("Game Result:", board.result())

        end_time = datetime.now()

        game = chess.pgn.Game()

        game.headers["Event"] = "AI vs AI Match"
        game.headers["Site"] = "Terminal Simulation"
        game.headers["Date"] = start_time.strftime("%Y.%m.%d")
        game.headers["Round"] = str(game_index)
        game.headers["White"] = "AlphaBetaPruningAI"
        game.headers["Black"] = "MonteCarloAI"
        game.headers["Result"] = board.result()
        game.headers["WhiteElo"] = "?"
        game.headers["BlackElo"] = "?"
        game.headers["TimeControl"] = "?"
        game.headers["EndTime"] = end_time.strftime("%H:%M:%S %Z")
        game.headers["Termination"] = board.outcome().termination.name if board.outcome() else "Unterminated"
        game.headers["AlphaBetaDepth"] = str(5)
        game.headers["MCTSSimulations"] = str(mcts_simulations)
        game.headers["MCTSMaxDepth"] = str(mcts_max_depth)

        node = game
        for move in board.move_stack:
            node = node.add_main_variation(move)

        os.makedirs(save_directory, exist_ok=True)
        pgn_path = os.path.join(save_directory, f'game_{game_index}.pgn')

        with open(pgn_path, 'w') as pgn_file:
            print(game, file=pgn_file)

        print(f"Game {game_index} has been saved to {pgn_path}")

if __name__ == "__main__":
    main(game_index=1, save_directory=save_dir)