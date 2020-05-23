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
    "board" : np.array(Image.open("board.png"))
    }

# This is the standard opening chessboard.
# K is knight, T is unmoved king, t is moved king (relevant for castling)
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
    # Currently only simple takes allowed
    if move[0] == "S" or move[0] == "C": # This is a "simple" move (S) or a "capture" move (C)
        brd[endy][endx] = brd[starty][startx]
        brd[starty][startx] = '  '
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
    return moves

def rook_moves(cboard,i,j):
    """ [rook_moves(cboard,i,j)] calculates all moves for a rook at (Y,X)=(i,j). """
    color = cboard[i][j][0]
    anticolor = opp_color(color)
    moves = []

    for m in range(8): # Calculate all downward moves
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
                print("INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(8): # Calculate all upward moves
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
                print("INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(8): # Calculate all rightward moves
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
                print("INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(8): # Calculate all leftward moves
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
                print("INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
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
            if cboardti][tj][0] == anticolor: # Check if location is an enemy piece
                moves.append("C{0}{1}:{2}{3}".format(i,j,ti,tj))
            if cboard[ti][tj] == '  ': # Check if location is empty
                moves.append("S{0}{1}:{2}{3}".format(i,j,ti,tj))
    return moves

def bishop_moves(cboard,i,j):
    """ [bishop_moves(cboard,i,j)] calculates all moves for a knight at (Y,X)=(i,j). """
    color = cboard[i][j][0]
    anticolor = opp_color(color)
    moves = []
    for m in range(8): # Calculate all up-left moves
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
                print("INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(8): # Calculate all down-left moves
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
                print("INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(8): # Calculate all down-right moves
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
                print("INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
        else: # If this is out of bounds, we can't move this way
            break
    for m in range(8): # Calculate all up-right moves
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
                print("INVALID PIECE AT Y={0},X={1}:{2}".format(ti,tj,cboard[ti][tj]))
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
    return moves

def valid_moves(cboard : Board, color : str) -> List[str]:
    """ [valid_moves(cboard,i,j)] calculates all moves for a color given a board.
        TODO: Add in restrictions on moving into/out of check. """
    moves = []
    for i in range(8):
        for j in range(8):
            c = cboard[i][j][0]
            piece = cboard[i][j][1]
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
                elif piece == "T" or piece == "t":
                    moves = moves + king_moves(cboard,i,j)
                else:
                    print("INVALID PIECE AT Y={0},X={1}:{2}".format(i,j,cboard[i][j]))
    return moves

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
    """ [render_board(cboard)] renders an entire chess board.
        TODO: UPDATE THIS FROM CHECKERS. """
    global assets
    res = assets["board"].copy()
    for i in range(8):
        for j in range(8):
            if cboard[i][j] == "W":
                insert_image(i,j,res,assets["w"])
            if cboard[i][j] == "B":
                insert_image(i,j,res,assets["b"])
            if cboard[i][j] == "WK":
                insert_image(i,j,res,assets["wk"])
            if cboard[i][j] == "BK":
                insert_image(i,j,res,assets["bk"])
    return Image.fromarray(res)