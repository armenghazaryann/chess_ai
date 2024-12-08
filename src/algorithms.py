import chess
import chess.engine
from state_eval import evaluate_board

def tie_break_moves(board, moves):
    scored_moves = []
    for move in moves:
        board.push(move)
        score = evaluate_board(board)
        board.pop()
        scored_moves.append((move, score))
    
    scored_moves.sort(key=lambda x: x[1], reverse=True)
    best_score = scored_moves[0][1]
    best_moves = [move for move, score in scored_moves if score == best_score]
    
    if len(best_moves) > 1:
        best_moves = prioritize_moves(board, best_moves)
    
    return best_moves[0]


def prioritize_moves(board, moves):
    def move_priority(move):
        priority = 0
        if board.is_capture(move):
            priority += 3
        board.push(move)
        if board.is_check():
            priority += 2
        board.pop()
        if board.is_attacked_by(not board.turn, move.to_square):
            priority += 1
        return priority

    prioritized_moves = sorted(moves, key=move_priority, reverse=True)
    return prioritized_moves

def order_moves(board, moves):
    def move_score(move):
        priority = 0
        if len(board.move_stack) < 10:
            if board.is_castling(move):
                priority += 10
            if board.piece_at(move.from_square) in {chess.KNIGHT, chess.BISHOP}:
                priority += 2
            if board.is_castling(move):
                priority += 3 
        if board.is_capture(move):
            priority += 3
        board.push(move)
        score = 2 if board.is_check() else 0
        board.pop()
        return priority + score

    return sorted(moves, key=move_score, reverse=True)

def alpha_beta(board, depth, alpha, beta, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = order_moves(board, list(board.legal_moves))

    if is_maximizing:
        max_eval = -float('inf')
        for move in legal_moves:
            board.push(move)
            eval = alpha_beta(board, depth - 1, alpha, beta, not is_maximizing)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def get_best_move_alpha_beta(board, depth):
    best_eval: float = -float('inf')
    best_moves: list = []
    
    for move in board.legal_moves:
        board.push(move)
        eval = alpha_beta(board, depth - 1, -float('inf'), float('inf'), False)
        board.pop()
        if eval > best_eval:
            best_eval = eval
            best_moves = [move]
        elif eval == best_eval:
            best_moves.append(move)
    if len(best_moves) == 1:
        return best_moves[0]

    return tie_break_moves(board, best_moves)
