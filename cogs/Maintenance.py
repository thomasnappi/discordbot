import discord,asyncio,sys
from discord.ext import commands

class Maintenance(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    def owner_only():
        def is_owner(ctx):
            owners = []
            with open("owners.txt") as file:
                for i in file.readlines():
                    owners.append(int(i))
            return ctx.author.id in owners
        return commands.check(is_owner)
    
    @commands.command(name="stop",aliases=["quit"],pass_context=True)
    @owner_only()
    async def stop(self,ctx):
        sys.exit(0)

    @commands.command(name="listmodules",aliases=["listcogs","lcogs"],pass_context=True)
    @owner_only()
    async def listmodules(self,ctx):
        exts = "Loaded extensions:"
        for i in self.client.extensions.keys():
            exts = exts + " " + i
        await ctx.send(exts)

    @commands.command(name="reloadmodule",aliases=["reload","rlcog"],pass_context=True)
    @owner_only()
    async def reloadmodule(self,ctx,module:str):
        if not "cogs.{}".format(module) in self.client.extensions.keys():
            await ctx.send("Unrecognized module.")
            return
        elif module == "Maintenance":
            await ctx.send("You cannot unload Maintenace using Maintenance!")
            return
        self.client.unload_extension("cogs.{}".format(module))
        await ctx.send("Successfully unloaded cog.")
        try:
            self.client.load_extension("cogs.{}".format(module))
            await ctx.send("Successfully loaded cog.")
        except:
            await ctx.send("Unable to reload cog.")


    @commands.command(name="unloadmodule",aliases=["unload","unloadcog"],pass_context=True)
    @owner_only()
    async def unloadmodule(self,ctx,module:str):
        """Unloads the specified cog"""
        if not "cogs.{}".format(module) in self.client.extensions.keys():
            await ctx.send("Unrecognized module.")
            return
        elif module == "Maintenance":
            await ctx.send("You cannot unload Maintenace using Maintenance!")
            return
        else:
            self.client.unload_extension("cogs.{}".format(module))
            await ctx.send("Successfully unloaded cog.")

    @commands.command(name="loadmodule",aliases=["load","loadcog"],pass_context=True)
    @owner_only()
    async def loadmodule(self,ctx,module:str):
        """Loads the specified cog"""
        if "cogs.{}".format(module) in self.client.extensions.keys():
            await ctx.send("Module already loaded!")
            return
        else:
            self.client.load_extension("cogs.{}".format(module))
            await ctx.send("Successfully loaded cog.")

    @commands.command(name="addrolein",aliases=["ari"],pass_context=True)
    @owner_only()
    async def addrolein(self,ctx,gid:int,user:discord.User,*,rname:str):
        """Add a role to a user in a server."""
        sv = self.client.get_guild(gid)
        if sv == None:
            await ctx.send("Server not found.")
            return
        role = discord.utils.get(sv.roles,name=rname)
        if role == None:
            await ctx.send("Role not found")
            return
        member = discord.utils.get(sv.members,id=user.id)
        if member == None:
            await ctx.send("User not found in server.")
            return
        try:
            await member.add_roles(role)
            await ctx.send("Role {0.name} added to user {1.mention} successfully.".format(role,user))
            return
        except:
            await ctx.send("Unable to add role to user; likely permission issue.")
    
    @commands.command(name="remrolein",aliases=["rri"],pass_context=True)
    @owner_only()
    async def remrolein(self,ctx,gid:int,user:discord.User,*,rname:str):
        """Remove a role from a user in a server."""
        sv = self.client.get_guild(gid)
        if sv == None:
            await ctx.send("Server not found.")
            return
        role = discord.utils.get(sv.roles,name=rname)
        if role == None:
            await ctx.send("Role not found")
            return
        member = discord.utils.get(sv.members,id=user.id)
        if member == None:
            await ctx.send("User not found in server.")
            return
        try:
            await member.remove_roles(role)
            await ctx.send("Role {0.name} removed from user {1.mention} successfully.".format(role,user))
            return
        except:
            await ctx.send("Unable to remove role from user; likely permission issue.")
    
    @commands.command(name="checkrolein",aliases=["cri"],pass_context=True)
    @owner_only()
    async def checkrolein(self,ctx,gid:int,user:discord.User,*,rname:str):
        """Check if a user in a server has a role."""
        sv = self.client.get_guild(gid)
        if sv == None:
            await ctx.send("Server not found.")
            return
        role = discord.utils.get(sv.roles,name=rname)
        if role == None:
            await ctx.send("Role not found")
            return
        member = discord.utils.get(sv.members,id=user.id)
        if member == None:
            await ctx.send("User not found in server.")
            return
        if role in member.roles:
            await ctx.send("User {0} has the role {1}".format(member.name+"#"+member.discriminator,role.name))
            return
        else:
            await ctx.send("User {0} does not have the role {1}".format(member.name+"#"+member.discriminator,role.name))
            return
    
    @commands.command(name="rpurge",aliases=["remotepurge","rp"],pass_context=True)
    @owner_only()
    async def rpurge(self,ctx,num:int,gid:int,channel:str,isname:bool=True):
        """Purge messages from a channel in a server; has option to non-bulk delete,
        in order to avoid the manage_messages permission for self deletes."""
        sv = self.client.get_guild(gid)
        if sv == None:
            await ctx.send("Server not found.")
            return
        if isname:
            channel = discord.utils.get(sv.text_channels,name=channel)
        else:
            try:
                channel = int(channel)
            except:
                await ctx.send("Error: stated ID is not an integer")
                return
            channel = discord.utils.get(sv.text_channels,id=channel)
        if channel == None:
            await ctx.send("Channel not found.")
            return
        if not sv.me.permissions_in(channel).manage_messages:
            await ctx.send("Unsuitable permissions.")
            return
        deleted = await channel.purge(limit=num+1)
        await ctx.send("Deleted {} messages.".format(len(deleted)))

    @commands.command(name="rach",aliases=["readallch","readallchannels","rallc"],pass_context=True)
    @owner_only()
    async def rach(self,ctx,gid:int):
        """Read all channels and channel categories in a server."""
        server = self.client.get_guild(gid)
        if server == None:
            await ctx.send("Server not found.")
            return
        clist = "Channels: "
        for cat in server.categories:
            clist = clist + "\n"+cat.name.upper()+""
            for ch in cat.text_channels:
                clist = clist + "\n#" + ch.name
            for ch in cat.voice_channels:
                clist = clist + "\n:speaker:" + ch.name
            clist = clist + "\n"
        clist = clist + "\n"
        await ctx.send(clist)

    @commands.command(name="rch",aliases=["readch","readchannel","readmessages"],pass_context=True)
    @owner_only()
    async def rch(self,ctx,gid:int,channel:str,lim:int,isname:bool=True):
        sv = self.client.get_guild(gid)
        if sv == None:
            await ctx.send("Server not found.")
            return
        if isname:
            channel = discord.utils.get(sv.text_channels,name=channel)
        else:
            try:
                channel = int(channel)
            except:
                await ctx.send("Error: stated ID is not an integer")
                return
            channel = discord.utils.get(sv.text_channels,id=channel)
        if channel == None:
            await ctx.send("Channel not found.")
            return
        if not sv.me.permissions_in(channel).read_message_history:
            await ctx.send("Insufficient permissions to read channel history.")
            return
        msgs = await channel.history(limit=lim).flatten()
        msgs.reverse()
        for msg in msgs:
            await ctx.send("{0.author.mention}({0.author.display_name} - {0.author.name}#{0.author.discriminator}) in #{0.channel.name}: {0.content}".format(msg))
    
    @commands.command(name="rdm",aliases=["readdm"],pass_context=True)
    @owner_only()
    async def rdm(self,ctx,user:discord.User,lim:int):
        try:
            msgs = await user.history(limit=lim).flatten()
            msgs.reverse()
            for msg in msgs:
                await ctx.send("{0.author.name}: {0.content}".format(msg))
        except:
            await ctx.send("Unable to read messages from that user.")

def setup(client):
    client.add_cog(Maintenance(client))