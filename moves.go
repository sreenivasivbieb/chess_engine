package main

const (
	WHITE = "white"
	BLACK = "black"
)


type Move struct{
    from string
	to string
	captured bool
	promoted bool
}
type state struct{
	data string
    next *state
	prev *state
}
func legal_display(x int,y int,turn string,){
     possible_moves :=[][2]int{
        {x+2,y+1},{x+2,y-1},{x-2,y-1},{x-2,y+1},{x+1,y+2},{x+1,y-2},{x-1,y+2},{x-1,y-2},
	 }
	 display_moves :=[][2]int{}
	 for _,move := possible_moves{
		 if move[0]>=0 && move[0]<8 && move[1]>=0 && move[1]<8{
			if turn==WHITE{
				if board[move[0]][move[1]]==" " || (board[move[0]][move[1]]>= "a" && board[move[0]][move[1]]<="z"){
					display_moves=append(display_moves,move)
				}
			}else{
				if board[move[0]][move[1]]==" " || (board[move[0]][move[1]]>= "A" && board[move[0]][move[1]]<="Z"){
					display_moves=append(display_moves,move)
				}
			}
	 }
}
 return Printboard(true,display_moves)}
func isWhite(p string) bool { return p >= "A" && p <= "Z" }
func isBlack(p string) bool { return p >= "a" && p <= "z" }
func white_all_moves()(map[[2]int][][2]int){
    place:=make(map[[][2]int][][2]int)
	res:=[]rune(board_sequence())
	row:=0
	col:=0
	for i:=0;i<len(res);i++{
		if res[i]=='/'{
			row++
			col=0
		}else if res[i]>='A' && res[i]<='Z'{
           
	       illegal_moves:=illegal_moves(row,col,WHITE)
           place[[2]int{row,col}]=illegal_moves
           col++
         }else if res[i]>='1' && res[i]<='8'{
              count:=int(res[i]-'0')
                col+=count
        }
		   
	}
    
	return place}
func black_all_moves()(map[[2]int][][2]int){
	place:=make(map[[2]int][][2]int)
	res:=[]rune(board_sequence())
	row:=0
	col:=0
	for i:=0;i<len(res);i++{
		if res[i]=='/'{
			row++
			col=0
		}else if res[i]>='a' && res[i]<='z'{
		   illegal_moves :=illegal_moves(row,col,BLACK)
           place[[2]int{row,col}]=illegal_moves
           col++
        
		}else if res[i]>='1' && res[i]<='8'{
              count:=int(res[i]-'0')
                col+=count
        }}
		return place}
func illegal_moves(x, y int, turn string) [][2]int {
    piece := board[x][y]
    possible_moves := [][2]int{}

    add := func(i, j int) {
        if i >= 0 && i < 8 && j >= 0 && j < 8 {
            possible_moves = append(possible_moves, [2]int{i, j})
        }
    }
   
    switch piece {
    case "P":
        
        if x == 6   {
            add(x-2, y)
        }
        if board[x-1][y] == " "{
            add(x-1, y)
        }
        

    case "p":
         if x == 1   && (board[x-2][y] == " "  || (board[x-2][y] >= "A" && board[x-2][y] <= "Z")) {
            add(x+2, y)
        }
        if board[x-1][y] == " " || (board[x-1][y] >= "A" && board[x-1][y] <= "Z") {
            add(x+1, y)
        }
    case "R", "r":
        
        dirs := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}} // down, up, right, left
        for _, d := range dirs {
           for i, j := x+d[0], y+d[1]; i >= 0 && i < 8 && j >= 0 && j < 8; i, j = i+d[0], j+d[1] {
           piece := board[i][j]

           if piece == " " { // empty square
              add(i, j)
              continue
            }

        // Capture enemy piece
           if (turn == WHITE && isBlack(piece)) || (turn == BLACK && isWhite(piece)) {
               add(i, j)
            }

            break // stop after hitting any piece (own or enemy)
    }
}

        

    case "N", "n":
        deltas := [][2]int{{2, 1}, {2, -1}, {-2, -1}, {-2, 1}, {1, 2}, {1, -2}, {-1, 2}, {-1, -2}}
        for _, d := range deltas {
            if !(x+d[0] >= 0 && x+d[0] < 8) ||!(y+d[1] >= 0 && y+d[1] < 8){
                continue
            }
            if (turn == WHITE && (board[x+d[0]][y+d[1]] == " " || (board[x+d[0]][y+d[1]] >= "a" && board[x+d[0]][y+d[1]] <= "z"))) ||
                (turn == BLACK && (board[x+d[0]][y+d[1]] == " " || (board[x+d[0]][y+d[1]] >= "A" && board[x+d[0]][y+d[1]] <= "Z"))) {
            add(x+d[0], y+d[1])
        }}

    case "B", "b", "Q", "q":
        dirs := [][2]int{{1, 1}, {-1, -1}, {1, -1}, {-1, 1}}
        if piece == "Q" || piece == "q" {
            dirs = append(dirs, [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}...)
        }
        for _, d := range dirs {
            for i, j := x+d[0], y+d[1]; i >= 0 && i < 8 && j >= 0 && j < 8; i, j = i+d[0], j+d[1] {
                if board[i][j] != " " {
                    if (turn == WHITE && isBlack(board[i][j]))
                        (turn == BLACK && isBlack(board[i][j]) ) {
                        add(i, j)
                    }
                    break
                }
                add(i, j)
              }
            }
        

    case "K", "k":
        deltas := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}, {1, 1}, {1, -1}, {-1, 1}, {-1, -1}}
        for _, d := range deltas {

            add(x+d[0], y+d[1])
        }
    }

    return possible_moves
}
func king_in_check(turn string, x int, y int,board [][]string)bool{
    //check for knight attacks
    knight_moves := [][2]int{{2, 1}, {2, -1}, {-2, -1}, {-2, 1}, {1, 2}, {1, -2}, {-1, 2}, {-1, -2}}
    for _,move := range knight_moves{
        nx, ny := x+move[0], y+move[1]
        if nx<0 || nx>=8 || ny<0 || ny>=8{
            continue
        }
        piece := board[nx][ny]
        if (turn == WHITE && piece == "n") || (turn == BLACK && piece == "N") {
            return true
        }
    }

    //check for pawn attacks 
    if turn == WHITE {
        pawn_attacks= [][2]int{{-1, -1}, {-1, 1}}
        for _,move :=range pawn_attacks{
            nx, ny := x+move[0], y+move[1]
            if nx<0 || nx>=8 || ny<0 || ny>=8{
                continue}
            piece := board[nx][ny]
            if piece == "p" {
                return true}
        }
    }else{
        pawn_attacks= [][2]int{{1, -1}, {1, 1}}
        for _,move :=range pawn_attacks{
            nx, ny := x+move[0], y+move[1]
            if nx<0 || nx>=8 || ny<0 || ny>=8{
                continue}
            piece := board[nx][ny]
            if piece == "P" {
                return true}
        }
    }
        

    //check for rook/queen attacks (horizontal and vertical)
    h_v_dirs := [][2]int{{1,0},{-1,0},{0,1},{0,-1}}
    for _,dir := range h_v_dirs{
        for i,j := x+dir[0], y+dir[1]; i>=0 && i<8 && j>=0 && j<8; i,j = i+dir[0], j+dir[1]{
            piece:= board[i][j]
            if turn == WHITE && (piece == "R" || piece == "Q") {
                return true}
            if turn == BLACK && (piece == "r" || piece == "q") {
                return true}}}
      
    //check for bisihop/queen attacks (diagnols)
    diag_dirs := [][2]int{{1,1},{1,-1},{-1,1},{-1,-1}}
    for _,dir := range diag_dirs{
        for i,j := x+dir[0], y+dir[1]; i>=0 && i<8 && j>=0 && j<8; i,j = i+dir[0], j+dir[1]{
            piece:= board[i][j]
            if turn == WHITE && (piece == "B" || piece == "Q") {
                return true}
            if turn == BLACK && (piece == "b" || piece == "q") {
                return true}
        }
    }
    // check for king attacks
    king_moves := [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}, {1, 1}, {1, -1}, {-1, 1}, {-1, -1}}
    for _,move := range king_moves{
        nx, ny := x+move[0], y+move[1]
        if nx<0 || nx>=8 || ny<0 || ny>=8{ 
            continue
        }
        piece := board[nx][ny]
        if (turn == WHITE && piece == "k") || (turn == BLACK && piece == "K") {
            return true
        }}
    return false
}
func legal_moves(possible_moves [][2]int, turn string,piece string,x int, y int)[][2]int{
    legal_moves := [][2]int{}
    for _, move := range possible_moves {
          
    }
        
}


func all_moves(turn string)([][]Move){
	  positions:=make(map[[][2]int][][2]int)
	  
        if turn==WHITE{
			positions=white_all_moves()
		}else{
			positions=black_all_moves()
		}
        llegal_moves :=make(map[string][]string)
      for from, to_list := range positions {
             for _, to := range to_list {
                    piece := board[from[0]][from[1]]
                    copy:=board
                    copy[to[0]][to[1]]=piece
                    copy[from[0]][from[1]]=" "
                    if king_in_check(turn,from[0],from[1],copy){
                        continue    
                    }
                    llegal_moves[IndexToAlpha(from[0],from[1])]=append(llegal_moves[IndexToAlpha(from[0],from[1])],IndexToAlpha(to[0],to[1]))
				
             }
            }
            
        
 }
