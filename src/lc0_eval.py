import chess
import chess.engine
from functools import lru_cache


@lru_cache(maxsize=None)
def get_lc0_evaluations_cached(engine, fen: str, is_black, lc0_depth = 2):

    board = chess.Board(fen)
    evaluations = {}
    
    for move in board.legal_moves:
        board.push(move)
        if board.is_game_over():
            score = 100000
            board.pop()
            evaluations[move] = score
            continue
        info = engine.analyse(board, chess.engine.Limit(depth=lc0_depth))
        board.pop()
        if is_black:
            score = info["score"].black().score(mate_score=100000)
        else:
            score = info["score"].white().score(mate_score=100000)
        evaluations[move] = score

    return evaluations


def get_lc0_evaluations(engine, board: chess.Board, is_black = True, lc0_depth = 2):
    fen = board.fen()
    return get_lc0_evaluations_cached(engine, fen, is_black, lc0_depth = lc0_depth)

