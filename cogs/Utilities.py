import discord,asyncio
from discord.ext import commands

class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self,member):
        pass
        # if member.guild.id != 640759197121904650:
            # return
        # role = member.guild.get_role(640767364459266070)
        # await member.add_roles(role)

    def admin_only():
        def is_admin(ctx):
            return ctx.author.permissions_in(ctx.channel).administrator
        return commands.check(is_admin)

    @commands.command(name="sslink",aliases=["ssl","screenshare","vclink"],pass_context=True)
    async def sslink(self,ctx):
        """Displays the screenshare link for your current VC."""
        vc = ctx.author.voice.channel
        if vc == None:
            await ctx.author.send("You're not in a voice channel.")
        else:
            await ctx.send(" https://www.discordapp.com/channels/{0}/{1}".format(ctx.guild.id,vc.id))

    @commands.command(name="rolelist",pass_context=True)
    @commands.guild_only()
    @admin_only()
    async def rolelist(self,ctx,member: discord.Member = None):
        """Displays all roles in a server, or the roles of a given member."""
        sv = ctx.guild
        roles = ""
        if member == None:
            roles = "Roles in {0.guild.name}:\n".format(ctx)
            for role in sv.roles:
                if role.name != "@everyone":
                    roles = roles + role.name + "\n"
        else:
            roles = "{0.name}#{0.discriminator}'s roles:\n".format(member)
            for role in member.roles:
                if role.name != "@everyone":
                    roles = roles + role.name + "\n"
            roles = roles[:-2]
        await ctx.send(roles)

    @commands.command(name="whohas",pass_context=True)
    @commands.guild_only()
    @admin_only()
    async def whohas(self,ctx,*,rname):
        """Displays users who have the listed role (by name)."""
        sv = ctx.guild
        role = discord.utils.get(sv.roles,name=rname)
        if role == None:
            await ctx.send("Role not found.")
            return
        members = "The following users have the role {0.name}: ".format(role)
        for member in sv.members:
            if role in member.roles:
                members = members + member.name+"#"+member.discriminator + ", "
        members = members[:-2]
        await ctx.send(members)

    @commands.command(name="serverinfo",pass_context=True)
    @commands.guild_only()
    async def serverinfo(self,ctx):
        """Displays a lot of info about the server."""
        sv = ctx.guild
        emb = discord.Embed(title=sv.name)
        try:
            emb.set_thumbnail(url=sv.icon_url)
        except:
            1 == 1
        owner = sv.owner.name+"#"+sv.owner.discriminator
        emb.add_field(name="Owner",value=owner)
        region = str(sv.region)
        emb.add_field(name="Region",value=region)
        cats = str(len(sv.categories))
        emb.add_field(name="Channel Categories",value=cats)
        tcs = str(len(sv.text_channels))
        emb.add_field(name="Text Channels",value=tcs)
        vcs = str(len(sv.voice_channels))
        emb.add_field(name="Voice Channels",value=vcs)
        members = str(sv.member_count)
        emb.add_field(name="Members",value=members)
        people = 0
        bots = 0
        for member in sv.members:
            if member.bot:
                bots = bots + 1
            else:
                people = people + 1
        emb.add_field(name="Humans",value=str(people))
        emb.add_field(name="Bots",value=str(bots))
        roles = str(len(sv.roles))
        emb.add_field(name="Roles",value=roles)
        boosters = str(len(sv.premium_subscribers))
        emb.add_field(name="Nitro Boosters",value=boosters)
        nlevel = str(sv.premium_tier)
        emb.add_field(name="Nitro Level",value=nlevel)
        vurl = "N/A"
        if "VANITY_URL" in sv.features:
            vurl = await sv.vanity_invite()
        emb.add_field(name="Vanity URL",value=vurl)
        await ctx.send(embed=emb)

    @commands.command(name="whois",aliases=["userinfo","memberinfo"],pass_context=True)
    @commands.guild_only()
    async def whois(self,ctx,member: discord.Member):
        """Displays info about the given member."""
        sv = ctx.guild
        name = member.name+"#"+member.discriminator
        emb = discord.Embed(title=name,description=member.mention)
        emb.set_thumbnail(url=member.avatar_url)
        joined = str(member.joined_at)
        emb.add_field(name="Joined",value=joined)
        sboost = member.premium_since
        if sboost == None:
            sboost = "N/A"
        emb.add_field(name="Nitro Boost",value=sboost)
        reg = str(member.created_at)
        emb.add_field(name="Registered",value=reg)
        roles = str(len(member.roles))
        emb.add_field(name="Roles",value=roles)
        await ctx.send(embed=emb)

    @commands.command(name="purge",aliases=["delete"],pass_context=True)
    @commands.guild_only()
    @admin_only()
    async def purge(self,ctx,num):
        """Deletes the last number messages"""
        await ctx.channel.purge(limit=int(num)+1)

    @commands.command(name="addrole",pass_context=True)
    @commands.guild_only()
    @admin_only()
    async def addrole(self,ctx,member: discord.Member,*,rname: str):
        """Add role for given member"""
        sv = ctx.guild
        if rname == None:
            await ctx.send("role name not specified.")
            return
        role = discord.utils.get(sv.roles,name=rname)
        if role == None:
            await ctx.send("Role not found")
            return
        try:
            await member.add_roles(role)
            await ctx.send("Successfully added {0} to {1}".format(role.name,member.name+"#"+member.discriminator))
            return
        except:
            await ctx.send("I have insufficient permissions")
            return
    @commands.command(name="remrole",aliases=["removerole"],pass_context=True)
    @commands.guild_only()
    @admin_only()
    async def remrole(self,ctx,member: discord.Member,*,rname: str):
        """Remove role, for given member"""
        sv = ctx.guild
        if rname == None:
            await ctx.send("role name not specified.")
            return
        role = discord.utils.get(sv.roles,name=rname)
        if role == None:
            await ctx.send("Role not found")
            return
        if not role in member.roles:
            await ctx.send("User does not have the role specified")
            return
        try:
            await member.remove_roles(role)
            await ctx.send("Successfully removed {0} from {1}".format(role.name,member.name+"#"+member.discriminator))
            return
        except:
            await ctx.send("I have insufficient permissions")
            return
    @commands.command(name="checkrole",pass_context=True)
    @commands.guild_only()
    @admin_only()
    async def checkrole(self,ctx,member: discord.Member,*,rname: str):
        """Check if a given member has a role"""
        sv = ctx.guild
        if rname == None:
            await ctx.send("role name not specified.")
            return
        role = discord.utils.get(sv.roles,name=rname)
        if role == None:
            await ctx.send("Role not found")
            return
        if role in member.roles:
            await ctx.send("User {0} has the role {1}".format(member.name+"#"+member.discriminator,role.name))
            return
        else:
            await ctx.send("User {0} does not have the role {1}".format(member.name+"#"+member.discriminator,role.name))
            return

    @commands.command(name="poll", pass_context=True)
    @commands.guild_only()
    @admin_only()
    async def poll(self, ctx, channel : discord.TextChannel, options : int, *, prompt : str):
        """ Create a poll in the given channel with the specified number of options.  1 is thumbs up, 2 is thumbs up and thumbs down, 3-9 are numbers."""
        if options < 1:
            await ctx.send("You can't create a poll with less than one option!")
            return
        elif options > 9:
            await ctx.send("You can't create a poll with more than 9 options!")
            return
        sent = await channel.send(prompt)
        if options == 1:
            await sent.add_reaction('👍')
        elif options == 2:
            await sent.add_reaction('👍')
            await sent.add_reaction('👎')
        else:
            nums = ['one','two','three','four','five','six','seven','eight','nine']
            for i in range(options):
                await sent.add_reaction(nums[i])

def setup(client):
    client.add_cog(Utilities(client))