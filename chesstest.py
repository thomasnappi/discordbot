from chess import *
tboard = [
    ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "], 
    ["  ", "  ", "  ", "WP", "  ", "  ", "  ", "  "], 
    ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "], 
    ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "], 
    ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "], 
    ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "], 
    ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "], 
    ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "]
    ]
pretty_print_board(tboard)
vmoves = valid_moves_wrap(tboard,"W")["moves"]
print(moves_to_readable(vmoves))
move = input("> ")
mmove = move_to_machine(vmoves, move)
print(mmove)
pretty_print_board(move_piece(tboard,mmove))
"""
[
    ['BR', 'BK', 'BB', 'BQ', 'BT', 'BB', 'BK', 'BR'], 
    ['  ', 'BP', '  ', 'BP', 'BP', 'BP', 'BP', 'BP'], 
    ['BP', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
    ['  ', 'WP', 'BP', '  ', '  ', '  ', '  ', '  '], 
    ['  ', '  ', 'Wp', '  ', '  ', '  ', '  ', '  '], 
    ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '], 
    ['WP', '  ', '  ', 'WP', 'WP', 'WP', 'WP', 'WP'], 
    ['WR', 'WK', 'WB', 'WQ', 'WT', 'WB', 'WK', 'WR']
]
"""
# colordict = {"red":(255,0,0),"green":(0,255,0),"blue":(0,0,255),"yellow":(255,255,0),"purple":(255,0,255),"black":(0,0,0),"white":(255,255,255)}
# color = 'red'
# if color in colordict.keys():
#     color = colordict[color]
# else:
#     try:
#         c = color[1:].split(",")
#         color = (int(c[0]),int(c[1]),int(c[2][:-1]))
#     except:
#         print("Malformed.")
# try:
#     im = np.array(Image.open("place.png"))
#     im[y][x] = color
#     im2 = Image.fromarray(im)
#     im2.save("place.png")
#     print("success")
# except:
#     print("Error updating file.")