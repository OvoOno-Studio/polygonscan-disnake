import json 
from disnake.ext import commands 
from replit import db 

# Define is donator to separate free and paied version
def is_donator():
    async def predicate(ctx):
        # Load the donators data from the JSON file
        with open('donators.json', 'r') as json_file:
            donators = json.load(json_file)

        # Check if the author's id is in the list of donator ids
        if ctx.author.id in [donator['user_id'] for donator in donators]:
            return True
        else:
            raise commands.CheckFailure("You need to be a Donator to use this bot's commands.")
    return commands.check(predicate)

# Ensure if there is guild confiuration in database
def ensure_server_config(server_id):
    if str(server_id) not in db.keys():
        db[str(server_id)] = {}
    return db[str(server_id)]   