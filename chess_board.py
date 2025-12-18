# Chess board and move generation
# Basic board representation with 8x8 array

import copy
from typing import List, Tuple, Optional


class ChessBoard:
    # Chess board class - stores pieces and generates moves
    
    # Piece constants
    EMPTY = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
    
    # Color constants
    WHITE = 0
    BLACK = 1
    
    def __init__(self):
        # setup board to starting position
        # board[row][col] = (piece_type, color) or None
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.current_turn = self.WHITE
        
        # Castling rights [white_kingside, white_queenside, black_kingside, black_queenside]
        self.castling_rights = [True, True, True, True]
        
        # En passant target square (row, col) or None
        self.en_passant_target = None
        
        # Move history for debugging and analysis
        self.move_history = []
        
        # Halfmove clock for fifty-move rule
        self.halfmove_clock = 0
        
        # Initialize to starting position
        self._setup_initial_position()
    
    def _setup_initial_position(self):
        # put pieces in starting positions
        # Black pieces (row 0 and 1)
        back_rank = [self.ROOK, self.KNIGHT, self.BISHOP, self.QUEEN, 
                     self.KING, self.BISHOP, self.KNIGHT, self.ROOK]
        
        for col in range(8):
            self.board[0][col] = (back_rank[col], self.BLACK)
            self.board[1][col] = (self.PAWN, self.BLACK)
        
        # White pieces (row 6 and 7)
        for col in range(8):
            self.board[6][col] = (self.PAWN, self.WHITE)
            self.board[7][col] = (back_rank[col], self.WHITE)
    
    def get_piece(self, row: int, col: int) -> Optional[Tuple[int, int]]:
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def set_piece(self, row: int, col: int, piece: Optional[Tuple[int, int]]):
        self.board[row][col] = piece
        if piece and piece[0] == self.KING:
            if piece[1] == self.WHITE:
                self.white_king_pos = (row, col)
            else:
                self.black_king_pos = (row, col)
    
    def is_valid_square(self, row: int, col: int) -> bool:
        return 0 <= row < 8 and 0 <= col < 8
    
    def generate_moves(self, color: int) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        # get all legal moves for the given color
        # returns list of ((from_row, from_col), (to_row, to_col))
        pseudo_legal_moves = []
        
        # Generate pseudo-legal moves for all pieces
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece[1] == color:
                    piece_type = piece[0]
                    moves = self._generate_piece_moves(row, col, piece_type, color)
                    pseudo_legal_moves.extend(moves)
        
        # Filter out moves that leave king in check
        legal_moves = []
        for move in pseudo_legal_moves:
            if self._is_legal_move(move, color):
                legal_moves.append(move)
        
        return legal_moves
    
    def _generate_piece_moves(self, row: int, col: int, piece_type: int, color: int) -> List:
        # generate moves based on piece type
        if piece_type == self.PAWN:
            return self._generate_pawn_moves(row, col, color)
        elif piece_type == self.KNIGHT:
            return self._generate_knight_moves(row, col, color)
        elif piece_type == self.BISHOP:
            return self._generate_bishop_moves(row, col, color)
        elif piece_type == self.ROOK:
            return self._generate_rook_moves(row, col, color)
        elif piece_type == self.QUEEN:
            return self._generate_queen_moves(row, col, color)
        elif piece_type == self.KING:
            return self._generate_king_moves(row, col, color)
        return []
    
    def _generate_pawn_moves(self, row: int, col: int, color: int) -> List:
        # pawn moves - forward, double move, captures, en passant
        moves = []
        direction = -1 if color == self.WHITE else 1
        start_row = 6 if color == self.WHITE else 1
        
        # Forward move
        new_row = row + direction
        if self.is_valid_square(new_row, col) and self.board[new_row][col] is None:
            moves.append(((row, col), (new_row, col)))
            
            # Double move from starting position
            if row == start_row:
                new_row2 = row + 2 * direction
                if self.board[new_row2][col] is None:
                    moves.append(((row, col), (new_row2, col)))
        
        # Captures
        for dcol in [-1, 1]:
            new_col = col + dcol
            new_row = row + direction
            if self.is_valid_square(new_row, new_col):
                target = self.board[new_row][new_col]
                if target and target[1] != color:
                    moves.append(((row, col), (new_row, new_col)))
                
                # En passant
                if self.en_passant_target == (new_row, new_col):
                    moves.append(((row, col), (new_row, new_col)))
        
        return moves
    
    def _generate_knight_moves(self, row: int, col: int, color: int) -> List:
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for drow, dcol in knight_moves:
            new_row, new_col = row + drow, col + dcol
            if self.is_valid_square(new_row, new_col):
                target = self.board[new_row][new_col]
                if target is None or target[1] != color:
                    moves.append(((row, col), (new_row, new_col)))
        
        return moves
    
    def _generate_sliding_moves(self, row: int, col: int, color: int, directions: List) -> List:
        # sliding pieces - keep going until hit edge or piece
        moves = []
        
        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol
            
            while self.is_valid_square(new_row, new_col):
                target = self.board[new_row][new_col]
                
                if target is None:
                    moves.append(((row, col), (new_row, new_col)))
                elif target[1] != color:
                    moves.append(((row, col), (new_row, new_col)))
                    break
                else:
                    break
                
                new_row += drow
                new_col += dcol
        
        return moves
    
    def _generate_bishop_moves(self, row: int, col: int, color: int) -> List:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self._generate_sliding_moves(row, col, color, directions)
    
    def _generate_rook_moves(self, row: int, col: int, color: int) -> List:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self._generate_sliding_moves(row, col, color, directions)
    
    def _generate_queen_moves(self, row: int, col: int, color: int) -> List:
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                     (0, 1), (1, -1), (1, 0), (1, 1)]
        return self._generate_sliding_moves(row, col, color, directions)
    
    def _generate_king_moves(self, row: int, col: int, color: int) -> List:
        # king moves + castling
        moves = []
        
        # Normal king moves
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if drow == 0 and dcol == 0:
                    continue
                new_row, new_col = row + drow, col + dcol
                if self.is_valid_square(new_row, new_col):
                    target = self.board[new_row][new_col]
                    if target is None or target[1] != color:
                        moves.append(((row, col), (new_row, new_col)))
        
        # Castling
        if color == self.WHITE:
            back_rank = 7
            # Kingside castling
            if self.castling_rights[0] and self._can_castle_kingside(color):
                moves.append(((row, col), (back_rank, 6)))
            # Queenside castling
            if self.castling_rights[1] and self._can_castle_queenside(color):
                moves.append(((row, col), (back_rank, 2)))
        else:
            back_rank = 0
            # Kingside castling
            if self.castling_rights[2] and self._can_castle_kingside(color):
                moves.append(((row, col), (back_rank, 6)))
            # Queenside castling
            if self.castling_rights[3] and self._can_castle_queenside(color):
                moves.append(((row, col), (back_rank, 2)))
        
        return moves
    
    def _can_castle_kingside(self, color: int) -> bool:
        back_rank = 7 if color == self.WHITE else 0
        
        # Check if squares between king and rook are empty
        if self.board[back_rank][5] is not None or self.board[back_rank][6] is not None:
            return False
        
        # Check if king is in check or passes through check
        if self.is_square_attacked(back_rank, 4, 1 - color):
            return False
        if self.is_square_attacked(back_rank, 5, 1 - color):
            return False
        if self.is_square_attacked(back_rank, 6, 1 - color):
            return False
        
        return True
    
    def _can_castle_queenside(self, color: int) -> bool:
        back_rank = 7 if color == self.WHITE else 0
        
        # Check if squares between king and rook are empty
        if (self.board[back_rank][1] is not None or 
            self.board[back_rank][2] is not None or 
            self.board[back_rank][3] is not None):
            return False
        
        # Check if king is in check or passes through check
        if self.is_square_attacked(back_rank, 4, 1 - color):
            return False
        if self.is_square_attacked(back_rank, 3, 1 - color):
            return False
        if self.is_square_attacked(back_rank, 2, 1 - color):
            return False
        
        return True
    
    def is_square_attacked(self, row: int, col: int, by_color: int) -> bool:
        # check if square is under attack
        # Check pawn attacks
        pawn_direction = 1 if by_color == self.WHITE else -1
        for dcol in [-1, 1]:
            attack_row = row + pawn_direction
            attack_col = col + dcol
            if self.is_valid_square(attack_row, attack_col):
                piece = self.board[attack_row][attack_col]
                if piece and piece == (self.PAWN, by_color):
                    return True
        
        # Check knight attacks
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        for drow, dcol in knight_moves:
            new_row, new_col = row + drow, col + dcol
            if self.is_valid_square(new_row, new_col):
                piece = self.board[new_row][new_col]
                if piece and piece == (self.KNIGHT, by_color):
                    return True
        
        # Check sliding piece attacks
        # Bishop/Queen diagonal attacks
        for drow, dcol in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            new_row, new_col = row + drow, col + dcol
            while self.is_valid_square(new_row, new_col):
                piece = self.board[new_row][new_col]
                if piece:
                    if piece[1] == by_color and piece[0] in [self.BISHOP, self.QUEEN]:
                        return True
                    break
                new_row += drow
                new_col += dcol
        
        # Rook/Queen straight attacks
        for drow, dcol in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + drow, col + dcol
            while self.is_valid_square(new_row, new_col):
                piece = self.board[new_row][new_col]
                if piece:
                    if piece[1] == by_color and piece[0] in [self.ROOK, self.QUEEN]:
                        return True
                    break
                new_row += drow
                new_col += dcol
        
        # Check king attacks
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if drow == 0 and dcol == 0:
                    continue
                new_row, new_col = row + drow, col + dcol
                if self.is_valid_square(new_row, new_col):
                    piece = self.board[new_row][new_col]
                    if piece and piece == (self.KING, by_color):
                        return True
        
        return False
    
    def _is_legal_move(self, move: Tuple, color: int) -> bool:
        # check if move is legal (king not in check after move)
        # Make the move temporarily
        from_pos, to_pos = move
        original_piece = self.board[to_pos[0]][to_pos[1]]
        moving_piece = self.board[from_pos[0]][from_pos[1]]
        
        self.board[to_pos[0]][to_pos[1]] = moving_piece
        self.board[from_pos[0]][from_pos[1]] = None
        
        # Update king position if king is moving
        if moving_piece[0] == self.KING:
            if color == self.WHITE:
                old_king_pos = self.white_king_pos
                self.white_king_pos = to_pos
            else:
                old_king_pos = self.black_king_pos
                self.black_king_pos = to_pos
        
        # Check if king is in check
        king_pos = self.white_king_pos if color == self.WHITE else self.black_king_pos
        is_legal = not self.is_square_attacked(king_pos[0], king_pos[1], 1 - color)
        
        # Undo the move
        self.board[from_pos[0]][from_pos[1]] = moving_piece
        self.board[to_pos[0]][to_pos[1]] = original_piece
        
        if moving_piece[0] == self.KING:
            if color == self.WHITE:
                self.white_king_pos = old_king_pos
            else:
                self.black_king_pos = old_king_pos
        
        return is_legal
    
    def make_move(self, move: Tuple) -> bool:
        # actually make the move on the board
        from_pos, to_pos = move
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        moving_piece = self.board[from_row][from_col]
        if not moving_piece:
            return False
        
        captured_piece = self.board[to_row][to_col]
        
        # Handle en passant capture
        en_passant_capture = None
        if moving_piece[0] == self.PAWN and self.en_passant_target == to_pos:
            capture_row = to_row + (1 if moving_piece[1] == self.WHITE else -1)
            en_passant_capture = self.board[capture_row][to_col]
            self.board[capture_row][to_col] = None
        
        # Make the move
        self.board[to_row][to_col] = moving_piece
        self.board[from_row][from_col] = None
        
        # Handle castling
        if moving_piece[0] == self.KING and abs(to_col - from_col) == 2:
            # Kingside castling
            if to_col == 6:
                rook = self.board[to_row][7]
                self.board[to_row][5] = rook
                self.board[to_row][7] = None
            # Queenside castling
            elif to_col == 2:
                rook = self.board[to_row][0]
                self.board[to_row][3] = rook
                self.board[to_row][0] = None
        
        # Update castling rights
        if moving_piece[0] == self.KING:
            if moving_piece[1] == self.WHITE:
                self.castling_rights[0] = False
                self.castling_rights[1] = False
            else:
                self.castling_rights[2] = False
                self.castling_rights[3] = False
        
        if moving_piece[0] == self.ROOK:
            if moving_piece[1] == self.WHITE:
                if from_pos == (7, 0):
                    self.castling_rights[1] = False
                elif from_pos == (7, 7):
                    self.castling_rights[0] = False
            else:
                if from_pos == (0, 0):
                    self.castling_rights[3] = False
                elif from_pos == (0, 7):
                    self.castling_rights[2] = False
        
        # Set en passant target
        self.en_passant_target = None
        if moving_piece[0] == self.PAWN and abs(to_row - from_row) == 2:
            self.en_passant_target = ((from_row + to_row) // 2, from_col)
        
        # Update halfmove clock
        if moving_piece[0] == self.PAWN or captured_piece or en_passant_capture:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        
        # Switch turn
        self.current_turn = 1 - self.current_turn
        
        # Add to move history
        self.move_history.append((move, captured_piece, en_passant_capture))
        
        return True
    
    def is_checkmate(self, color: int) -> bool:
        # checkmate = in check and no legal moves
        king_pos = self.white_king_pos if color == self.WHITE else self.black_king_pos
        
        # Must be in check
        if not self.is_square_attacked(king_pos[0], king_pos[1], 1 - color):
            return False
        
        # No legal moves available
        legal_moves = self.generate_moves(color)
        return len(legal_moves) == 0
    
    def is_stalemate(self, color: int) -> bool:
        # stalemate = not in check but no legal moves
        king_pos = self.white_king_pos if color == self.WHITE else self.black_king_pos
        
        # Must NOT be in check
        if self.is_square_attacked(king_pos[0], king_pos[1], 1 - color):
            return False
        
        # No legal moves available
        legal_moves = self.generate_moves(color)
        return len(legal_moves) == 0
    
    def copy(self):
        # make a copy of the board for searching
        new_board = ChessBoard.__new__(ChessBoard)
        new_board.board = [row[:] for row in self.board]
        new_board.white_king_pos = self.white_king_pos
        new_board.black_king_pos = self.black_king_pos
        new_board.current_turn = self.current_turn
        new_board.castling_rights = self.castling_rights[:]
        new_board.en_passant_target = self.en_passant_target
        new_board.move_history = self.move_history[:]
        new_board.halfmove_clock = self.halfmove_clock
        return new_board
    
    def __str__(self):
        # print the board nicely
        piece_symbols = {
            (self.PAWN, self.WHITE): '♙',
            (self.KNIGHT, self.WHITE): '♘',
            (self.BISHOP, self.WHITE): '♗',
            (self.ROOK, self.WHITE): '♖',
            (self.QUEEN, self.WHITE): '♕',
            (self.KING, self.WHITE): '♔',
            (self.PAWN, self.BLACK): '♟',
            (self.KNIGHT, self.BLACK): '♞',
            (self.BISHOP, self.BLACK): '♝',
            (self.ROOK, self.BLACK): '♜',
            (self.QUEEN, self.BLACK): '♛',
            (self.KING, self.BLACK): '♚',
        }
        
        lines = []
        lines.append("  a b c d e f g h")
        for row in range(8):
            line = f"{8-row} "
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    line += piece_symbols[piece] + " "
                else:
                    line += ". "
            lines.append(line + f"{8-row}")
        lines.append("  a b c d e f g h")
        return "\n".join(lines)
