import discord,asyncio,io,random,datetime
from datetime import timezone
import numpy as np
import matplotlib.pyplot as plt
from discord.ext import commands

class Activity(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mstats = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Beginning message load...")
        servers = self.client.guilds
        for i in range(len(servers)):
            server = servers[i]
            self.mstats[server.id] = {}
            print("Loading server {0} of {1}: {2.name}".format(i+1,len(servers),server))
            channels = server.text_channels
            for j in range(len(channels)):
                channel = channels[j]
                async for msg in channel.history(limit=50000000):
                    if msg.author.bot:
                        1 == 1
                    elif not msg.author.id in self.mstats[server.id]:
                        self.mstats[server.id][msg.author.id] = 1
                    else:
                        self.mstats[server.id][msg.author.id] = self.mstats[server.id][msg.author.id] + 1
        print("Loading all done!")

    @commands.Cog.listener()
    async def on_message(self,message):
        uid = message.author.id
        if message.guild != None and not message.author.bot:
            gid = message.guild.id
            if not gid in self.mstats:
                self.mstats[gid] = {}
            if not uid in self.mstats[gid]:
                self.mstats[gid][uid] = 1
            else:
                self.mstats[gid][uid] = self.mstats[gid][uid] + 1
        
    
    @commands.command(name="myscore",pass_context=True)
    @commands.guild_only()
    async def myscore(self,ctx):
        """Returns your activity in the server"""
        if ctx.guild != None and ctx.guild.id in self.mstats and ctx.author.id in self.mstats[ctx.guild.id]:
            await ctx.send("Your score in {0.guild.name} is {1}".format(ctx,self.mstats[ctx.guild.id][ctx.author.id]))
        else:
            print("gid: {0.guild.id} type(self.mstats): {1} self.mstats.keys() {2}".format(ctx,type(self.mstats),self.mstats.keys()))
        return

    @commands.command(name="leaderboard",pass_context=True)
    @commands.guild_only()
    async def leaderboard(self,ctx):
        """Returns top 10 active users in the server"""
        if ctx.guild != None and ctx.guild.id in self.mstats and ctx.author.id in self.mstats[ctx.guild.id]:
            msg = "Leaderboard for {0.guild.name}".format(ctx)
            limit = 0
            lis = sorted(self.mstats[ctx.guild.id].items(), key = lambda ms:(ms[1], ms[0]))
            lis.reverse()
            for i in lis:
                limit = limit + 1
                u = ctx.guild.get_member(i[0])
                prefix = "th"
                if limit == 1:
                    prefix = "st"
                elif limit == 2:
                    prefix = "nd"
                elif limit == 3:
                    prefix = "rd"
                if u != None:
                    msg = msg + "\n{0}{1}: {2.name}#{2.discriminator} with {3} messages".format(limit,prefix,u,i[1])
                else:
                    limit = limit - 1
                if limit == 10:
                    break
            await ctx.send(msg)
        else:
            print("gid: {0.guild.id} type(self.mstats): {1}".format(ctx,type(self.mstats)))
        return
    
    @commands.command(name="activity",pass_context=True)
    async def activity(self,ctx):
        """Displays a histogram of activity in the channel"""
        if ctx.guild != None and not ctx.author.permissions_in(ctx.channel).administrator:
            await ctx.author.send("You must be an administrator to use `activity`.")
            return
        times = []
        count = 0
        async for i in ctx.history(limit=500000000):
            ltime = i.created_at
            times.append(ltime.hour)
            count = count + 1
        tar = np.array(times)
        plt.figure()
        plt.xlabel("Hour (UTC)")
        plt.ylabel("Number of messages")
        plt.xlim(0,24)
        numbers=[x for x in range(0,24)]
        labels=map(lambda x: str(x), numbers)
        plt.xticks(numbers, labels)
        plt.hist(tar,bins=24)
        plt.title("Activity over the last {0} messages in {1.channel.name}".format(count,ctx))
        with io.BytesIO() as buf:
            plt.savefig(buf,format="png")
            buf.seek(0)
            await ctx.send(file=discord.File(buf,filename="hist.png"))

    @commands.command(name="totactivity",pass_context=True)
    @commands.guild_only()
    async def totactivity(self,ctx):
        """Displays a histogram of activity in the server"""
        if not ctx.author.permissions_in(ctx.channel).administrator:
            await ctx.author.send("You must be an administrator to use `totactivity`.")
            return
        times = []
        count = 0
        for c in ctx.guild.text_channels:
            async for i in c.history(limit=500000000):
                #if datetime.datetime.now() - i.created_at < datetime.timedelta(hours=24):
                ltime = i.created_at
                times.append(ltime.hour)
                count = count + 1
                #print(count)
        tar = np.array(times)
        plt.figure()
        plt.xlabel("Hour (UTC)")
        plt.ylabel("Number of messages")
        plt.xlim(0,24)
        numbers=[x for x in range(0,24)]
        labels=map(lambda x: str(x), numbers)
        plt.xticks(numbers, labels)
        plt.hist(tar,bins=24)
        plt.title("Activity over the last {0} messages in {1.guild.name}".format(count,ctx))
        #plt.show()
        with io.BytesIO() as buf:
            plt.savefig(buf,format="png")
            buf.seek(0)
            await ctx.send(file=discord.File(buf,filename="hist.png"))
    
def setup(client):
    client.add_cog(Activity(client))