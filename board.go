package main

import ("fmt";
         "strings")
var board= [][]string{
	{"R","N","B","Q","K","B","N","R"},
	{"P","P","P","P","P","P","P","P"},
	{" "," "," "," "," "," "," "," "},
	{" "," "," "," "," "," "," "," "},
	{" "," "," "," "," "," "," "," "},
	{" "," "," "," "," "," "," "," "},
	{"p","p","p","p","p","p","p","p"},
	{"r","n","b","q","k","b","n","r"},
}
func board_sequence()string{
	var sb strings.Builder
	for i:=0;i<8;i++{
		count:=0
		for j:=0;j<8;j++{
			if board[i][j]== " "{
				count++;
				continue
			}
			if count>0{
				sb.WriteString(fmt.Print(count))}
			sb.WriteString(fmt.Print(board[i][j]))
			count=0
		}
		if count>0 {
			sb.WriteString(fmt.Print(count))
		}
		sb.WriteString(fmt.Print("/"))
	}
	return sb.String()
}
func Printboard(flag bool,display_moves [][2]int){
	for i:=0;i<8;i++{
		for j:=0;j<8;j++{
			for _,move :=range display_moves{
			if flag && i==move[0] && j==move[1]{
				if board[i][j]!=" "{
					fmt.Println("kill", " ")
				}else{ 
					fmt.Print("*"," ")
				}
			continue }

			fmt.Print(board[i][j], " ")
		}
		fmt.Println()
}}}
func IndexToAlpha(x int,y int)string{
	a:=string(rune('a'+y))

	b:=string(rune('8'-x))
	return a+b
}
func  AlphaToIndex(pos string)(int,int){
	a:=[]rune(pos)
	x:=int('8'-a[1])
	y:=int(a[0]-'a')
	return x,y
}


func main(){
	fmt.Println(IndexToAlpha(0,0))
    
}