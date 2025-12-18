# CLI to play against the engine
# run this to play chess!

import sys
import time
from chess_board import ChessBoard
from chess_engine import ChessEngine
from evaluation import Evaluator


class ChessCLI:
    
    def __init__(self):
        self.board = ChessBoard()
        self.engine = ChessEngine(tt_size_mb=128)
        self.evaluator = Evaluator()
        self.game_over = False
        self.move_history_notation = []
    
    def print_banner(self):
        print("\n" + "="*60)
        print("   CHESS ENGINE - Student Project")
        print("   Features: Alpha-Beta Pruning, Transposition Tables,")
        print("   Iterative Deepening, Move Ordering")
        print("="*60 + "\n")
    
    def print_board(self):
        print("\n" + str(self.board))
        print()
    
    def print_game_status(self):
        turn = "White" if self.board.current_turn == ChessBoard.WHITE else "Black"
        print(f"Turn: {turn}")
        
        eval_score = self.evaluator.evaluate(self.board)
        print(f"Position Evaluation: {eval_score:+d} centipawns")
        
        if self.board.is_checkmate(self.board.current_turn):
            winner = "Black" if self.board.current_turn == ChessBoard.WHITE else "White"
            print(f"\n*** CHECKMATE! {winner} wins! ***\n")
            self.game_over = True
        elif self.board.is_stalemate(self.board.current_turn):
            print(f"\n*** STALEMATE! Game is a draw. ***\n")
            self.game_over = True
        elif self.board.halfmove_clock >= 50:
            print(f"\n*** FIFTY-MOVE RULE! Game is a draw. ***\n")
            self.game_over = True
    
    def parse_move(self, move_str: str):
        # convert e2e4 notation to coordinates
        move_str = move_str.strip().lower()
        
        if len(move_str) != 4:
            return None
        
        try:
            from_col = ord(move_str[0]) - ord('a')
            from_row = 8 - int(move_str[1])
            to_col = ord(move_str[2]) - ord('a')
            to_row = 8 - int(move_str[3])
            
            if not (0 <= from_row < 8 and 0 <= from_col < 8 and 
                   0 <= to_row < 8 and 0 <= to_col < 8):
                return None
            
            return ((from_row, from_col), (to_row, to_col))
        except:
            return None
    
    def move_to_notation(self, move: tuple) -> str:
        from_pos, to_pos = move
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        from_square = chr(ord('a') + from_col) + str(8 - from_row)
        to_square = chr(ord('a') + to_col) + str(8 - to_row)
        
        return from_square + to_square
    
    def get_player_move(self):
        legal_moves = self.board.generate_moves(self.board.current_turn)
        
        if not legal_moves:
            return None
        
        while True:
            print("\nEnter your move (e.g., e2e4), 'legal' to see legal moves, or 'quit' to exit:")
            user_input = input("> ").strip().lower()
            
            if user_input == 'quit':
                print("\nThanks for playing!")
                sys.exit(0)
            
            if user_input == 'legal':
                print("\nLegal moves:")
                for i, move in enumerate(legal_moves[:20], 1):  # Show first 20
                    print(f"  {self.move_to_notation(move)}", end="  ")
                    if i % 5 == 0:
                        print()
                if len(legal_moves) > 20:
                    print(f"\n  ... and {len(legal_moves) - 20} more")
                print()
                continue
            
            move = self.parse_move(user_input)
            
            if move is None:
                print("Invalid move format. Use algebraic notation (e.g., e2e4).")
                continue
            
            if move not in legal_moves:
                print("Illegal move. Try again or type 'legal' to see valid moves.")
                continue
            
            return move
    
    def get_engine_move(self, depth: int = 5, time_limit: float = 5.0):
        print(f"\nEngine thinking (depth={depth}, max_time={time_limit}s)...")
        
        start_time = time.time()
        best_move, score = self.engine.search(self.board, max_depth=depth, max_time=time_limit)
        elapsed = time.time() - start_time
        
        stats = self.engine.get_statistics()
        
        if best_move:
            print(f"Engine move: {self.move_to_notation(best_move)}")
            print(f"Evaluation: {score:+d} centipawns")
            print(f"Searched {stats['nodes_searched']:,} nodes in {elapsed:.2f}s "
                  f"({stats['nodes_per_second']:,.0f} nps)")
            print(f"TT hit rate: {stats['tt_stats']['hit_rate']:.1%}, "
                  f"Cutoffs: {stats['cutoffs']:,}")
        
        return best_move
    
    def play_human_vs_engine(self):
        self.print_banner()
        
        print("Choose your color:")
        print("1. Play as White (you move first)")
        print("2. Play as Black (engine moves first)")
        
        while True:
            choice = input("> ").strip()
            if choice == '1':
                player_color = ChessBoard.WHITE
                break
            elif choice == '2':
                player_color = ChessBoard.BLACK
                break
            else:
                print("Invalid choice. Enter 1 or 2.")
        
        print("\nChoose engine difficulty:")
        print("1. Easy (depth 3, 3s)")
        print("2. Medium (depth 4, 5s)")
        print("3. Hard (depth 5, 8s)")
        print("4. Expert (depth 6, 15s)")
        
        difficulty_settings = {
            '1': (3, 3.0),
            '2': (4, 5.0),
            '3': (5, 8.0),
            '4': (6, 15.0)
        }
        
        while True:
            choice = input("> ").strip()
            if choice in difficulty_settings:
                engine_depth, engine_time = difficulty_settings[choice]
                break
            else:
                print("Invalid choice. Enter 1-4.")
        
        print("\nGame starting!")
        self.print_board()
        
        while not self.game_over:
            self.print_game_status()
            
            if self.game_over:
                break
            
            if self.board.current_turn == player_color:
                # Player's turn
                move = self.get_player_move()
                if move is None:
                    break
            else:
                # Engine's turn
                move = self.get_engine_move(depth=engine_depth, time_limit=engine_time)
                if move is None:
                    print("Engine couldn't find a move (this shouldn't happen!)")
                    break
            
            # Make the move
            self.move_history_notation.append(self.move_to_notation(move))
            self.board.make_move(move)
            self.print_board()
        
        # Game over
        print("\nGame Over!")
        print(f"Moves played: {', '.join(self.move_history_notation)}")
    
    def play_engine_vs_engine(self):
        self.print_banner()
        print("Engine vs Engine Mode\n")
        
        print("Choose game speed:")
        print("1. Fast (depth 3, 2s per move)")
        print("2. Normal (depth 4, 5s per move)")
        print("3. Slow (depth 5, 10s per move)")
        
        speed_settings = {
            '1': (3, 2.0),
            '2': (4, 5.0),
            '3': (5, 10.0)
        }
        
        while True:
            choice = input("> ").strip()
            if choice in speed_settings:
                depth, time_limit = speed_settings[choice]
                break
            else:
                print("Invalid choice. Enter 1-3.")
        
        print("\nGame starting!")
        self.print_board()
        
        move_count = 0
        while not self.game_over and move_count < 100:  # Limit to 100 moves
            self.print_game_status()
            
            if self.game_over:
                break
            
            move = self.get_engine_move(depth=depth, time_limit=time_limit)
            if move is None:
                print("Engine couldn't find a move.")
                break
            
            self.move_history_notation.append(self.move_to_notation(move))
            self.board.make_move(move)
            self.print_board()
            
            move_count += 1
            time.sleep(0.5)  # Brief pause between moves
        
        print("\nGame Over!")
        print(f"Total moves: {move_count}")
        print(f"Move history: {', '.join(self.move_history_notation)}")
    
    def run(self):
        self.print_banner()
        
        print("Select game mode:")
        print("1. Play against the engine")
        print("2. Watch engine vs engine")
        print("3. Run benchmarks")
        print("4. Quit")
        
        while True:
            choice = input("> ").strip()
            
            if choice == '1':
                self.play_human_vs_engine()
                break
            elif choice == '2':
                self.play_engine_vs_engine()
                break
            elif choice == '3':
                print("\nRunning benchmarks...\n")
                from benchmark import PerformanceBenchmark
                benchmark = PerformanceBenchmark()
                benchmark.run_full_benchmark_suite()
                break
            elif choice == '4':
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Enter 1-4.")


def main():
    cli = ChessCLI()
    cli.run()


if __name__ == "__main__":
    main()
