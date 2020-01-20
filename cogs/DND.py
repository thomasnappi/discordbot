import discord,asyncio,io,random,requests
from discord.ext import commands
from bs4 import BeautifulSoup

class DND(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="dperc",aliases=["percent","d100","roll100"])
    async def dperc(self,ctx):
        """Rolls a percent die"""
        await ctx.send("```markdown\n[You rolled]({}%)```".format(random.randint(1,100)))

    @commands.command(name="d20",aliases=["roll20"],pass_context=True)
    async def d20(self,ctx):
        """Rolls a d20"""
        await ctx.send("```markdown\n[You rolled]({})```".format(random.randint(1,20)))

    @commands.command(name="d12",aliases=["roll12"],pass_context=True)
    async def d12(self,ctx):
        """Rolls a d12"""
        await ctx.send("```markdown\n[You rolled]({})```".format(random.randint(1,12)))

    @commands.command(name="d10",aliases=["roll10"],pass_context=True)
    async def d10(self,ctx):
        """Rolls a d10"""
        await ctx.send("```markdown\n[You rolled]({})```".format(random.randint(1,10)))

    @commands.command(name="d8",aliases=["roll8"],pass_context=True)
    async def d8(self,ctx):
        """Rolls a d8"""
        await ctx.send("```markdown\n[You rolled]({})```".format(random.randint(1,8)))

    @commands.command(name="d6",aliases=["dice","roll6"],pass_context=True)
    async def d6(self,ctx):
        """Rolls a d6"""
        await ctx.send("```markdown\n[You rolled]({})```".format(random.randint(1,6)))

    @commands.command(name="d4",aliases=["roll4"],pass_context=True)
    async def d4(self,ctx):
        """Rolls a d4"""
        await ctx.send("```markdown\n[You rolled]({})```".format(random.randint(1,4)))

    @commands.command(name="cflip",aliases=["coinflip","penny","flip","d2","roll2"],pass_context=True)
    async def cflip(self,ctx):
        """Flips a coin"""
        if random.randint(0,1) == 1:
            await ctx.send("```markdown\n[You got](HEADS)```")
        else:
            await ctx.send("```markdown\n[You got](TAILS)```")

    @commands.command(name="spellinfo",pass_context=True)
    async def spellinfo(self,ctx,*,spell):
        """Displays information abot spells from 5thsrd.org"""
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' }
        url = "https://5thsrd.org/spellcasting/spells/{}/".format("_".join(spell.lower().split(" ")))
        req = requests.get(url,headers=headers)
        div = BeautifulSoup(req.text.replace("<br>","\n"),"html.parser").find("div",role="main")
        string = ""
        for i in div.find_all("p"):
            string = "{0}{1}\n".format(string,i.text)
        rellines = string.split("\n")
        rellines.insert(0,"**{}**".format(div.find("h1").text))
        rellines[1] = "*{}*".format(rellines[1])
        while len(rellines) > 0:
            ts = rellines.pop(0)
            for i in range(len(rellines)):
                if len(ts + rellines[0]) > 2000:
                    break
                else:
                    ts = ts + "\n" + rellines.pop(0)
            await ctx.send(ts)

def setup(client):
    client.add_cog(DND(client))