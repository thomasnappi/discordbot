import discord, asyncio,os
from discord.ext import commands
try:
    import requests
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", 'requests'])
finally:
    import requests
try:
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", 'beautifulsoup4'])
finally:
    from bs4 import BeautifulSoup
try:
    import json
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", 'json'])
finally:
    import json
try:
    from youtube_search import YoutubeSearch
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", 'youtube-search'])
finally:
    from youtube_search import YoutubeSearch
from voicebot import *

# I DO NOT CLAIM CREDIT FOR ALL OF THE BELOW CODE; IT WAS LARGELY ADAPTED FROM ANOTHER MUSIC BOT.
# Source: https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = {}
        self.np = {}

    @commands.Cog.listener()
    async def on_ready(self):
        while(True):
            for i in self.queue.keys():
                voice = self.client.get_guild(i).voice_client
                if voice != None and voice.is_connected() and not voice.is_playing() and not voice.is_paused():
                    if i in self.np.keys() and self.np[i] != None:
                        succ = False
                        while(not succ):
                            try:
                                os.remove(self.np[i].filename)
                                succ = True
                            except:
                                pass
                        self.np[i] = None
                    if len(self.queue[i]) > 0:
                        url = self.queue[i].pop(0)
                        self.np[i] = await YTDLSource.from_url(url,stream=False)
                        voice.play(self.np[i])
            await asyncio.sleep(1)

    @commands.command(name="play")
    async def play(self,ctx,*,title):
        voice = ctx.guild.voice_client
        vc = ctx.message.author.voice.channel
        if vc == None:
            await ctx.send("You must be in a voice channel to use this command.")
            return
        if not ctx.guild.id in self.queue.keys():
            self.queue[ctx.guild.id] = []
        if title.startswith("https://www.youtube.com/watch?v="):
            url = title.split(" ")[0]
            if voice == None:
                voice = await vc.connect()
            self.queue[ctx.guild.id].append(url)
            await ctx.send("Adding {} to the list of songs.".format(url))
        if title.startswith("https://www.youtube.com/playlist?list="):
            #print("PLAYLIST URL " + title.split(" ")[0])
            req = requests.get(title.split(" ")[0])
            bs = BeautifulSoup(req.text,"html.parser")
            num = 0
            for i in bs.find_all("a", class_="pl-video-title-link"):
                num = num + 1
                ind = i["href"].find("&list=")
                url = "https://www.youtube.com" + i["href"][:ind]
                #print("LINK " + url)
                self.queue[ctx.guild.id].append(url)
            if voice == None:
                voice = await vc.connect()
            await ctx.send("Added {} songs to the queue!".format(num))
        else:
            yts = YoutubeSearch(title, max_results=1).to_json()
            topres = json.loads(yts)["videos"][0]["id"]
            if topres == None:
                await ctx.send("No results!")
                return
            url = "https://www.youtube.com/watch?v=" + topres
            #vid = "https://www.youtube.com/watch?v=r5EXKDlf44M"
            if voice == None:
                voice = await vc.connect()
            self.queue[ctx.guild.id].append(url)
            await ctx.send("Adding {} to the list of songs.".format(url))

    @commands.command(name="leave")
    async def leave(self,ctx):
        voice = ctx.guild.voice_client
        if voice == None or not voice.is_connected():
            await ctx.send("Not in a voice channel!")
            return
        else:
            await voice.disconnect()

    @commands.command(name="join")
    async def join(self,ctx):
        voice = ctx.guild.voice_client
        vc = ctx.message.author.voice.channel
        if vc == None:
            await ctx.send("You must be in a voice channel to use this command.")
        elif voice == None or not voice.is_connected():
            await vc.connect()
        else:
            await voice.move_to(vc)

    @commands.command(name="pause")
    async def pause(self,ctx):
        voice = ctx.guild.voice_client
        if voice == None or not voice.is_playing():
            await ctx.send("Nothing playing!")
        else:
            await voice.pause()
    
    @commands.command(name="resume")
    async def resume(self,ctx):
        voice = ctx.guild.voice_client
        if voice == None or not voice.is_paused():
            await ctx.send("Nothing playing!")
        else:
            await voice.resume()

    @commands.command(name="queue")
    async def queue_(self,ctx):
        voice = ctx.guild.voice_client
        if not ctx.guild.id in self.queue.keys() or self.queue[ctx.guild.id] == []:
            await ctx.send("No songs queued!")
        else:
            lis = "Queued songs:\n"
            num = len(self.queue[ctx.guild.id])
            for i in range(num):
                lis = lis + "{0}: {1}\n".format(i+1,self.queue[ctx.guild.id][i])
                #print(i)
                if i > 25:
                    lis = lis + "and {} more songs.".format(num - 25)
                    break;
            await ctx.send(lis)

    @commands.command(name="skip")
    async def skip(self,ctx):
        voice = ctx.guild.voice_client
        if voice == None or not voice.is_connected or not voice.is_playing():
            await ctx.send("Not playing!")
        else:
            msg = await ctx.send("Skipping current song...")
            voice.stop()
            await msg.edit(content="Song skipped!")
    
    @commands.command(name="skipall")
    async def skipall(self,ctx):
        voice = ctx.guild.voice_client
        if voice == None or not voice.is_connected or not voice.is_playing():
            await ctx.send("Not playing!")
        else:
            self.queue[ctx.guild.id] = []
            voice.stop()
            await ctx.send("Current song skipped and queue cleared!")
    
    @commands.command(name="song")
    async def song(self,ctx):
        if ctx.guild.id in self.np.keys() and self.np[ctx.guild.id] != None:
            await ctx.send("*Now playing:* **{}**".format(self.np[ctx.guild.id].title))
        else:
            await ctx.send("Nothing playing!")

def setup(client):
    client.add_cog(Music(client))