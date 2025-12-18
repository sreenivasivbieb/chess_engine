# Main chess engine - search and evaluation
# Uses minimax with alpha-beta pruning
# Zobrist hashing for transposition table

import random
import time
from typing import Optional, Tuple, List
from chess_board import ChessBoard
from evaluation import Evaluator


class ZobristHash:
    # Hash positions so we can store them in transposition table
    
    def __init__(self):
        random.seed(42)  # for testing
        
        # Hash values for pieces on squares
        # [piece_type][color][row][col]
        self.piece_keys = [[[[random.getrandbits(64) for _ in range(8)]
                             for _ in range(8)]
                            for _ in range(2)]
                           for _ in range(7)]  # 7 piece types (including EMPTY)
        
        # Hash for side to move
        self.side_to_move = random.getrandbits(64)
        
        # Hash for castling rights [4 rights]
        self.castling_keys = [random.getrandbits(64) for _ in range(4)]
        
        # Hash for en passant file [8 files]
        self.en_passant_keys = [random.getrandbits(64) for _ in range(8)]
    
    def hash_position(self, board: ChessBoard) -> int:
        # compute hash for the position
        h = 0
        
        # Hash all pieces on the board
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece:
                    piece_type, color = piece
                    h ^= self.piece_keys[piece_type][color][row][col]
        
        # Hash side to move
        if board.current_turn == ChessBoard.BLACK:
            h ^= self.side_to_move
        
        # Hash castling rights
        for i, right in enumerate(board.castling_rights):
            if right:
                h ^= self.castling_keys[i]
        
        # Hash en passant
        if board.en_passant_target:
            _, col = board.en_passant_target
            h ^= self.en_passant_keys[col]
        
        return h


class TranspositionTable:
    # Cache for positions we already evaluated
    # saves a lot of time!
    
    # Entry types
    EXACT = 0  # Exact score
    LOWER_BOUND = 1  # Alpha cutoff occurred (score >= beta)
    UPPER_BOUND = 2  # Beta cutoff occurred (score <= alpha)
    
    def __init__(self, size_mb: int = 64):
        # Each entry is roughly 40 bytes
        self.max_entries = (size_mb * 1024 * 1024) // 40
        self.table = {}
        self.hits = 0
        self.misses = 0
    
    def store(self, zobrist_hash: int, depth: int, score: int, flag: int, best_move: Optional[tuple] = None):
        # store position in table
        if zobrist_hash not in self.table or self.table[zobrist_hash][1] <= depth:
            self.table[zobrist_hash] = (score, depth, flag, best_move)
            
            # Limit table size (simple replacement scheme)
            if len(self.table) > self.max_entries:
                # Remove a random entry (better schemes exist but this is simple)
                self.table.pop(next(iter(self.table)))
    
    def probe(self, zobrist_hash: int, depth: int, alpha: int, beta: int) -> Optional[Tuple[int, Optional[tuple]]]:
        # look up position in table
        if zobrist_hash in self.table:
            score, stored_depth, flag, best_move = self.table[zobrist_hash]
            
            # Only use if stored depth is sufficient
            if stored_depth >= depth:
                self.hits += 1
                
                if flag == self.EXACT:
                    return (score, best_move)
                elif flag == self.LOWER_BOUND and score >= beta:
                    return (score, best_move)
                elif flag == self.UPPER_BOUND and score <= alpha:
                    return (score, best_move)
            
            # Even if depth is insufficient, return best move for move ordering
            if best_move:
                return (None, best_move)
        
        self.misses += 1
        return None
    
    def clear(self):
        self.table.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> dict:
        total_probes = self.hits + self.misses
        hit_rate = self.hits / total_probes if total_probes > 0 else 0
        
        return {
            'entries': len(self.table),
            'max_entries': self.max_entries,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }


class ChessEngine:
    # main engine - searches for best move
    
    def __init__(self, tt_size_mb: int = 64):
        self.evaluator = Evaluator()
        self.zobrist = ZobristHash()
        self.transposition_table = TranspositionTable(tt_size_mb)
        
        # Search statistics
        self.nodes_searched = 0
        self.cutoffs = 0
        self.tt_hits = 0
        self.search_start_time = 0
        self.max_time = 0
    
    def search(self, board: ChessBoard, max_depth: int = 5, max_time: float = 10.0) -> Tuple[Optional[tuple], int]:
        # search for best move with iterative deepening
        self.nodes_searched = 0
        self.cutoffs = 0
        self.tt_hits = 0
        self.search_start_time = time.time()
        self.max_time = max_time
        
        best_move = None
        best_score = float('-inf')
        
        # Iterative deepening: search at increasing depths
        # start shallow, go deeper each iteration
        for depth in range(1, max_depth + 1):
            # Check time limit
            if time.time() - self.search_start_time >= self.max_time:
                break
            
            current_best_move, current_score = self._search_root(board, depth)
            
            # Update best move if we completed the search at this depth
            if current_best_move:
                best_move = current_best_move
                best_score = current_score
                
                # Log progress (useful for debugging and analysis)
                elapsed = time.time() - self.search_start_time
                nps = self.nodes_searched / elapsed if elapsed > 0 else 0
                print(f"Depth {depth}: score={current_score}, "
                      f"nodes={self.nodes_searched}, nps={nps:.0f}, "
                      f"time={elapsed:.2f}s")
            
            # Stop if we found a forced checkmate
            if abs(current_score) > 90000:
                break
        
        return best_move, best_score
    
    def _search_root(self, board: ChessBoard, depth: int) -> Tuple[Optional[tuple], int]:
        # search from root position
        legal_moves = board.generate_moves(board.current_turn)
        
        if not legal_moves:
            return None, 0
        
        # Order moves for better pruning
        legal_moves = self._order_moves(board, legal_moves, depth)
        
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        for move in legal_moves:
            # Check time limit
            if time.time() - self.search_start_time >= self.max_time:
                break
            
            # Make move
            board_copy = board.copy()
            board_copy.make_move(move)
            
            # Search this position
            score = -self._alpha_beta(board_copy, depth - 1, -beta, -alpha, 1 - board.current_turn)
            
            # Update best move
            if score > best_score:
                best_score = score
                best_move = move
            
            # Update alpha
            alpha = max(alpha, score)
        
        # Store in transposition table
        zobrist_hash = self.zobrist.hash_position(board)
        self.transposition_table.store(
            zobrist_hash, depth, best_score, 
            TranspositionTable.EXACT, best_move
        )
        
        return best_move, best_score
    
    def _alpha_beta(self, board: ChessBoard, depth: int, alpha: int, beta: int, color: int) -> int:
        # minimax with alpha-beta pruning
        # this is the main search function
        self.nodes_searched += 1
        
        # Check time limit
        if time.time() - self.search_start_time >= self.max_time:
            return 0
        
        # Probe transposition table
        zobrist_hash = self.zobrist.hash_position(board)
        tt_entry = self.transposition_table.probe(zobrist_hash, depth, alpha, beta)
        if tt_entry and tt_entry[0] is not None:
            self.tt_hits += 1
            return tt_entry[0]
        
        # Terminal node: evaluate position
        if depth == 0:
            eval_score = self.evaluator.evaluate(board)
            # Return from perspective of current color
            return eval_score if color == ChessBoard.WHITE else -eval_score
        
        # Generate legal moves
        legal_moves = board.generate_moves(color)
        
        # Terminal node: checkmate or stalemate
        if not legal_moves:
            if board.is_checkmate(color):
                return -100000 - depth  # Prefer faster checkmates
            else:
                return 0  # Stalemate
        
        # Order moves for better pruning
        hash_move = tt_entry[1] if tt_entry else None
        legal_moves = self._order_moves(board, legal_moves, depth, hash_move)
        
        best_score = float('-inf')
        best_move = None
        original_alpha = alpha
        
        # Search all moves
        for move in legal_moves:
            # Make move
            board_copy = board.copy()
            board_copy.make_move(move)
            
            # Recursive search
            score = -self._alpha_beta(board_copy, depth - 1, -beta, -alpha, 1 - color)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            # Alpha-beta pruning - this is where the magic happens!
            alpha = max(alpha, score)
            if alpha >= beta:
                self.cutoffs += 1
                break  # cutoff - don't need to search more
        
        # Store in transposition table
        if best_score <= original_alpha:
            flag = TranspositionTable.UPPER_BOUND
        elif best_score >= beta:
            flag = TranspositionTable.LOWER_BOUND
        else:
            flag = TranspositionTable.EXACT
        
        self.transposition_table.store(zobrist_hash, depth, best_score, flag, best_move)
        
        return best_score
    
    def _order_moves(self, board: ChessBoard, moves: List[tuple], depth: int, hash_move: Optional[tuple] = None) -> List[tuple]:
        # order moves - search good moves first for better pruning
        # Assign priority to each move
        move_priorities = []
        
        for move in moves:
            priority = self.evaluator.evaluate_move_priority(board, move)
            
            # Bonus for hash move
            if hash_move and move == hash_move:
                priority += 1000000
            
            move_priorities.append((move, priority))
        
        # Sort by priority (descending)
        move_priorities.sort(key=lambda x: x[1], reverse=True)
        
        return [move for move, _ in move_priorities]
    
    def get_statistics(self) -> dict:
        elapsed = time.time() - self.search_start_time
        nps = self.nodes_searched / elapsed if elapsed > 0 else 0
        
        return {
            'nodes_searched': self.nodes_searched,
            'nodes_per_second': nps,
            'cutoffs': self.cutoffs,
            'tt_hits': self.tt_hits,
            'time_elapsed': elapsed,
            'tt_stats': self.transposition_table.get_stats()
        }
    
    def clear_transposition_table(self):
        self.transposition_table.clear()
