import discord,asyncio,io,random,re,requests,aiohttp,html,pickle
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from bs4 import BeautifulSoup
from discord.ext import commands
# from sklearn import svm

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.party = {}
        self.day = {}
        self.hglock = {}
        # with open("modeldata.p",'rb') as file:
        #     self.modeldata = pickle.load(file)

    def owner_only():
        def is_owner(ctx):
            owners = []
            with open("owners.txt") as file:
                for i in file.readlines():
                    owners.append(int(i))
            return ctx.author.id in owners
        return commands.check(is_owner)

    @commands.Cog.listener()
    async def on_message(self,message):
        cont = message.content.lower()
        if "who" in cont and "joe" in cont:
            await message.channel.send("Joe Mama {0.author.mention}".format(message))
        if "amirite" in cont:
            if random.randint(0,1)==1:
                await message.channel.send("No, you're wrong.")
            else:
                await message.channel.send("Yes, you're right.")

    @commands.command()
    async def retcon(self,ctx):
        """Make me change my decision on whether or not you were right."""
        async for message in ctx.history(limit=20):
            cont = message.content
            if cont == "No, you're wrong." and message.author.id == self.client.user.id:
                await message.edit(content="Yes, you're right.")
                break
            elif cont == "Yes, you're right." and message.author.id == self.client.user.id:
                await message.edit(content="No, you're wrong.")
                break

    @commands.command(name="ttimg",pass_context=True)
    async def ttimg(self,ctx,*,caption:str):
        """Adds a caption to the top of the last image sent, including links."""
        if not ctx.author.permissions_in(ctx.channel).attach_files:
            await ctx.author.send("You do not have permissions to send images in {0.name}".format(ctx.channel))
            return
        limg = io.BytesIO()
        fn = ""
        async for message in ctx.history(limit=10):
            cont = message.content.lower()
            if len(message.attachments) > 0:
                await message.attachments[0].save(limg)
                fn = message.attachments[0].filename
                #print("attachment")
                break
            elif ".gif" in cont or ".png" in cont or ".jpg" in cont:
                url = "http://"+message.content.split("//")[1].split(" ")[0]
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            print("failed to get file.")
                        else:
                            limg = io.BytesIO(await resp.read())
                            fn = message.content.split("//")[1].split(" ")[0].split("/")[-1]
                #print("link")
                break
        if fn == "":
            await ctx.send("No image found")
            return
        limg.seek(0)
        im = Image.open(limg) # Load the image with PIL
        ratio = im.width / im.height # Ratio of width/height of the image
        nw = 1024 # We want every image to be 1024 pixels wide
        nh = nw / ratio # Calculate the new height of the image maintaining original image ratio
        rim = im.resize((nw,int(nh))) # Resize image so it's always nw pixels wide and nh pixels high
        del im,ratio # Now that image is resized we don't need original
        fsz = int(nw / 15) # Calculate font size from new width (should be constant every time)
        lettersperrow = (nw - (fsz)) / fsz # Calculate (conservatively) how many letters we can fit in a row
        
        words = caption.split(" ") # Split words along spaces from the input
        rows = [""] # Row of strings to render on the image
        crow = 0 # The current row we are adding words to
        for w in words:
            if len(w) + len(rows[crow]) + 1 > lettersperrow: # If word is too long to fit
                if len(rows[crow]) == 0: # If word is too long for it's own line, it is too long
                    await ctx.send("Word too long; max word length is {} characters.".format(lettersperrow))
                    return
                rows.append(w) # Otherwise add a new row and put it in
                crow = crow + 1 # Move our counter to the next row
            else:
                rows[crow] = rows[crow] + " " + w # There is enough space to add it to the current row
        del crow,words # Words aren't needed anymore & crow is also unnecessary
        imarr = np.array(rim)[:,:,:3] # Make an array from resized image; cut everything other than simple RGB values
        del rim # We don't need original resized image anymore
        topbuf = Image.new('RGB', (nw, int(fsz * (len(rows)+1))), (255, 255, 255)) # Create an image the size of the white space we need
        newimg = Image.fromarray(np.vstack((np.array(topbuf),imarr)), 'RGB') # Create a new image stacking the white space on top
        del imarr,topbuf # Delete the array and buffer image
        draw = ImageDraw.Draw(newimg) # Create a draw object for the new image
        font = ImageFont.truetype("freesansbold.ttf", fsz) # The font we will use to render the font
        for i in range(len(rows)):
            draw.text((fsz/2,int(fsz/2) + (fsz * i)),rows[i],(0,0,0),font=font) # Draw all of our rows of text, with a left/right/top/bottom buffer
        del draw,rows # We no longer need the draw object or the rows of strings

        with io.BytesIO() as output: # Send the image in discord
            newimg.save(output,format="PNG")
            output.seek(0)
            await ctx.send(file=discord.File(output,filename="img.png"))
    
    @commands.command(name="imgsearch",pass_context=True)
    async def imgsearch(self,ctx,num:int,*,term:str):
        """Returns num number of images of name from google. Limit is 10."""
        if not ctx.author.permissions_in(ctx.channel).attach_files:
            await ctx.author.send("You do not have permissions to send images in this channel.")
            return
        if num > 10:
            await ctx.author.send("The limit of images is 10.")
            return
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' }
        query = term.replace(' ','+')
        url = 'https://www.google.com.sg/search?q={}&tbm=isch&tbs=sbd:0'.format(query)
        req = requests.get(url,headers=headers)
        urllist = [n for n in re.findall('"(http[a-zA-Z0-9_./:-]+.(?:jpg|jpeg|png))",', req.text)]
        for i in range(num):
            url = urllist[i]
            fn = url.split("/")[-1]
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        print("failed to get file.")
                        await ctx.send("Failed to get image: {}".format(fn))
                        return
                    else:
                        await ctx.send(file=discord.File(io.BytesIO(await resp.read()),fn))
    
    @commands.command(name="udict",pass_context=True)
    async def udict(self,ctx,*,term:str):
        """Returns the top definition of a term from Urban Dictionary"""
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' }
        query = term.replace(' ','+')
        url = 'https://www.urbandictionary.com/define.php?term={}'.format(query)
        req = requests.get(url,headers=headers)
        div = BeautifulSoup(req.text.replace("<br>","\n"),"html.parser").find("div",class_="def-panel")
        if div is None:
            await ctx.send("Sorry, no definitions found for {} on Urban Dictonary.".format(term))
            return
        title   = div.find("a",class_="word").text
        defn = div.find("div",class_="meaning")
        for br in defn.find_all("br"):
            br.replace_with("\n")
        defn = defn.text.replace("\n\n","\n")
        example = div.find("div",class_="example").text
        string  = "**{0}**\n{1}\n\nExamples:\n*{2}*".format(title,defn,example)
        rellines = string.split("\n")
        while len(rellines) > 0:
            ts = rellines.pop(0)
            for i in range(len(rellines)):
                if len(ts + rellines[0]) > 2000:
                    break
                else:
                    ts = ts + "\n" + rellines.pop(0)
            await ctx.send(ts)

    @commands.command(name="hgjoin",aliases=["joinhg"],pass_context=True)
    @commands.guild_only()
    async def hgjoin(self,ctx):
        """Join the hunger games party!  There can only be one active hunger games party in a server at a time."""
        try:
            self.party[ctx.guild.id] == None
        except:
            self.party[ctx.guild.id] = []
        try:
            self.hglock[ctx.guild.id] == None
        except:
            self.hglock[ctx.guild.id] = False
        try:
            self.day[ctx.guild.id] == None
        except:
            self.day[ctx.guild.id] = 0
        for i in self.party[ctx.guild.id]:
            if i["uid"] == ctx.author.id:
                await ctx.send("You are already in this party!")
                return
        if self.day[ctx.guild.id] == 0:
            name = ctx.author.display_name.replace("_","").replace("\\","").replace("*","")
            self.party[ctx.guild.id].append({"user":name,"statuses":[],"health":200,"uid":ctx.author.id})
            await ctx.send("You have joined the hunger games party; there are now {} people".format(len(self.party[ctx.guild.id])))
        else:
            await ctx.send("Unfortunately, this round has already started - please wait for it to finish")
    
    @commands.command(name="joinallserv",aliases=["forcealljoin","fillparty"],pass_context=True)
    @owner_only()
    @commands.guild_only()
    async def joinallserv(self,ctx):
        """Add every non-bot member of a server to the party!"""
        try:
            self.party[ctx.guild.id] == None
        except:
            self.party[ctx.guild.id] = []
        try:
            self.hglock[ctx.guild.id] == None
        except:
            self.hglock[ctx.guild.id] = False
        try:
            self.day[ctx.guild.id] == None
        except:
            self.day[ctx.guild.id] = 0
        for i in ctx.guild.members:
            if not i.bot:
                name = i.display_name.replace("_","").replace("\\","").replace("*","")
                self.party[ctx.guild.id].append({"user":name,"statuses":[],"health":200,"uid":i.id})
        await ctx.send("You have added all {} users in the server to the party".format(len(self.party[ctx.guild.id])))

    @commands.command(name="hgcheat",pass_context=True)
    @commands.guild_only()
    @owner_only()
    async def hgcheat(self,ctx,member:discord.Member,hp:int):
        """Change the HP of a member in the party by $hp."""
        try:
            self.party[ctx.guild.id] == None
        except:
            self.party[ctx.guild.id] = []
        try:
            self.hglock[ctx.guild.id] == None
        except:
            self.hglock[ctx.guild.id] = False
        try:
            self.day[ctx.guild.id] == None
        except:
            self.day[ctx.guild.id] = 0
        for i in self.party[ctx.guild.id]:
            if i["uid"] == member.id:
                i["health"] = i["health"] + hp
                await ctx.send("{0.display_name} had their health changed by {1}".format(member,hp))
                return

    @commands.command(name="hgday",aliases=["hgadvance","hgrun"],pass_context=True)
    @commands.guild_only()
    async def hgday(self,ctx):
        """Run a day of hunger games in this channel!"""
        try:
            self.party[ctx.guild.id] == None
        except:
            self.party[ctx.guild.id] = []
        try:
            self.hglock[ctx.guild.id] == None
        except:
            self.hglock[ctx.guild.id] = False
        try:
            self.day[ctx.guild.id] == None
        except:
            self.day[ctx.guild.id] = 0
        if self.hglock[ctx.guild.id]:
            await ctx.send("Sorry, this day is being played elsewhere.")
            return
        if len(self.party[ctx.guild.id]) == 0:
            await ctx.send("There is nobody in the party!")
            return
        self.hglock[ctx.guild.id] = True
        self.day[ctx.guild.id] = self.day[ctx.guild.id] + 1
        totsend = ""
        trapevents = [{"name":"Bear Trap",         "drops":"Bear Trap", "hmodmin":15, "hmodmax":50,  "statusmod":"a broken leg", "smod%":0.3, "party":False, "detect":0.2, "max":6},
                      {"name":"Shotgun Trap",      "drops":"Gunpowder", "hmodmin":30, "hmodmax":80,  "statusmod":"tinnitus",     "smod%":0.8, "party":False, "detect":0.3, "max":2},
                      {"name":"Spike Pit",         "drops":"Spear",     "hmodmin":20, "hmodmax":70,  "statusmod":"been impaled", "smod%":0.8, "party":True,  "detect":0.3, "max":2},
                      {"name":"Landmine",          "drops":"None",      "hmodmin":80, "hmodmax":200, "statusmod":"a broken leg", "smod%":0.7, "party":False, "detect":0.1, "max":2},
                      {"name":"Tree Snare",        "drops":"Rope",      "hmodmin":10, "hmodmax":40,  "statusmod":"a broken leg", "smod%":0.5, "party":False, "detect":0.4, "max":4},
                      {"name":"Acid Trap",         "drops":"None",      "hmodmin":30, "hmodmax":50,  "statusmod":"been burned",  "smod%":0.8, "party":True,  "detect":0.3, "max":1}]

        choiceevents = [{"name":"IED Airdrop",       "hmodmin":-60,  "hmodmax":-120, "statusmod":"tinnitus",     "smod%":0.8, "party":True,  "detect":0.2, "deceit":"First Aid Airdrop"},
                        {"name":"IED Airdrop",       "hmodmin":-60,  "hmodmax":-120, "statusmod":"tinnitus",     "smod%":0.8, "party":True,  "detect":0.2, "deceit":"Empty Airdrop"},
                        {"name":"First Aid Airdrop", "hmodmin":20,   "hmodmax":60,   "statusmod":"CLEAR",        "smod%":0.5, "party":True,  "detect":0.2, "deceit":"Empty Airdrop"},
                        {"name":"First Aid Airdrop", "hmodmin":20,   "hmodmax":60,   "statusmod":"CLEAR",        "smod%":0.5, "party":True,  "detect":0.5, "deceit":"IED Airdrop"},
                        {"name":"First Aid Airdrop", "hmodmin":20,   "hmodmax":60,   "statusmod":"CLEAR",        "smod%":0.5, "party":True,  "detect":0.5, "deceit":"IED Airdrop"},
                        {"name":"Empty Airdrop",     "hmodmin":0,    "hmodmax":5,    "statusmod":"None",           "smod%":0.0, "party":False, "detect":0.6, "deceit":"First Aid Airdrop"},
                        {"name":"Empty Airdrop",     "hmodmin":0,    "hmodmax":5,    "statusmod":"None",           "smod%":0.0, "party":False, "detect":0.6, "deceit":"IED Airdrop"},
                        {"name":"Nailbomb",          "hmodmin":-30,  "hmodmax":-40, " statusmod":"been blinded", "smod%":0.4, "party":False, "detect":0.3, "deceit":"Can of Beans"},
                        {"name":"Nailbomb",          "hmodmin":-30,  "hmodmax":-40, " statusmod":"been blinded", "smod%":0.4, "party":False, "detect":0.3, "deceit":"Empty Can"},
                        {"name":"Empty Can",         "hmodmin":0,    "hmodmax":0,    "statusmod":"None",           "smod%":0.0, "party":False, "detect":0.5, "deceit":"Can of Beans"},
                        {"name":"Expired Beans",     "hmodmin":-20,  "hmodmax":20,   "statusmod":"gotten sick",  "smod%":0.5, "party":False, "detect":0.2, "deceit":"Can of Beans"},
                        {"name":"Expired Beans",     "hmodmin":-20,  "hmodmax":20,   "statusmod":"gotten sick",  "smod%":0.5, "party":False, "detect":0.2, "deceit":"Nailbomb"},
                        {"name":"Can of Beans",      "hmodmin":10,   "hmodmax":40,   "statusmod":"None",           "smod%":0.0, "party":False, "detect":0.5, "deceit":"Empty Can"},
                        {"name":"Can of Beans",      "hmodmin":10,   "hmodmax":40,   "statusmod":"None",           "smod%":0.0, "party":False, "detect":0.5, "deceit":"Nailbomb"},
                        {"name":"Poisonous Plant",   "hmodmin":-10,  "hmodmax":-60,  "statusmod":"gotten sick",  "smod%":1.0, "party":False,  "detect":0.5, "deceit":"Healing Herb"},
                        {"name":"Healing Herb",      "hmodmin":10,   "hmodmax":30,   "statusmod":"None",           "smod%":0.0, "party":False, "detect":0.5, "deceit":"Poisonous Plant"}]

        niceevents = [{"name":"'normal' day",      "drops":"None",          "hmodmin":-30,  "hmodmax":10,  "statusmod":"None",  "smod%":0.0},
                      {"name":"'normal' day",      "drops":"None",          "hmodmin":-30,  "hmodmax":10,  "statusmod":"None",  "smod%":0.0},
                      {"name":"'normal' day",      "drops":"None",          "hmodmin":-30,  "hmodmax":10,  "statusmod":"None",  "smod%":0.0},
                      {"name":"'normal' day",      "drops":"None",          "hmodmin":-30,  "hmodmax":10,  "statusmod":"None",  "smod%":0.0},
                      {"name":"uneventful day",    "drops":"None",          "hmodmin":-10,  "hmodmax":10,  "statusmod":"None",  "smod%":0.0},
                      {"name":"uneventful day",    "drops":"None",          "hmodmin":-10,  "hmodmax":10,  "statusmod":"None",  "smod%":0.0},
                      {"name":"uneventful day",    "drops":"None",          "hmodmin":-10,  "hmodmax":10,  "statusmod":"None",  "smod%":0.0},
                      {"name":"safe day",          "drops":"None",          "hmodmin":20,   "hmodmax":40,  "statusmod":"CLEAR", "smod%":0.3}]
        #await ctx.send("Day {}".format(self.day[ctx.guild.id]))
        totsend = totsend + "Day {}".format(self.day[ctx.guild.id]) + "\n"
        selection = random.randint(0,4)
        RESPONDER = None
        if selection < 3:
            cev = choiceevents[random.randint(0,len(choiceevents)-1)]
            name = ""
            deceived = False
            if (random.randint(0,100) / 100.0) - (self.day[ctx.guild.id] * 0.01) < cev["detect"]:
                name = cev["name"]
            else:
                name = cev["deceit"]
                deceived = True
            #await ctx.send("You see what you think is a " + name)
            totsend = totsend + "You see what you think is a " + name + "\n"
            choice = ""
            c = None
            while choice != "y" and choice != "n":
                #await ctx.send("approach?(y/n)")
                if c != None:
                    RESPONDER = None
                    for i in self.party[ctx.guild.id]:
                        #print("Responder:{}".format(c.author.id))
                        #print("Compared to:{}".format(i["uid"]))
                        if c.author.id == i["uid"]:
                            print("User found!")
                            RESPONDER = i
                            break
                    if c.channel.id == ctx.channel.id and not RESPONDER is None:
                        totsend = totsend + "approach?(y/n)"
                        rellines = totsend.split("\n")
                        while len(rellines) > 0:
                            ts = rellines.pop(0)
                            for i in range(len(rellines)):
                                if len(ts + rellines[0]) > 2000:
                                    break
                                else:
                                    ts = ts + "\n" + rellines.pop(0)
                            await ctx.send(ts)
                        #await ctx.send(totsend)
                        usr = None
                else:
                    totsend = totsend + "approach?(y/n)"
                    rellines = totsend.split("\n")
                    while len(rellines) > 0:
                        ts = rellines.pop(0)
                        for i in range(len(rellines)):
                            if len(ts + rellines[0]) > 2000:
                                break
                            else:
                                ts = ts + "\n" + rellines.pop(0)
                        await ctx.send(ts)
                    #await ctx.send(totsend)
                totsend = ""
                c = await self.client.wait_for("message")
                choice = c.content.lower()
                for i in self.party[ctx.guild.id]:
                    #print("Responder:{}".format(c.author.id))
                    #print("Compared to:{}".format(i["uid"]))
                    if c.author.id == i["uid"]:
                        #print("User found!")
                        RESPONDER = i
                        break
                if RESPONDER is None:
                    print("USR is none")
                    choice = ""
            if choice == "n":
                #await ctx.send("You quickly leave.\n")
                totsend = totsend + "You quickly leave.\n"
                selection = random.randint(3,4)
            else:
                #print(type(RESPONDER))
                #print(cev["name"])
                if deceived:
                    #await ctx.send("You were wrong! It was actually a " + cev["name"]+"!")
                    totsend = totsend + "You were wrong! It was actually a " + cev["name"]+"!\n"
                if (not cev["party"]) and (random.randint(0,10) / 10.0) <= cev["smod%"]:
                    if RESPONDER is None: #should not happen
                        print("User was none...")
                        RESPONDER = self.party[ctx.guild.id][random.randint(0,len(self.party[ctx.guild.id])-1)]
                    if not cev["statusmod"] is None and cev["statusmod"] == "CLEAR":
                        #await ctx.send("{0} had all status effects cleared!".format(usr["user"]))
                        totsend = totsend + "{0} had all status effects cleared!".format(RESPONDER["user"]) + "\n"
                        RESPONDER["statuses"] = []
                    elif cev["statusmod"] != "None":
                        RESPONDER["statuses"].append(cev["statusmod"])
                        #await ctx.send("{0} has {1}!".format(usr["user"],cev["statusmod"]))
                        totsend = totsend + "{0} has {1}!".format(RESPONDER["user"],cev["statusmod"]) + "\n"
                elif cev["party"] and (random.randint(0,10) / 10.0) <= cev["smod%"]:
                    for i in self.party[ctx.guild.id]:
                        if cev["statusmod"] != "None":
                            i["statuses"].append(cev["statusmod"])
                        if cev["statusmod"] == "CLEAR":
                            i["statuses"] = []
                    #await ctx.send("Everyone in the party now has {}!".format(cev["statusmod"]))
                    if cev["statusmod"] != "CLEAR" or cev["statusmod"] != "None":
                        totsend = totsend + "Everyone in the party now has {}!".format(cev["statusmod"]) + "\n"
                if cev["party"]:
                    for i in self.party[ctx.guild.id]:
                        if cev["hmodmin"] < cev["hmodmax"]:
                            hp = random.randint(cev["hmodmin"],cev["hmodmax"])
                        else:
                            hp = random.randint(cev["hmodmax"],cev["hmodmin"])
                        i["health"] = i["health"] + hp
                        #await ctx.send("{0} took {1} damage!".format(i["user"],-1 * dm))
                        if hp < 0:
                            totsend = totsend + "{0} took {1} damage!".format(i["user"],-1 * hp) + "\n"
                        if hp > 0:
                            totsend = totsend + "{0} was healed by {1}!".format(i["user"],hp) + "\n"
                hp = 0
                if cev["hmodmin"] < cev["hmodmax"]:
                    hp = random.randint(cev["hmodmin"],cev["hmodmax"])
                else:
                    hp = random.randint(cev["hmodmax"],cev["hmodmin"])
                if hp > 0 and not cev["party"]:
                    #usr = self.party[ctx.guild.id][random.randint(0,len(self.party)-1)]
                    if RESPONDER is None: #should not happen
                        print("User was none...")
                        RESPONDER = self.party[ctx.guild.id][random.randint(0,len(self.party[ctx.guild.id])-1)]
                    hp = random.randint(cev["hmodmin"],cev["hmodmax"])
                    RESPONDER["health"] = RESPONDER["health"] + hp
                    totsend = totsend + "{0} was healed by {1}!".format(RESPONDER["user"],hp) + "\n"
                if hp < 0 and not cev["party"]:
                    #usr = self.party[ctx.guild.id][random.randint(0,len(self.party)-1)]
                    if RESPONDER is None: #should not happen
                        print("User was none...")
                        RESPONDER = self.party[ctx.guild.id][random.randint(0,len(self.party[ctx.guild.id])-1)]
                    RESPONDER["health"] = RESPONDER["health"] + hp
                    #await ctx.send("{0} took {1} damage!".format(i["user"],-1 * dm))
                    totsend = totsend + "{0} took {1} damage!".format(RESPONDER["user"],-1 * hp) + "\n"
                if hp == 0 and cev["smod%"] == 0.0 and not cev["party"]:
                    totsend = totsend + "Nothing happens...\n"

        if selection == 3:
            #print(len(trapevents))
            trev = trapevents[random.randint(0,len(trapevents)-1)]
            dodged = False
            #print("You found a {0}!".format(trev["name"]))
            if (random.randint(0,100) / 100.0) - (self.day[ctx.guild.id] * 0.01) < trev["detect"]:
                #await ctx.send("You found a {0}, but not the hard way".format(trev["name"]))
                totsend = totsend + "You found a {0}, but not the hard way".format(trev["name"]) + "\n"
                dodged = True
            if (not trev["party"]) and not dodged:
                for i in range(random.randint(1,trev["max"])):
                    usr = self.party[ctx.guild.id][random.randint(0,len(self.party[ctx.guild.id])-1)]
                    #await ctx.send("{0} found a {1}!".format(usr["user"],trev["name"]))
                    #print("{0} found a {1}".format(usr["user"],trev["name"]))
                    totsend = totsend + "{0} found a {1}!".format(usr["user"],trev["name"]) +"\n"
                    if (random.randint(0,10) / 10.0) <= trev["smod%"]:
                        usr["statuses"].append(trev["statusmod"])
                        #await ctx.send("{0} got {1}!".format(usr["user"],trev["statusmod"]))
                        totsend = totsend + "{0} got {1}!".format(usr["user"],trev["statusmod"]) + "\n"
                    ch = random.randint(trev["hmodmin"],trev["hmodmax"])
                    usr["health"]=usr["health"]-ch
                    #await ctx.send(usr["user"] + " took {} damage!".format(ch))
                    totsend = totsend + usr["user"] + " took {} damage!".format(ch) + "\n"
            elif trev["party"] and (random.randint(0,10) / 10.0) <= trev["smod%"] and not dodged:
                totsend = totsend + "Everyone in the party found a {}!".format(trev["name"]) + "\n"
                for i in self.party[ctx.guild.id]:
                    if trev["statusmod"] == "CLEAR":
                        #await ctx.send("{0} had all status effects cleared!".format(usr["user"]))
                        totsend = totsend + "{0} had all status effects cleared!".format(usr["user"]) + "\n"
                        i["statuses"] = []
                    elif i["statusmod"] != "None":
                        i["statuses"].append(trev["statusmod"])
                        #await ctx.send("{0} has {1}!".format(usr["user"],cev["statusmod"]))
                    #i["statuses"].append(trev["statusmod"])
                    #await ctx.send("Everyone in the party now has {}!".format(trev["statusmod"]))
                if i["statusmod"] != "None":
                    totsend = totsend + "Everyone in the party now has {}!".format(trev["statusmod"]) + "\n"
            if not dodged and trev["party"]:
                for i in self.party[ctx.guild.id]:
                    #print("hmmin {0} hmmax {1}".format(trev["hmodmin"],trev["hmodmax"]))
                    ch = random.randint(trev["hmodmin"],trev["hmodmax"])
                    i["health"]=i["health"]-ch
                    #await ctx.send(i["user"] + " took {} damage!".format(ch))
                    totsend = totsend + i["user"] + " took {} damage!".format(ch) + "\n"

        if selection == 4 and len(self.party[ctx.guild.id]) > 1:
            #Betrayal!
            #print("betrayal")
            numattackers = random.randint(1,len(self.party[ctx.guild.id])-1)
            #print("Attackers {}".format(numattackers))
            numdefenders  = random.randint(1,len(self.party[ctx.guild.id])-numattackers)
            #print("Defenders {}".format(numdefenders))
            if len(self.party[ctx.guild.id])-(numattackers+numdefenders)-1 <= 0:
                numaltruism = 0
            else:
                numaltruism  = random.randint(0,len(self.party[ctx.guild.id])-(numattackers+numdefenders)-1)
            #print("Altruism {}".format(numaltruism))
            rng = range(len(self.party[ctx.guild.id]))
            #print("Range {}".format(rng))
            totalppl = numattackers+numdefenders+numaltruism
            #print("Involved {}".format(totalppl))
            involved = random.sample(rng, totalppl)
            attackerinds = involved[:numattackers]
            defenderinds = involved[numattackers:numdefenders+numattackers]
            altruisminds = []
            if numaltruism != 0:
                altruisminds = involved[numattackers+numdefenders:]
            totsend = totsend + "**Betrayal!  Suddenly**"
            for i in attackerinds:
                totsend = totsend + ", " + self.party[ctx.guild.id][i]["user"]
            totsend = totsend + " **attack** "
            for i in defenderinds:
                totsend = totsend  + self.party[ctx.guild.id][i]["user"] + ", "
            totsend = totsend[:-2] + "**!**\n"
            if numaltruism > 0:
                for i in altruisminds:
                    totsend = totsend + self.party[ctx.guild.id][i]["user"] + ", "
                totsend = totsend[:-2] + " try to break it up.\n"
            if numaltruism > numattackers:
                totsend = totsend + "Because enough people broke up the fight, nobody got hurt.\n"
            else:
                plannedattacks = []
                for i in range(len(attackerinds)):
                    target = random.randint(0,numdefenders-1)
                    plannedattacks.append([attackerinds[i],defenderinds[target]])
                    print(plannedattacks[i])
                if len(plannedattacks) < len(altruisminds):
                    print("wtf bro how lmao")
                for i in range(len(altruisminds)):
                    totsend = totsend + self.party[ctx.guild.id][altruisminds[i]]["user"] + " stopped " + self.party[ctx.guild.id][plannedattacks[i][0]]["user"] + " from attacking " + self.party[ctx.guild.id][plannedattacks[i][1]]["user"] + "!\n"
                    plannedattacks.pop(i)
                for i in range(len(plannedattacks)):
                    dm = random.randint(1,self.party[ctx.guild.id][plannedattacks[i][0]]["health"])
                    totsend = totsend + self.party[ctx.guild.id][plannedattacks[i][0]]["user"] + " attacked " + self.party[ctx.guild.id][plannedattacks[i][1]]["user"] + " for {} damage!\n".format(dm)
                    self.party[ctx.guild.id][plannedattacks[i][1]]["health"] = self.party[ctx.guild.id][plannedattacks[i][1]]["health"] - dm
            rellines = totsend.split("\n")
            while len(rellines) > 0:
                ts = rellines.pop(0)
                for i in range(len(rellines)):
                    if len(ts + rellines[0]) > 2000:
                        break
                    else:
                        ts = ts + "\n" + rellines.pop(0)
                await ctx.send(ts)
            #await ctx.send(totsend)
            totsend = ""

        selection = 5
        if selection == 5:
            nev = niceevents[random.randint(0,len(niceevents)-1)]
            #await ctx.send("You had a " + nev["name"])
            totsend = totsend + "You had a " + nev["name"] + "\n"
            for i in self.party[ctx.guild.id]:
                #print("hmmin {0} hmmax {1}".format(trev["hmodmin"],trev["hmodmax"]))
                ch = random.randint(nev["hmodmin"],nev["hmodmax"])
                i["health"]=i["health"]+ch
                if ch < 0:
                    #await ctx.send(i["user"] + " took {} damage!".format(-1 *ch))
                    totsend = totsend + i["user"] + " took {} damage!".format(-1 *ch) + "\n"
                elif ch > 0:
                    #await ctx.send(i["user"] + " was healed by  {}!".format(ch))
                    totsend = totsend + i["user"] + " was healed by  {}!".format(ch) + "\n"

        ind = 0
        opl = len(self.party[ctx.guild.id])
        #await ctx.send("Party status:")
        totsend = totsend + "```Party status:\n"
        for i in range(len(self.party[ctx.guild.id])):
            #print(i)
            usr = self.party[ctx.guild.id][ind]
            if usr["health"] > 200:
                usr["health"] = 200
            hasstr = ""
            for j in usr["statuses"]:
                hasstr = hasstr + ", has " + j
            
            if usr["health"] <= 0:
                #await ctx.send(usr["user"] + " has died! ({} health)".format(usr["health"]))
                totsend = totsend + usr["user"] + " has died! ({} health)".format(usr["health"]) + "\n"
                self.party[ctx.guild.id].pop(ind)
                ind = ind - 1
            else:
                #await ctx.send("{0}: {1} health{2}".format(usr["user"],usr["health"],hasstr))
                totsend = totsend + "{0}: {1} health{2}".format(usr["user"],usr["health"],hasstr) + "\n"
            ind = ind + 1
        totsend = totsend + "```"
        if len(self.party[ctx.guild.id]) != opl:
            #await ctx.send("Your party now has {} people.".format(len(self.party[ctx.guild.id])))
            totsend = totsend + "Your party now has {} people.".format(len(self.party[ctx.guild.id])) + "\n"
        if len(self.party[ctx.guild.id]) == 0:
            #await ctx.send("Everyone is dead! New people can now join, and the game can be restarted.")
            totsend = totsend + "Everyone is dead! New people can now join, and the game can be restarted.\n"
            self.day[ctx.guild.id] = 0
        rellines = totsend.split("\n")
        while len(rellines) > 0:
            ts = rellines.pop(0)
            for i in range(len(rellines)):
                if len(ts + rellines[0]) > 2000:
                    break
                else:
                    ts = ts + "\n" + rellines.pop(0)
            await ctx.send(ts)
        #await ctx.send(totsend)
        self.hglock[ctx.guild.id] = False

    @commands.command(name="wikipedia",aliases=["wsearch","wikisearch"],pass_context=True)
    async def wikipedia(self,ctx,*,term:str):
        """Returns the first paragraph of information on a subject from Wikipedia"""
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' }
        query = term.replace(' ','_')
        url = 'https://en.wikipedia.org/wiki/{}'.format(query)
        req = requests.get(url,headers=headers)
        div = BeautifulSoup(req.text.replace("<br>","\n"),"html.parser")
        title   = div.find("h1",class_="firstHeading").text
        firstpar = div.find("div",class_="mw-parser-output").find("p",class_="").text
        string  = "**{0}** (*{2}*)\n{1}".format(title,firstpar,url)
        if "may refer to:" in firstpar:
            td = div.find("div",class_="mw-parser-output")
            td.find("div",class_="tocright").decompose()
            for sth in td.find_all("ul"):
                string = "{0}{1}\n".format(string,sth.text)

        rellines = string.split("\n")
        while len(rellines) > 0:
            ts = rellines.pop(0)
            for i in range(len(rellines)):
                if len(ts + rellines[0]) > 2000:
                    break
                else:
                    ts = ts + "\n" + rellines.pop(0)
            await ctx.send(ts)
        #await ctx.send(string)
    
    @commands.command(name="printplace",aliases=["printpl","pp"],pass_context=True)
    async def printplace(self,ctx):
        """ Prints the current place image. """
        await ctx.send("The current state of place.",file=discord.File("place.jpg"))

    @commands.command(name="editplace",aliases=["ep"],pass_context=True)
    async def ep(self,ctx,x:int,y:int,color):
        """ Changes pixel at x,y to a color of format (R,G,B) (or one of these colors: red, green, blue, yellow, purple, black, white). """
        colordict = {"red":(255,0,0),"green":(0,255,0),"blue":(0,0,255),"yellow":(255,255,0),"purple":(255,0,255),"black":(0,0,0),"white":(255,255,255)}
        if color in colordict.keys():
            color = colordict[color]
        else:
            try:
                c = color[1:].split(",")
                color = (int(c[0]),int(c[1]),int(c[2][:-1]))
            except:
                await ctx.send("Malformed.")
        im = np.array(Image.open("place.jpg"))
        im[y][x] = color
        print(im[y][x])
        im2 = Image.fromarray(im)
        im2.save("place.jpg")
        await ctx.send(file=discord.File("place.jpg"))

    @commands.command(name="xkcd",pass_context=True)
    async def xkcd(self,ctx,num : int = -1):
        """ Get an xkcd comic by number, or just grab the most recent one. """
        if (num == -1):
            num = ""
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' }
        url = 'https://www.xkcd.com/{}'.format(num)
        req = requests.get(url,headers=headers)
        pls = "Image URL (for hotlinking/embedding): "
        tp = "title=\""
        cs = req.text.index("<div id=\"comic\">")
        ts = req.text.index(tp,cs) + len(tp)
        te = req.text[ts:].index("\"")
        title = html.unescape(req.text[ts:ts+te])
        start = req.text.index(pls) + len(pls)
        end = req.text[start:].index("\n",1)
        nt = req.text[start:end+start]
        fn = nt.split("/")[-1]
        async with aiohttp.ClientSession() as session:
            async with session.get(nt) as resp:
                if resp.status != 200:
                    print("failed to get file.")
                    await ctx.send("Failed to get image: {}".format(fn))
                    return
                else:
                    await ctx.send(title,file=discord.File(io.BytesIO(await resp.read()),fn))

    # @commands.command(name="imitate",pass_context=True)
    # async def imitate(self,ctx,author : int, *, prompt):
    #     combined = []
    #     for channel in server.text_channels:
    #         if channel.name != "bot-testing":
    #             print("On Channel "+channel.name)
    #             cdict = []
    #             async for msg in channel.history(limit=50000000000,oldest_first=True):
    #                 if len(msg.content) == 0 or msg.content[0] != "!":
    #                     cdict += [{"user":msg.author.id,"msg":msg.content}]
    #                     i = i + 1
    #             combined = combined + cdict
    #     await ctx.send("Compiled training dataset; " + i + " messages.")
    #     byauthor = {}
    #     for i in range(len(combined)):
    #         msg = combined[i]
    #         if i == 0:
    #             pass
    #         else:
    #             if not msg["user"] in byauthor.keys():
    #                 byauthor[msg['user']] = {"prev":[],"r1":[],"r2":[],"r3":[]}
                
    #             x = combined[i-1]['msg'].lower().split(' ')
    #             nx = []
    #             ny = []
    #             for g in range(len(x)):
    #                 w = regex.sub('',x[g])
    #                 if not w in words:
    #                     words.append(regex.sub('',x[g]))
    #                 nx.append(words.index(w))
    #             y = msg['msg'].lower().split(' ')
    #             for g in range(len(y)):
    #                 w = regex.sub('',y[g])
    #                 if not w in words:
    #                     words.append(regex.sub('',y[g]))
    #                 ny.append(words.index(w))
    #             while len(nx) < 5:
    #                 nx = nx + [-1]
    #             nx = nx[:5]
    #             while len(ny) < 3:
    #                 ny = ny + [-1]
    #             ny = ny[:3]
    #             byauthor[msg['user']]['prev'].append(nx)
    #             byauthor[msg['user']]['r1'].append(ny[0])
    #             byauthor[msg['user']]['r2'].append(ny[1])
    #             byauthor[msg['user']]['r3'].append(ny[2])

    #     await ctx.send("Processed data")

    #     author = ctx.author.id
    #     proto_x = np.array(byauthor[author]['prev'])
    #     y1      = np.array(byauthor[author]['r1'])
    #     y2      = np.array(byauthor[author]['r2'])
    #     y3      = np.array(byauthor[author]['r3'])
    #     # print(proto_x.shape)
    #     # print(y.shape)

    #     model1 = svm.SVR()
    #     model2 = svm.SVR()
    #     model3 = svm.SVR()

    #     model1.fit(proto_x,y1)
    #     await ctx.send("model 1 trained")
    #     model2.fit(proto_x,y2)
    #     await ctx.send("model 2 trained")
    #     model3.fit(proto_x,y3)
    #     await ctx.send("model 3 trained")

    #     pred = input("Prediction > ")
    #     pred = pred.lower().split(' ')
    #     num = len(pred)
    #     predx = []

    #     for g in range(len(pred)):
    #         w = regex.sub('',pred[g])
    #         if w in words:
    #             predx.append(words.index(w))
    #         else:
    #             predx.append(-1)

    #     while len(predx) < 5:
    #         predx.append(-1)
    #     predx = np.array(predx[:5])

    #     pred1 = model1.predict([predx])
    #     pred2 = model2.predict([predx])
    #     pred3 = model3.predict([predx])

    #     await ctx.send(words[int(pred1)] + " " + words[int(pred2)] + " " + words[int(pred3)])

def setup(client):
    client.add_cog(Fun(client))
