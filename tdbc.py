import discord, asyncio, datetime
from discord.ext import commands

TOKEN = ''

with open("token.txt") as file:
    TOKEN = file.readlines()[0]

prefix = "!!"
status = "Type !!help for help"
client = commands.Bot(command_prefix=prefix)


cogs = ["cogs.Utilities","cogs.DND","cogs.Maintenance","cogs.Fun","cogs.Activity","cogs.Annoying","cogs.Chess","cogs.Lof"]#,"cogs.Music"

if __name__ == '__main__':
    for cog in cogs:
        client.load_extension(cog)


commands.HelpCommand.hidden = True

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    await client.change_presence(activity=discord.Game(name=status))
    print("----------")
    #print(client.extensions.keys())
    """
    running = True
    q = ["quit","exit","stop","q"]
    while(running):
        console = input(">")
        args = console.split(" ")
        if console in q:
            running = False
        elif args[0].lower() == "unload":
            try:
                client.unload_extension("cogs.{}".format(args[1]))
            except:
                print("Extension {} not found.".format(args[1]))
        elif args[0].lower() == "load":
            try:
                client.load_extension("cogs.{}".format(args[1]))
            except:
                print("Extension {} not found.".format(args[1]))
        elif args[0].lower() == "status":
            exts = "Loaded extensions:"
            for i in client.extensions.keys():
                exts = exts + " " + i
            print(exts)
        else:
            print("Command not recognized. To quit, type 'quit'")
    quit()
    """

client.run(TOKEN)
