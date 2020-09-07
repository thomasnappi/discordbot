import discord, asyncio, random
from discord.ext import commands
from lof import *

class Lof(commands.Cog):
    def __init__(self, client):
        self.games = {}
        self.client = client
        # How many cards the player starts with
        self.num_cards = 5

    def owner_only():
        def is_owner(ctx):
            owners = []
            with open("owners.txt") as file:
                for i in file.readlines():
                    owners.append(int(i))
            return ctx.author.id in owners
        return commands.check(is_owner)

    def admin_only():
        def is_admin(ctx):
            return ctx.author.permissions_in(ctx.channel).administrator
        return commands.check(is_admin)

    @commands.command(name='ljoin', pass_context=True)
    async def join(self, ctx):
        """Join the game in this channel"""
        if not ctx.channel.id in self.games.keys():
            self.games[ctx.channel.id] = {
                "players": {},
                "order"  : [],
                "top"    : get_card(),
                "state"  : "unstarted"
            }
        g = self.games[ctx.channel.id]
        if ctx.author.id in g["players"].keys():
            await ctx.send("You are already in this game!")
        else:
            cards = []
            for i in range(self.num_cards):
                cards.append(get_card())
            g["players"][ctx.author.id] = cards
            await ctx.author.send("You have joined the lof game in {}!".format(ctx.channel.name))

    @commands.command(name='lstart', pass_context=True)
    async def start(self, ctx):
        """Start the game in this channel."""
        if not ctx.channel.id in self.games.keys():
            self.games[ctx.channel.id] = {
                "players": {},
                "order"  : [],
                "top"    : get_card(),
                "state"  : "unstarted"
            }
        g = self.games[ctx.channel.id]
        g["order"] = random.sample(g["players"].keys(),len(g["players"].keys()))
        for p in g["order"]:
            usr = self.client.get_user(p)
            sort_hand(g["players"][p])
            read_hand = ""
            for c in g["players"][p]:
                read_hand += print_card(c) + "\n"
            await usr.send("The game in {0} has started!  Your hand is:```\n{1}```".format(ctx.channel.name, read_hand))
        await ctx.send("It is {0}'s turn!  The top card is ***{1}***".format(self.client.get_user(g["order"][0]).mention, print_card(g['top'])))
        g["state"] = "in_progress"

    @commands.command(name='lplay', pass_context=True)
    async def play(self, ctx, *, card):
        """Play a card from your hand, on your turn."""
        if not ctx.channel.id in self.games.keys() or self.games[ctx.channel.id]['state'] != 'in_progress':
            await ctx.send("There is no game in progress!")
            return
        g = self.games[ctx.channel.id]
        if not ctx.author.id in g['players'].keys():
            await ctx.send("You are not in this game!")
            return
        elif g['order'][0] != ctx.author.id:
            await ctx.send("It is not your turn!")
            return
        card = get_card_of_hand(card, g["players"][ctx.author.id])
        if card == None or not can_play_over(card, g['top']):
            await ctx.send("You cannot play that card!  Check your direct messages to see your hand.")
            return
        g['top'] = remove_card_from_hand(card, g['players'][ctx.author.id])
        if card['value'] == 'reverse':
            # Reverse our ordering
            g['order'].reverse()
        else:
            # Rotate the first player to the back
            g['order'].append(g['order'].pop(0))
        if card['value'] == 'skip':
            await ctx.send(self.client.get_user(g["order"][0]).mention + " was skipped!")
            g['order'].append(g['order'].pop(0))
        elif card['value'] == 'draw2':
            await ctx.send(self.client.get_user(g["order"][0]).mention + " drew 2!")
            g['players'][g['order'][0]].append(get_card())
            g['players'][g['order'][0]].append(get_card())
            g['order'].append(g['order'].pop(0))
        elif card['value'] == 'draw4':
            await ctx.send(self.client.get_user(g["order"][0]).mention + " drew 4!")
            g['players'][g['order'][0]].append(get_card())
            g['players'][g['order'][0]].append(get_card())
            g['players'][g['order'][0]].append(get_card())
            g['players'][g['order'][0]].append(get_card())
            g['order'].append(g['order'].pop(0))
        if len(g['players'][ctx.author.id]) == 0:
            await ctx.send("{0} has won the game!".format(ctx.author.mention))
            self.games[ctx.channel.id] = {
                "players": {},
                "order"  : [],
                "top"    : get_card(),
                "state"  : "unstarted"
            }
            return
        else:
            await ctx.send("The top card is now ***{0}***.  It is {1}'s turn.".format(print_card(g['top']),self.client.get_user(g["order"][0]).mention))
            order = ''
            for p in g['order']:
                usr = self.client.get_user(p)
                order += ctx.guild.get_member(p).nick + " (" + usr.name + "#" + usr.discriminator + ") with " + str(len(g['players'][p])) + " cards\n"
            await ctx.send("The order of play is:\n```"+order+"```")
        for p in g["order"]:
            usr = self.client.get_user(p)
            sort_hand(g["players"][p])
            read_hand = ""
            for c in g["players"][p]:
                read_hand += print_card(c) + "\n"
            await usr.send("Your hand in {0} is:```\n{1}```".format(ctx.channel.name, read_hand))

    @commands.command(name='ldraw', pass_context=True)
    async def draw(self, ctx):
        """Draw a card, on your turn."""
        if not ctx.channel.id in self.games.keys() or self.games[ctx.channel.id]['state'] != 'in_progress':
            await ctx.send("There is no game in progress!")
            return
        g = self.games[ctx.channel.id]
        if not ctx.author.id in g['players'].keys():
            await ctx.send("You are not in this game!")
            return
        elif g['order'][0] != ctx.author.id:
            await ctx.send("It is not your turn!")
            return
        g['players'][ctx.author.id].append(get_card())
        g['order'].append(g['order'].pop(0))
        await ctx.send("It is now {0}'s turn.  The top card is still ***{1}***".format(self.client.get_user(g["order"][0]).mention, print_card(g['top'])))
        order = ''
        for p in g['order']:
            usr = self.client.get_user(p)
            order += ctx.guild.get_member(p).nick + " (" + usr.name + "#" + usr.discriminator + ") with " + str(len(g['players'][p])) + " cards\n"
        await ctx.send("The order of play is:\n```"+order+"```")
        for p in g["order"]:
            usr = self.client.get_user(p)
            sort_hand(g["players"][p])
            read_hand = ""
            for c in g["players"][p]:
                read_hand += print_card(c) + "\n"
            await usr.send("Your hand in {0} is:```\n{1}```".format(ctx.channel.name, read_hand))

    @commands.command(name='lorder', pass_context=True)
    async def order(self, ctx):
        if not ctx.channel.id in self.games.keys() or self.games[ctx.channel.id]['state'] != 'in_progress':
            await ctx.send("There is no game in progress!")
            return
        g = self.games[ctx.channel.id]
        order = ''
        for p in g['order']:
            usr = self.client.get_user(p)
            order += ctx.guild.get_member(p).nick + " (" + usr.name + "#" + usr.discriminator + ") with " + str(len(g['players'][p])) + " cards\n"
        await ctx.send("The order of play is:\n```"+order+"```")

    @commands.command(name='lrules', pass_context=True)
    async def rules(self, ctx):
        """Print the rules of the game."""
        await ctx.send("The goal of the game is to have no cards in your hand; when you play the last card in your hand, you win.  You may play cards of the same color on top of each other, or cards of the same value on top of each other; draw 4 cards and wildcards can be played on any card, and any card can be played on them.")

    @commands.command(name='lreset', pass_context=True)
    @admin_only()
    async def override(self, ctx):
        self.games[ctx.channel.id] = {
            "players": {},
            "order"  : [],
            "top"    : get_card(),
            "state"  : "unstarted"
        }
        await ctx.send("The current game has been forcibly ended.")

def setup(client):
    client.add_cog(Lof(client))