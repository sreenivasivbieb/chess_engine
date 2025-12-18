# Position evaluation - score how good a position is
# positive = white better, negative = black better

from chess_board import ChessBoard


class Evaluator:
    
    # Material values (in centipawns)
    PIECE_VALUES = {
        ChessBoard.PAWN: 100,
        ChessBoard.KNIGHT: 320,
        ChessBoard.BISHOP: 330,
        ChessBoard.ROOK: 500,
        ChessBoard.QUEEN: 900,
        ChessBoard.KING: 20000
    }
    
    # Piece-Square Tables - bonus points for good piece placement
    # from white's perspective
    
    # Pawns - better in center and advanced
    PAWN_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]
    ]
    
    # Knights - better in center, bad on edges
    KNIGHT_TABLE = [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50]
    ]
    
    # Bishops - like diagonals
    BISHOP_TABLE = [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20]
    ]
    
    # Rooks - good on 7th rank
    ROOK_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [0,  0,  0,  5,  5,  0,  0,  0]
    ]
    
    # Queen
    QUEEN_TABLE = [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [-5,  0,  5,  5,  5,  5,  0, -5],
        [0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20]
    ]
    
    # King middlegame - stay safe, castle
    KING_MIDDLE_TABLE = [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [20, 20,  0,  0,  0,  0, 20, 20],
        [20, 30, 10,  0,  0, 10, 30, 20]
    ]
    
    # King endgame - get active
    KING_END_TABLE = [
        [-50,-40,-30,-20,-20,-30,-40,-50],
        [-30,-20,-10,  0,  0,-10,-20,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-30,  0,  0,  0,  0,-30,-30],
        [-50,-30,-30,-30,-30,-30,-30,-50]
    ]
    
    def __init__(self):
        self.piece_square_tables = {
            ChessBoard.PAWN: self.PAWN_TABLE,
            ChessBoard.KNIGHT: self.KNIGHT_TABLE,
            ChessBoard.BISHOP: self.BISHOP_TABLE,
            ChessBoard.ROOK: self.ROOK_TABLE,
            ChessBoard.QUEEN: self.QUEEN_TABLE,
            ChessBoard.KING: self.KING_MIDDLE_TABLE
        }
    
    def evaluate(self, board: ChessBoard) -> int:
        # evaluate position and return score
        # Quick checkmate detection
        if board.is_checkmate(ChessBoard.WHITE):
            return -100000
        if board.is_checkmate(ChessBoard.BLACK):
            return 100000
        
        # Stalemate is a draw
        if board.is_stalemate(ChessBoard.WHITE) or board.is_stalemate(ChessBoard.BLACK):
            return 0
        
        score = 0
        
        # Material and positional evaluation
        score += self._evaluate_material_and_position(board)
        
        # Mobility bonus
        score += self._evaluate_mobility(board)
        
        # King safety
        score += self._evaluate_king_safety(board)
        
        return score
    
    def _evaluate_material_and_position(self, board: ChessBoard) -> int:
        score = 0
        
        # Determine if we're in endgame (for king PST selection)
        is_endgame = self._is_endgame(board)
        
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece:
                    piece_type, color = piece
                    
                    # Material value
                    material_value = self.PIECE_VALUES[piece_type]
                    
                    # Positional value from piece-square tables
                    if piece_type == ChessBoard.KING:
                        pst = self.KING_END_TABLE if is_endgame else self.KING_MIDDLE_TABLE
                    else:
                        pst = self.piece_square_tables[piece_type]
                    
                    # For black pieces, flip the board vertically
                    if color == ChessBoard.WHITE:
                        positional_value = pst[row][col]
                        score += material_value + positional_value
                    else:
                        positional_value = pst[7 - row][col]
                        score -= material_value + positional_value
        
        return score
    
    def _evaluate_mobility(self, board: ChessBoard) -> int:
        # more moves = better
        white_moves = len(board.generate_moves(ChessBoard.WHITE))
        black_moves = len(board.generate_moves(ChessBoard.BLACK))
        
        # Small bonus for mobility (0.1 centipawn per move)
        return (white_moves - black_moves) * 10 // 10
    
    def _evaluate_king_safety(self, board: ChessBoard) -> int:
        # king safety - pawns in front are good
        score = 0
        
        # Check pawn shield for white king
        white_king_row, white_king_col = board.white_king_pos
        if white_king_row == 7:  # King on back rank
            for col in [white_king_col - 1, white_king_col, white_king_col + 1]:
                if 0 <= col < 8:
                    piece = board.board[6][col]
                    if piece and piece == (ChessBoard.PAWN, ChessBoard.WHITE):
                        score += 10  # Bonus for pawn shield
        
        # Check pawn shield for black king
        black_king_row, black_king_col = board.black_king_pos
        if black_king_row == 0:  # King on back rank
            for col in [black_king_col - 1, black_king_col, black_king_col + 1]:
                if 0 <= col < 8:
                    piece = board.board[1][col]
                    if piece and piece == (ChessBoard.PAWN, ChessBoard.BLACK):
                        score -= 10  # Penalty for black's pawn shield
        
        return score
    
    def _is_endgame(self, board: ChessBoard) -> bool:
        # endgame if few pieces left
        piece_count = 0
        queen_count = 0
        
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece and piece[0] != ChessBoard.KING:
                    piece_count += 1
                    if piece[0] == ChessBoard.QUEEN:
                        queen_count += 1
        
        # Endgame if no queens and few pieces, or very few pieces total
        return (queen_count == 0 and piece_count <= 6) or piece_count <= 4
    
    def evaluate_move_priority(self, board: ChessBoard, move: tuple) -> int:
        # give moves a priority for ordering
        from_pos, to_pos = move
        moving_piece = board.board[from_pos[0]][from_pos[1]]
        captured_piece = board.board[to_pos[0]][to_pos[1]]
        
        score = 0
        
        # Captures are prioritized (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
        if captured_piece:
            victim_value = self.PIECE_VALUES[captured_piece[0]]
            attacker_value = self.PIECE_VALUES[moving_piece[0]]
            score += 10 * victim_value - attacker_value
        
        # Promotions are very valuable
        if moving_piece[0] == ChessBoard.PAWN:
            if (moving_piece[1] == ChessBoard.WHITE and to_pos[0] == 0) or \
               (moving_piece[1] == ChessBoard.BLACK and to_pos[0] == 7):
                score += 9000  # Queen promotion
        
        # Center control bonus
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if to_pos in center_squares:
            score += 50
        
        return score
