import chess

def evaluate_board(board: chess.Board) -> int:
    """Evaluate the board state."""
    move_count = len(board.move_stack)

    if move_count < 10:
        value = evaluate_opening(board)
    elif move_count < 30:
        value = evaluate_middlegame(board)
    else:
        value = evaluate_endgame(board)

    # Add castling heuristic
    value += evaluate_castling(board)

    # Adding king safety **only if castling has occurred**
    value += evaluate_king_safety(board, chess.WHITE)
    value -= evaluate_king_safety(board, chess.BLACK)

    return value

def evaluate_opening(board: chess.Board) -> int:
    """Evaluate the board specifically for the opening phase."""
    value = evaluate_material(board)
    value += evaluate_central_control(board, chess.WHITE) * 0.3
    value -= evaluate_central_control(board, chess.BLACK) * 0.3
    value += evaluate_piece_development(board, chess.WHITE) * 0.4
    value -= evaluate_piece_development(board, chess.BLACK) * 0.4
    value += evaluate_early_queen_move_penalty(board, chess.WHITE)

    return value
        


def evaluate_middlegame(board: chess.Board) -> int:
    """Evaluate the board specifically for the middlegame phase."""
    value = evaluate_material(board)
    value += evaluate_central_control(board, chess.WHITE) * 0.2
    value -= evaluate_central_control(board, chess.BLACK) * 0.2
    value += evaluate_activity(board, chess.WHITE) * 0.3
    value -= evaluate_activity(board, chess.BLACK) * 0.3
    value += evaluate_king_safety(board, chess.WHITE) * 0.3
    value -= evaluate_king_safety(board, chess.BLACK) * 0.3
    return value

def evaluate_endgame(board: chess.Board) -> int:
    """Evaluate the board specifically for the endgame phase."""
    value = evaluate_material(board)
    value += evaluate_king_activity(board, chess.WHITE) * 0.3
    value -= evaluate_king_activity(board, chess.BLACK) * 0.3
    value += evaluate_pawn_advancement(board, chess.WHITE) * 0.4
    value -= evaluate_pawn_advancement(board, chess.BLACK) * 0.4
    return value

def evaluate_material(board: chess.Board) -> int | float:
    """Evaluate material balance on the board."""
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0 
    }
    value = 0

    if board.is_checkmate():
        return -float('inf') if board.turn == chess.WHITE else float('inf')
    if board.is_stalemate():
        return 0

    # Material evaluation
    for piece_type, piece_value in piece_values.items():
        value += len(board.pieces(piece_type, chess.WHITE)) * piece_value
        value -= len(board.pieces(piece_type, chess.BLACK)) * piece_value

    return value

def evaluate_central_control(board: chess.Board, color: chess.Color) -> int:
    """Evaluate central square control."""
    central_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
    score = 0
    for square in central_squares:
        if board.piece_at(square) and board.piece_at(square).color == color:
            score += 0.5
        elif board.is_attacked_by(color, square):
            score += 0.1
    return score

def evaluate_piece_development(board: chess.Board, color: chess.Color) -> int:
    """Evaluate piece development for knights and bishops."""
    developed_score = 0
    knight_squares = board.pieces(chess.KNIGHT, color)
    for square in knight_squares:
        if chess.square_rank(square) > 1 if color == chess.WHITE else chess.square_rank(square) < 6:
            developed_score += 0.3

    bishop_squares = board.pieces(chess.BISHOP, color)
    for square in bishop_squares:
        if chess.square_rank(square) > 1 if color == chess.WHITE else chess.square_rank(square) < 6:
            developed_score += 0.3
    return developed_score

def evaluate_activity(board: chess.Board, color: chess.Color) -> int:
    """Evaluate activity for a given color."""
    activity_score = 0
    for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
        for square in board.pieces(piece_type, color):
            activity_score += len(board.attacks(square))
    return activity_score * 0.1

# state_eval.py

def evaluate_king_safety(board: chess.Board, color: chess.Color) -> float:
    """
    Evaluate king safety for a given color **only after castling**.
    Penalizes if, after castling, the surrounding pawns are insufficient.
    
    Args:
        board (chess.Board): The current board state.
        color (chess.Color): The color to evaluate (chess.WHITE or chess.BLACK).
        
    Returns:
        float: The king safety score.
    """
    # Check if the player has castled
    if not has_castled(board, color):
        # Before castling, do not consider king safety
        return 0.0

    king_square = board.king(color)
    king_safety_score = 0.0

    # Define squares surrounding the king based on castling side
    if king_square in [chess.G1, chess.G8]:  # Kingside castling
        surrounding_squares = [chess.F1, chess.F2, chess.G2, chess.H1, chess.H2] if color == chess.WHITE else [chess.F8, chess.F7, chess.G7, chess.H8, chess.H7]
    elif king_square in [chess.C1, chess.C8]:  # Queenside castling
        surrounding_squares = [chess.B1, chess.B2, chess.C2, chess.D1, chess.D2] if color == chess.WHITE else [chess.B8, chess.B7, chess.C7, chess.D8, chess.D7]
    else:
        surrounding_squares = []

    # Count the number of friendly pawns in the surrounding squares
    pawns_near_king = sum(
        1 for sq in surrounding_squares 
        if board.piece_at(sq) == chess.PAWN and board.color_at(sq) == color
    )

    # Penalize if there are fewer than 2 pawns protecting the king
    if pawns_near_king < 2:
        king_safety_score -= 0.5

    return king_safety_score

def evaluate_king_activity(board: chess.Board, color: chess.Color) -> int | float:
    """Evaluate king activity (useful in endgames)."""
    king_square = board.king(color)
    return len(board.attacks(king_square)) * 0.1

def evaluate_pawn_advancement(board: chess.Board, color: chess.Color) -> int | float:
    """Evaluate pawn advancement in the endgame."""
    advancement_score = 0
    pawns = board.pieces(chess.PAWN, color)
    for square in pawns:
        rank = chess.square_rank(square)
        advancement_score += rank if color == chess.WHITE else (7 - rank)
    return advancement_score * 0.1

def evaluate_positional_heuristics(board: chess.Board, color: chess.Color) -> int | float:
    """Evaluate pawn structure and other positional factors."""
    positional_score = 0
    pawns = board.pieces(chess.PAWN, color)
    positional_score -= 0.3 * sum(is_isolated_pawn(board, sq, color) for sq in pawns)
    positional_score -= 0.05 * sum(is_backward_pawn(board, sq, color) for sq in pawns)
    return positional_score

def is_isolated_pawn(board: chess.Board, square: chess.Square, color: chess.Color) -> int | float:
    """Check if a pawn is isolated."""
    file = chess.square_file(square)
    adjacent_files = [file - 1, file + 1]
    for adj_file in adjacent_files:
        if 0 <= adj_file <= 7:
            for rank in range(8):
                adj_square = chess.square(adj_file, rank)
                if board.piece_at(adj_square) == chess.PAWN and board.color_at(adj_square) == color:
                    return 0
    return 1

def is_backward_pawn(board: chess.Board, square: chess.Square, color: chess.Color) -> int | float:
    """Check if a pawn is backward."""
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    direction = 1 if color == chess.WHITE else -1

    for adj_file in [file - 1, file + 1]:
        if 0 <= adj_file <= 7:
            adj_square = chess.square(adj_file, rank)
            if board.piece_at(adj_square) == chess.PAWN and board.color_at(adj_square) == color:
                return 0

    forward_square = chess.square(file, rank + direction)
    if 0 <= chess.square_rank(forward_square) <= 7:
        if board.piece_at(forward_square) is None and not board.is_attacked_by(not color, forward_square):
            return 0
    return 1


def evaluate_early_queen_move_penalty(board: chess.Board, color: chess.Color) -> float:
    penalty = 0.0
    move_count = len(board.move_stack)

    queen = chess.QUEEN
    queen_squares = board.pieces(queen, color)
    
    if queen_squares:
        queen_square = list(queen_squares)[0]
        starting_square = chess.D1 if color == chess.WHITE else chess.D8
        
        if queen_square != starting_square:
            if move_count <= 10:
                knights = board.pieces(chess.KNIGHT, color)
                bishops = board.pieces(chess.BISHOP, color)
                starting_knights = {chess.B1, chess.G1} if color == chess.WHITE else {chess.B8, chess.G8}
                starting_bishops = {chess.C1, chess.F1} if color == chess.WHITE else {chess.C8, chess.F8}
                
                knights_moved = any(knight not in starting_knights for knight in knights)
                bishops_moved = any(bishop not in starting_bishops for bishop in bishops)
                
                if not (knights_moved and bishops_moved):
                    penalty = -0.7 * (6 - move_count) / 6  
                else:
                    penalty = -0.2
    return penalty



def evaluate_castling(board: chess.Board) -> float:
    castling_score = 0.0

    if board.has_kingside_castling_rights(chess.WHITE):
        castling_score += 0.5
    if board.has_queenside_castling_rights(chess.WHITE):
        castling_score += 0.5

    if board.has_kingside_castling_rights(chess.BLACK):
        castling_score += 0.5
    if board.has_queenside_castling_rights(chess.BLACK):
        castling_score += 0.5

    return castling_score

def has_castled(board: chess.Board, color: chess.Color) -> bool:
    king_square = board.king(color)
    if color == chess.WHITE:
        return king_square in [chess.G1, chess.C1]
    else:
        return king_square in [chess.G8, chess.C8]