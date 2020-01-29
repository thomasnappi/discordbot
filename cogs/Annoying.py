import discord, asyncio
from discord.ext import commands

class Annoying(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="remind",aliases=["nag","bother"],pass_context=True)
    @commands.guild_only()
    async def remind(self, ctx, user: discord.Member, hours: float, *, message: str):
        """ Pings the user in this channel with the specified message after a certain number of hours (fractions supported)"""
        if len(message) > 150:
            await ctx.send("Sorry, that message is too long. Messages must be less than 150 characters.")
        await ctx.send("Timer set; in {0} hours I will ping {1.name} here to tell them {2}".format(hours,user,message))
        await asyncio.sleep(round(3600 * hours))
        await ctx.send("{0.mention}, {1.author.name}#{1.author.discriminator} asked me {2} hours ago to tell you {3}".format(user,ctx,hours,message))

def setup(client):
    client.add_cog(Annoying(client))