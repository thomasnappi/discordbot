import discord,asyncio,io
from discord.ext import commands
from chess import *

class Chess(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.games = {}

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
        
        if not cid in self.games.keys():
            self.games[cid] = {"B":-1,"W":-1,"board":bcopy(start_board),"turn":"pre"}
        if self.games[cid]["W"] == ctx.author.id or self.games[cid]["B"] == ctx.author.id:
            await ctx.send("You cannot join the game twice!")
            return
        if self.games[cid][color] != -1:
            await ctx.send("That color has already been claimed.")
            return
        
        self.games[cid][color] = ctx.author.id
        await ctx.send("{0} has joined the game as {1}".format(ctx.author.mention,c))

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
        b = render_board(self.games[cid]["board"])
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
        b = render_board(self.games[cid]["board"])

        # Add who moved what to the image message
        msg = ""
        if turn == "W":
            msg = "White moved {}.".format(move)
        else:
            msg = "Black moved {}.".format(move)

        # Send the rendered board in discord
        with io.BytesIO() as output:
            b.save(output,format="PNG")
            output.seek(0)
            await ctx.send(msg,file=discord.File(output,filename="img.png"))

        self.games[cid]["turn"] = opp_color(turn) # Change whose turn it is

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
        b = render_board(self.games[cid]["board"])
        msg = ""
        if self.games[cid]["turn"] == "W":
            msg = "White moved {}.".format(move)
        else:
            msg = "Black moved {}.".format(move)
        # Send the rendered board in discord
        with io.BytesIO() as output:
            b.save(output,format="PNG")
            output.seek(0)
            await ctx.send(msg,file=discord.File(output,filename="img.png"))


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

def setup(client):
    client.add_cog(Chess(client))