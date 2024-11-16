import random


import chess


from state_eval import evaluate_board

def alpha_beta(board, depth, alpha, beta, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    legal_moves = list(board.legal_moves)
    if is_maximizing:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)
            eval = alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval = alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def get_best_move_alpha_beta(board, depth):
    max_eval = float('-inf')
    best_move = None
    for move in board.legal_moves:
        board.push(move)
        eval = alpha_beta(board, depth - 1, float('-inf'), float('inf'), False)
        board.pop()
        if eval > max_eval:
            max_eval = eval
            best_move = move
    return best_move

def monte_carlo(board, simulations):
    move_scores = {}
    legal_moves = list(board.legal_moves)
    for move in legal_moves:
        move_scores[move] = 0
    for move in legal_moves:
        for _ in range(simulations):
            board.push(move)
            result = simulate_random_game(board)
            board.pop()
            if result == 1:
                move_scores[move] += 1
            elif result == 0:
                move_scores[move] += 0.5
    best_move = max(move_scores, key=move_scores.get)
    return best_move

def simulate_random_game(board):
    temp_board = board.copy()
    while not temp_board.is_game_over():
        moves = list(temp_board.legal_moves)
        move = random.choice(moves)
        temp_board.push(move)
    result = temp_board.result()
    if result == '1-0':
        return 1 if board.turn == chess.WHITE else -1
    elif result == '0-1':
        return -1 if board.turn == chess.WHITE else 1
    else:
        return 0