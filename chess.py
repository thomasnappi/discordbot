import numpy as np
from PIL import Image
from random import randint
from math import ceil
# Used for type enforcement
from typing import List

# A Board is a list of 8 string lists, which have an 'X' every
# other entry making a checkerboard.  In the spaces between Xs, there
# can be 'B' for a black piece, 'W' for a white piece, 'BK' for a
# black king, or 'WK' for a white king.  White always starts from the
# top of the board and moves down; black always starts from the bottom
# of the board and moves up.
Board = List[List[str]]

# ############### #
# Global variabes #
# ############### #

assets = {
    "board" : np.array(Image.open("board.png"))[:,:,:3],
    "wt"    : np.array(Image.open("wt.png"))[:,:,:4],
    "wq"    : np.array(Image.open("wq.png"))[:,:,:4],
    "wb"    : np.array(Image.open("wb.png"))[:,:,:4],
    "wk"    : np.array(Image.open("wk.png"))[:,:,:4],
    "wr"    : np.array(Image.open("wr.png"))[:,:,:4],
    "wp"    : np.array(Image.open("wp.png"))[:,:,:4],
    "bt"    : np.array(Image.open("bt.png"))[:,:,:4],
    "bq"    : np.array(Image.open("bq.png"))[:,:,:4],
    "bb"    : np.array(Image.open("bb.png"))[:,:,:4],
    "bk"    : np.array(Image.open("bk.png"))[:,:,:4],
    "br"    : np.array(Image.open("br.png"))[:,:,:4],
    "bp"    : np.array(Image.open("bp.png"))[:,:,:4]
    }

# This is the standard opening chessboard.
# K is knight, T is unmoved king, t is moved king (relevant for castling), R is for unmoved rook, r is moved rook
start_board = [
    ['BR','BK','BB','BQ','BT','BB','BK','BR'],
    ['BP','BP','BP','BP','BP','BP','BP','BP'],
    ['  ','  ','  ','  ','  ','  ','  ','  '],
    ['  ','  ','  ','  ','  ','  ','  ','  '],
    ['  ','  ','  ','  ','  ','  ','  ','  '],
    ['  ','  ','  ','  ','  ','  ','  ','  '],
    ['WP','WP','WP','WP','WP','WP','WP','WP'],
    ['WR','WK','WB','WQ','WT','WB','WK','WR']
    ]

# ################# #
# REFERENCE METHODS #
# ################# #
def bcopy(cboard : Board) -> Board:
    b = [[],[],[],[],[],[],[],[]]
    for i in range(8):
        for j in range(8):
            b[i].append(cboard[i][j])
    # print(b)
    return b

def iavg(a : int, b : int) -> int:
    """ [iavg(a,b)] is the integer result of the average of two integers. """
    return round((a + b) / 2)

def enforce_color(color : str):
    """ [enforce_color(color)] asserts [color] is a valid color ('W' or 'B'). """
    assert(color != 'W' or color != 'B')

def opp_color(color : str):
    """ [opp_color(color)] returns the opposite color of [color]. """
    anticolor = None
    if color == 'W':
        anticolor = 'B'
    if color == 'B':
        anticolor = 'W'
    return anticolor

def in_bounds(n : int) -> bool:
    """ [in_bounds(n)] returns if [n] is within 0-7. """
    return n >= 0 and n < 8

def moves_to_readable(moves : List[str]) -> str:
    """ [moves_to_readable(moves)] turns a list of machine moves into a string of human-readable moves.
    TODO: Fix castling 
    TODO: Pawn to queen """
    c2s = {"0":"A","1":"B","2":"C","3":"D","4":"E","5":"F","6":"G","7":"H"}
    string = ""
    for i in moves:
        if i[0] != "K" and i[0] != "Q": # Not a castling move
            string = string + c2s[i[2]] + str(8-int(i[1])) + c2s[i[5]] + str(8-int(i[4])) + ", "
        elif i[0] == "K":
            string = string + "KINGSIDE_CASTLE, "
        elif i[0] == "Q":
            string = string + "QUEENSIDE_CASTLE, "
    if len(string) > 2:
        string = string[:-2]
    return string

def move_to_machine(moves : List[str], m : str) -> str:
    """ [move_to_machine(moves,m)] converts a standard move to machine location, if it is in the list of moves. """
    s2c = {"A":"0","B":"1","C":"2","D":"3","E":"4","F":"5","G":"6","H":"7"}
    try:
        if m.upper() == "KINGSIDE_CASTLE":
            for i in moves:
                if i == "K74:76,77:75" or i == "K04:06,07:05":
                    # print(i)
                    return i
        elif m.upper() == "QUEENSIDE_CASTLE":
            for i in moves:
                if i == "Q04:02,00:03" or i == "Q74:72,70:73":
                    # print(i)
                    return i
        else:
            partial = str(8 - int(m[1])) + s2c[m[0]] + ":" + str(8 - int(m[3])) + s2c[m[2]]
            # print(m)
            for i in moves:
                if i[1:] == partial:
                    return i
    except:
        print("Exception: " + m)
        pass
    return "Invalid move."

# ################## #
# BOARD MANIPULATION #
# ################## #
def move_piece(cboard : Board, move : str) -> Board:
    """ [move_piece(cboard,move)] executes the move [move] on [board], and returns the
        resulting board. 
        TODO: ADD SUPPORT FOR SPECIAL MOVES LIKE EN-PASSANT, CASTLING, ETC. """
    brd = bcopy(cboard)
    starty = int(move[1])
    startx = int(move[2])
    endy   = int(move[4])
    endx   = int(move[5])
    piece = cboard[starty][startx]
    for i in range(8):
        for j in range(8):
            if brd[i][j][1] == "p":
                print("Pawn unmarked")
                brd[i][j] = brd[i][j][0] + "P" # Mark this pawn as no longer "just moved"
    if piece[1] == "P" and ((starty - endy == 2) or (starty - endy == -2)): # Mark a pawn if it just moved 2
        print("Eligible pawn marked")
        piece = piece[0] + "p"
        # print("properly changed string of pawn moved")
    if piece[1] == "T": # Mark a king as having moved when it moves.
        print("Moved king marked.")
        piece = piece[0] + "t"
    if piece[1] == "R": # Mark the rook as having moved when it moves.
        print("Moved rook marked")
        piece = piece[0] + "r"
    # Currently only simple takes allowed
    if move[0] == "S" or move[0] == "C": # This is a "simple" move (S) or a "capture" move (C)
        brd[endy][endx] = piece
        brd[starty][startx] = '  '
    if move[0] == "E": # En passant moves
        brd[endy][endx] = piece
        brd[starty][endx] = '  '
        brd[starty][endy] = '  '
    if move[0] == "Q" or move[0] == "K": # Castle moves
        """K00:00,00:00"""
        brd[endy][endx] = piece
        brd[starty][startx] = '  '
        brd[int(move[10])][int(move[11])] = brd[int(move[7])][int(move[8])]
        brd[int(move[7])][int(move[8])]  = '  '
        # brd = move_piece(brd, "S"+move[7:]) # Move the rook
    # Upgrade pawns to queens
    for i in range(8):
        for j in range(8):
            if i == 0 and brd[i][j][0] == "W":
                brd[i][j] == "WQ"
            if i == 7 and brd[i][j][0] == "B":
                brd[i][j] == "BQ"
    return brd

# ################ #
# MOVE CALCULATION #
# ################ #
def pawn_moves(cboard,i,j):
    """ [pawn_moves(cboard,i,j)] calculates all moves for a pawn at (Y,X)=(i,j).
        TODO: ADD EN-PASSANT. """
    color = cboard[i][j][0]
    anticolor = opp_color(color)
    direction = None
    if color == "W":
        direction = -1
    else:
        direction = 1
    moves = []
    firstmove = (color == "W" and i == 6) or (color == "B" and i == 1) # Is it the pawn's first move?
    step2 = i + (2*direction) # Where we go if we move forward 2 (Y value)
    step1 = i + direction # Where we go if we move forward 1 (Y value)
    capleft = (i + direction),(j-1) # Where we go if we capture left (Y,X)
    capright = (i + direction),(j+1) # Where we go if we capture right (Y,X)
    if firstmove and cboard[step2][j] == '  ': # Can only jump forward two spaces if it's the first move
        moves.append("S{0}{1}:{2}{3}".format(i,j,step2,j))
    if in_bounds(step1) and cboard[step1][j] == '  ': # Check if we can move forward one
        moves.append("S{0}{1}:{2}{3}".format(i,j,step1,j))
    if in_bounds(capleft[0]) and in_bounds(capleft[1]) and cboard[capleft[0]][capleft[1]][0] == anticolor: # Check if we can capture to the right
        moves.append("C{0}{1}:{2}{3}".format(i,j,capleft[0],capleft[1]))
    if in_bounds(capright[0]) and in_bounds(capright[1]) and cboard[capright[0]][capright[1]][0] == anticolor: # Check if we can capture to the right
        moves.append("C{0}{1}:{2}{3}".format(i,j,capright[0],capright[1]))
    # En Passant rules
    print(capright,j)
    if in_bounds(capright[0]) and in_bounds(capright[1]) and  cboard[i][capright[1]][1] == 'p': # Don't need to worry much about color, since pawns can't hop 2 to the 5th rank
        moves.append("E{0}{1}:{2}{3}".format(i,j,capright[0],capright[1])) # We can en passant
    if in_bounds(capleft[0]) and in_bounds(capleft[1]) and  cboard[i][capleft[1]][1] == 'p':
        moves.append("E{0}{1}:{2}{3}".format(i,j,capleft[0],capleft[1])) # We can en passant
    return moves

def rook_moves(cboard,i,j):
    """ [rook_moves(cboard,i,j)] calculates all moves for a rook at (Y,X)=(i,j). """
    color = cboard[i][j][0]
    anticolor = opp_color(color)
    moves = []

    for m in range(1,8): # Calculate all downward moves
        ti = i+m
        tj = j
        if in_bounds(ti) and in_bounds(tj):
            if cboard[ti][tj][0] == anticolor: # Can we capture a piece here? (This also means we can't move further this way)
                moves.append("C{0}{1}:{2}{3}".format(i,j,ti,tj))
                break
            elif cboard[ti][tj] == '  ': # Can we move to a free space here?
                moves.append("S{0}{1}:{2}{3}".format(i,j,ti,tj))
            elif cboard[ti][tj][0] == color: # Are we blocked by our own piece here? (This means we can't move any further this way)
                break
            else: # There should be no case here; print something and let us know!
                print("RM1: INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(1,8): # Calculate all upward moves
        ti = i-m
        tj = j
        if in_bounds(ti) and in_bounds(tj):
            if cboard[ti][tj][0] == anticolor: # Can we capture a piece here? (This also means we can't move further this way)
                moves.append("C{0}{1}:{2}{3}".format(i,j,ti,tj))
                break
            elif cboard[ti][tj] == '  ': # Can we move to a free space here?
                moves.append("S{0}{1}:{2}{3}".format(i,j,ti,tj))
            elif cboard[ti][tj][0] == color: # Are we blocked by our own piece here? (This means we can't move any further this way)
                break
            else: # There should be no case here; print something and let us know!
                print("RM2: INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(1,8): # Calculate all rightward moves
        ti = i
        tj = j+m
        if in_bounds(ti) and in_bounds(tj):
            if cboard[ti][tj][0] == anticolor: # Can we capture a piece here? (This also means we can't move further this way)
                moves.append("C{0}{1}:{2}{3}".format(i,j,ti,tj))
                break
            elif cboard[ti][tj] == '  ': # Can we move to a free space here?
                moves.append("S{0}{1}:{2}{3}".format(i,j,ti,tj))
            elif cboard[ti][tj][0] == color: # Are we blocked by our own piece here? (This means we can't move any further this way)
                break
            else: # There should be no case here; print something and let us know!
                print("RM3: INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(1,8): # Calculate all leftward moves
        ti = i
        tj = j-m
        if in_bounds(ti) and in_bounds(tj):
            if cboard[ti][tj][0] == anticolor: # Can we capture a piece here? (This also means we can't move further this way)
                moves.append("C{0}{1}:{2}{3}".format(i,j,ti,tj))
                break
            elif cboard[ti][tj] == '  ': # Can we move to a free space here?
                moves.append("S{0}{1}:{2}{3}".format(i,j,ti,tj))
            elif cboard[ti][tj][0] == color: # Are we blocked by our own piece here? (This means we can't move any further this way)
                break
            else: # There should be no case here; print something and let us know!
                print("RM4: INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    return moves

def knight_moves(cboard,i,j):
    """ [knight_moves(cboard,i,j)] calculates all moves for a knight at (Y,X)=(i,j). """
    color = cboard[i][j][0]
    anticolor = opp_color(color)
    moves = []
    # Knights have 8 moves; to simplify, add them to a list and check them all
    pmoves = []
    pmoves.append((i-1,j+2))
    pmoves.append((i+1,j+2))
    pmoves.append((i-1,j-2))
    pmoves.append((i+1,j-2))
    pmoves.append((i-2,j+1))
    pmoves.append((i+2,j+1))
    pmoves.append((i-2,j-1))
    pmoves.append((i+2,j-1))
    for m in pmoves:
        ti = m[0]
        tj = m[1]
        if in_bounds(ti) and in_bounds(tj): # Check if the location is on the board
            if cboard[ti][tj][0] == anticolor: # Check if location is an enemy piece
                moves.append("C{0}{1}:{2}{3}".format(i,j,ti,tj))
            if cboard[ti][tj] == '  ': # Check if location is empty
                moves.append("S{0}{1}:{2}{3}".format(i,j,ti,tj))
    return moves

def bishop_moves(cboard,i,j):
    """ [bishop_moves(cboard,i,j)] calculates all moves for a knight at (Y,X)=(i,j). """
    color = cboard[i][j][0]
    anticolor = opp_color(color)
    moves = []
    for m in range(1,8): # Calculate all up-left moves
        ti = i-m
        tj = j-m
        if in_bounds(ti) and in_bounds(tj):
            if cboard[ti][tj][0] == anticolor: # Can we capture a piece here? (This also means we can't move further this way)
                moves.append("C{0}{1}:{2}{3}".format(i,j,ti,tj))
                break
            elif cboard[ti][tj] == '  ': # Can we move to a free space here?
                moves.append("S{0}{1}:{2}{3}".format(i,j,ti,tj))
            elif cboard[ti][tj][0] == color: # Are we blocked by our own piece here? (This means we can't move any further this way)
                break
            else: # There should be no case here; print something and let us know!
                print("BM1: INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(1,8): # Calculate all down-left moves
        ti = i+m
        tj = j-m
        if in_bounds(ti) and in_bounds(tj):
            if cboard[ti][tj][0] == anticolor: # Can we capture a piece here? (This also means we can't move further this way)
                moves.append("C{0}{1}:{2}{3}".format(i,j,ti,tj))
                break
            elif cboard[ti][tj] == '  ': # Can we move to a free space here?
                moves.append("S{0}{1}:{2}{3}".format(i,j,ti,tj))
            elif cboard[ti][tj][0] == color: # Are we blocked by our own piece here? (This means we can't move any further this way)
                break
            else: # There should be no case here; print something and let us know!
                print("BM2: INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(1,8): # Calculate all down-right moves
        ti = i+m
        tj = j+m
        if in_bounds(ti) and in_bounds(tj):
            if cboard[ti][tj][0] == anticolor: # Can we capture a piece here? (This also means we can't move further this way)
                moves.append("C{0}{1}:{2}{3}".format(i,j,ti,tj))
                break
            elif cboard[ti][tj] == '  ': # Can we move to a free space here?
                moves.append("S{0}{1}:{2}{3}".format(i,j,ti,tj))
            elif cboard[ti][tj][0] == color: # Are we blocked by our own piece here? (This means we can't move any further this way)
                break
            else: # There should be no case here; print something and let us know!
                print("BM3: INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(1,8): # Calculate all up-right moves
        ti = i-m
        tj = j+m
        if in_bounds(ti) and in_bounds(tj):
            if cboard[ti][tj][0] == anticolor: # Can we capture a piece here? (This also means we can't move further this way)
                moves.append("C{0}{1}:{2}{3}".format(i,j,ti,tj))
                break
            elif cboard[ti][tj] == '  ': # Can we move to a free space here?
                moves.append("S{0}{1}:{2}{3}".format(i,j,ti,tj))
            elif cboard[ti][tj][0] == color: # Are we blocked by our own piece here? (This means we can't move any further this way)
                break
            else: # There should be no case here; print something and let us know!
                print("BM4: INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    return moves

def queen_moves(cboard,i,j):
    """ [queen_moves(cboard,i,j)] calculates all moves for a queen at (Y,X)=(i,j). """
    return rook_moves(cboard,i,j) + bishop_moves(cboard,i,j)

def king_moves(cboard,i,j):
    """ [king_moves(cboard,i,j)] calculates all moves for a king at (Y,X)=(i,j). """
    color = cboard[i][j][0]
    anticolor = opp_color(color)
    moves = []
    pmoves = []
    pmoves.append((i-1,j-1))
    pmoves.append((i,j-1))
    pmoves.append((i+1,j-1))
    pmoves.append((i-1,j))
    pmoves.append((i+1,j))
    pmoves.append((i-1,j+1))
    pmoves.append((i,j+1))
    pmoves.append((i+1,j+1))
    for m in pmoves:
        ti = m[0]
        tj = m[1]
        if in_bounds(ti) and in_bounds(tj):
            if cboard[ti][tj] == anticolor: # Can we capture a piece here?
                moves.append("C{0}{1}:{2}{3}".format(i,j,ti,tj))
            elif cboard[ti][tj] == '  ': # Can we move to a free space here?
                moves.append("S{0}{1}:{2}{3}".format(i,j,ti,tj))
    # Castle rules
    if cboard[i][j][1] == "T": # Check that king is unmoved
        if in_bounds(j+1) and in_bounds(j+2) and in_bounds(j+3):
            if cboard[i][j+1] == '  ' and cboard[i][j+2] == '  ' and cboard[i][j+3] == color + "R":
                moves.append("K{0}{1}:{2}{3},{4}{5}:{6}{7}".format(i,j,i,j+2,i,j+3,i,j+1)) # Kingside castle
        if in_bounds(j-1) and in_bounds(j-2) and in_bounds(j-3) and in_bounds(j-4):
            if cboard[i][j-1] == '  ' and cboard[i][j-2] == '  ' and cboard[i][j-3] == '  ' and cboard[i][j-4] == color + "R":
                moves.append("Q{0}{1}:{2}{3},{4}{5}:{6}{7}".format(i,j,i,j-2,i,j-4,i,j-1)) # Queenside castle
    return moves

def valid_moves(cboard : Board, color : str) -> List[str]:
    """ [valid_moves(cboard,i,j)] calculates all moves for a color given a board. """
    moves = []
    for i in range(8):
        for j in range(8):
            c = cboard[i][j][0]
            piece = cboard[i][j][1].upper()
            if c == color:
                if piece == "P":
                    moves = moves + pawn_moves(cboard,i,j)
                elif piece == "R":
                    moves = moves + rook_moves(cboard,i,j)
                elif piece == "K":
                    moves = moves + knight_moves(cboard,i,j)
                elif piece == "B":
                    moves = moves + bishop_moves(cboard,i,j)
                elif piece == "Q":
                    moves = moves + queen_moves(cboard,i,j)
                elif piece == "T":
                    moves = moves + king_moves(cboard,i,j)
                else:
                    print("VM: INVALID PIECE AT Y={0},X={1}:{2}".format(i,j,cboard[i][j]))
    return moves

def in_check(cboard: Board, color : str, kingpos) -> bool:
    """ [in_check(cboard,color,kingpos)] returns if color is in check given the board layout
        and king position. """
    emoves = valid_moves(cboard, opp_color(color))
    for em in emoves:
        # print("({0},{1})=({2},{3})".format(em[4],em[5],kingpos[0],kingpos[1]))
        if int(em[4]) == kingpos[0] and int(em[5]) == kingpos[1]:
            return True
    return False

def valid_moves_wrap(cboard : Board, color : str) -> List[str]:
    """ [valid_moves_wrap(cboard,color)] returns moves and whether or not there is a tie
        or the game has been lost. """
    moves = valid_moves(cboard, color)
    ncmoves = []
    for move in moves:
        nb = move_piece(cboard, move)
        kingpos = [-1,-1]
        for i in range(8):
            for j in range(8):
                if nb[i][j].lower() == color.lower() + "t":
                    kingpos = [i,j]
                    break
            if kingpos != [-1,-1]:
                break
        if not in_check(nb,color,kingpos):
            ncmoves.append(move)
    if len(ncmoves) == 0:
        if in_check(cboard,color,kingpos):
            return {"moves":[],"state":color+" lost"}
        else:
            return {"moves":[],"state":"tied"}
    else:
        return {"moves":ncmoves,"state":"playing"}
            


# ################### #
# RENDERING FUNCTIONS #
# ################### #
def merge_pixels(lower : np.array, upper : np.array):
    """ [merge_pixels(lower, upper)] merges an upper pixel onto a lower pixel.
        Assumes that the lower pixel has 100% opaque, and returns an opaque output. """
    p = upper[3] / 255
    rd = (int(upper[0]) - int(lower[0]))
    gd = (int(upper[1]) - int(lower[1]))
    bd = (int(upper[2]) - int(lower[2]))
    r = (rd * p) + lower[0]
    g = (gd * p) + lower[1]
    b = (bd * p) + lower[2]
    return np.array([r,g,b])

def insert_image(y : int, x : int, brd : np.array, img : np.array):
    """ [insert_image(y,x,brd,img)] modifies 512x512 pixel array [brd] with 
        64x64 pixel square at [y],[x] as itself with 64x64 [img] flattened on it. """
    for i in range(64):
        for j in range(64):
            if img[i][j][3] != 0:
                brd[(y*64)+i][(x*64)+j] = merge_pixels(brd[(y*64)+i][(x*64)+j],img[i][j])

def render_board(cboard : Board) -> Image:
    """ [render_board(cboard)] renders an entire chess board. """
    global assets
    res = assets["board"].copy()
    for i in range(8):
        for j in range(8):
            if cboard[i][j] != '  ':
                insert_image(i,j,res,assets[cboard[i][j].lower()])
    return Image.fromarray(res)