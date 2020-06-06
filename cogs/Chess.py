import discord,asyncio,io,json
from discord.ext import commands
from chess import *

class Chess(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.games = {}
        self.boardsel = {}

    @commands.command()
    async def cjoin(self,ctx,color):
        """ Join a game of chess, with a color black or white. """
        cid = ctx.channel.id
        c = color.lower()
        if c == "white" or c == "w":
            color = "W"
            c = "white"
        elif c == "black" or c == "black":
            color = "B"
            c = "black"
        else:
            await ctx.send("Color must be black or white.")
            return
        
        if not cid in self.games.keys() or self.games[cid] == None:
            self.games[cid] = {"B":-1,"W":-1,"board":bcopy(start_board),"turn":"pre","lm":"None"}
        # if self.games[cid]["W"] == ctx.author.id or self.games[cid]["B"] == ctx.author.id:
        #     await ctx.send("You cannot join the game twice!")
        #     return
        if self.games[cid][color] != -1:
            await ctx.send("That color has already been claimed.")
            return
        
        self.games[cid][color] = ctx.author.id
        await ctx.send("{0} has joined the game as {1}".format(ctx.author.mention,c))

    @commands.command()
    async def cboard(self,ctx,target):
        """ Change the current board image between the standard one and a fun one, with "reg" or "asl". """
        if target.lower() == "asl":
            self.boardsel[ctx.guild.id] = "asl"
            # print("asl")
        elif target.lower() == "reg":
            self.boardsel[ctx.guild.id] = "reg"
            # print("reg")
        else:
            await ctx.send("Invalid name; use reg or asl.")

    @commands.command()
    async def cstart(self,ctx):
        """ Start a chess game after two players have joined. """
        cid = ctx.channel.id
        if not cid in self.games.keys():
            await ctx.send("No game set up!")
            return
        if self.games[cid]["W"] == -1 or self.games[cid]["B"] == -1:
            await ctx.send("Not enough players!")
            return
        self.games[cid]["turn"] = "W"
        bs = ""
        if not ctx.guild.id in self.boardsel.keys():
            bs = "reg"
        else:
            bs = self.boardsel[ctx.guild.id]
        b = render_board(self.games[cid]["board"],bs)
        moves = moves_to_readable(valid_moves_wrap(self.games[cid]["board"],"W")["moves"])
        if self.games[cid]["turn"] == "W":
            moves = "White to move.  Possible moves: " + moves
        else:
            moves = "Black to move. Possible moves: " + moves
        with io.BytesIO() as output: # Send the image in discord
            b.save(output,format="PNG")
            output.seek(0)
            await ctx.send(moves,file=discord.File(output,filename="img.png"))

    @commands.command()
    async def cmove(self,ctx,move):
        """ Move a piece in chess, using the standard chess move notation, ex. A2A4. """
        cid = ctx.channel.id
        if not cid in self.games.keys(): # Ensure there is a game
            await ctx.send("No game in progress!")
            return
        turn = self.games[cid]["turn"]
        if turn == "pre":
            await ctx.send("The game has not started yet!")
            return
        if self.games[cid][turn] != ctx.author.id: # Ensure there are players
            await ctx.send("It is not your turn!")
            return

        
        # Try to move the way the player has specified
        pmresp = valid_moves_wrap(self.games[cid]["board"],turn)
        mm = move_to_machine(pmresp["moves"],move.upper())
        if mm == "Invalid move.":
            await ctx.send("Invalid move; your possible moves are {}".format(moves_to_readable(pmresp["moves"])))
            return
        self.games[cid]["board"] = move_piece(self.games[cid]["board"],mm)
        bs = ""
        if not ctx.guild.id in self.boardsel.keys():
            bs = "reg"
        else:
            bs = self.boardsel[ctx.guild.id]
        b = render_board(self.games[cid]["board"],bs)

        # Add who moved what to the image message
        msg = ""
        if turn == "W":
            msg = "White moved {0}.  It is now <@{1}>'s turn".format(move,self.games[cid]["B"])
        else:
            msg = "Black moved {0}.  It is now <@{1}>'s turn".format(move,self.games[cid]["W"])
        # msg = msg + ". It is now <@{}>'s turn".format()
        # Send the rendered board in discord
        with io.BytesIO() as output:
            b.save(output,format="PNG")
            output.seek(0)
            await ctx.send(msg,file=discord.File(output,filename="img.png"))

        self.games[cid]["turn"] = opp_color(turn) # Change whose turn it is
        self.games[cid]["lm"] = move
        kingpos = [-1,-1]
        for i in range(8):
            for j in range(8):
                if self.games[cid]["board"][i][j].lower() == opp_color(turn).lower() + "t":
                    kingpos = [i,j]
                    break
            if kingpos != [-1,-1]:
                break
        if in_check(self.games[cid]["board"],opp_color(turn),kingpos):
            await ctx.send("Check!")

        # Check if the game is over
        mresp = valid_moves_wrap(self.games[cid]["board"],opp_color(turn))
        if mresp["state"] != "playing":
            if mresp["state"] == "tied":
                await ctx.send("The game tied!")
                self.games[cid] = None
            else:
                await ctx.send("{} won the game!".format(ctx.author.mention))
                self.games[cid] = None

    @commands.command()
    async def cprint(self,ctx):
        """ Print the current chessboard, and the last move. """
        cid = ctx.channel.id
        if not cid in self.games.keys():
            await ctx.send("No game in progress!")
            return
        bs = ""
        if not ctx.guild.id in self.boardsel.keys():
            bs = "reg"
        else:
            bs = self.boardsel[ctx.guild.id]
        b = render_board(self.games[cid]["board"],bs)
        move = self.games[cid]["lm"]
        msg = ""
        try:
            if self.games[cid]["turn"] == "W":
                msg = "White moved {}.".format(move)
            else:
                msg = "Black moved {}.".format(move)
        except:
            pass
        # Send the rendered board in discord
        with io.BytesIO() as output:
            b.save(output,format="PNG")
            output.seek(0)
            await ctx.send(msg,file=discord.File(output,filename="img.png"))

    @commands.command()
    async def cexp(self,ctx):
        """ Export current game. """
        try:
            await ctx.send(json.dumps(self.games[ctx.channel.id]))
        except:
            await ctx.send("No game in progress.")
        # await ctx.send(json.dumps(self.games[ctx.channel.id]))

    @commands.command()
    async def cimp(self,ctx,*,all):
        """ Import a game from string. """
        self.games[ctx.channel.id] = json.loads(all)

    @commands.command()
    async def cforfeit(self,ctx):
        """ Forfeit a game of chess. """
        cid = ctx.channel.id
        if not cid in self.games.keys(): # Ensure there is a game
            await ctx.send("No game in progress!")
            return
        if self.games[cid]["W"] == ctx.author.id or self.games[cid]["B"] == ctx.author.id:
            self.games[cid] = None
            await ctx.send("{} has forfeit the game!".format(ctx.author.mention))
        else:
            await ctx.send("You can't forfeit a game you aren't a part of!")

    @commands.command()
    async def crules(self,ctx):
        """ Print the rules of chess. """
        await ctx.send("The rules are the same as standard chess.")

def setup(client):
    client.add_cog(Chess(client))