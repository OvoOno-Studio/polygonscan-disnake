import disnake
from disnake.ext import commands
from replit import db

# Define is donator to separate free and paied version
def is_donator(self):
    async def predicate(ctx):
        donator_role = disnake.utils.get(ctx.guild.roles, name="OvoDonator")
        if donator_role in ctx.author.roles:
            return True
        else:
            raise commands.CheckFailure("You need to be a Donator to use this bot's commands.")
    return commands.check(predicate)

# Ensure if there is guild confiuration in database
def ensure_server_config(server_id):
    if str(server_id) not in db.keys():
        db[str(server_id)] = {}
    return db[str(server_id)] 