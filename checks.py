import disnake
from disnake.ext import commands
from replit import db

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

# Ensure if there is guild confiuration in database
def ensure_server_config(server_id):
    server_id = str(server_id)  # Convert server_id to a string
    if server_id not in db or not isinstance(db[server_id], dict):
        db[server_id] ={}

    return db[server_id]