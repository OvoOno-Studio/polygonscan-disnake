import disnake
import aiohttp
import json
from disnake.ext import commands
from replit import db

# Define is donator to separate free and paied version
async def fetch_donators():
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer your_token_here',
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.upgrade.chat/v1/users', headers=headers) as resp:
            data = await resp.text()

    return json.loads(data)

def is_donator():
    async def predicate(ctx):
        donators = await fetch_donators()
        donator_ids = [donator['discord_id'] for donator in donators['data']]
        if str(ctx.author.id) in donator_ids:
            return True
        else:
            raise commands.CheckFailure("You need to be a Donator to use this bot's commands.")
    return commands.check(predicate)

# Ensure if there is guild confiuration in database
def ensure_server_config(server_id):
    if str(server_id) not in db.keys():
        db[str(server_id)] = {}
    return db[str(server_id)] 