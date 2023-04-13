import disnake
from disnake.ext import commands

# Define is donator to separate free and paied version
def is_donator():
    async def predicate(ctx):
        donator_role = disnake.utils.get(ctx.guild.roles, name="OvoDonator")
        if donator_role in ctx.author.roles:
            return True
        else:
            await ctx.send("You need to be a Donator to use this bot's commands.")
            return False
    return commands.check(predicate)