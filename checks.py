import disnake
import aiohttp
import json
from disnake.ext import commands
import config
from replit import db

# Define is donator to separate free and paied version
async def fetch_donators():
    headers = {
        'accept': 'application/json',
        'Authorization': str(config.BearerToken),
        'client_id': str(config.ClientID),
        'client_secret': str(config.Secret),
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('https://api.upgrade.chat/v1/users', headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.text()
                    return json.loads(data)
                else:
                    print(f"Failed to fetch donators. HTTP status code: {resp.status}")
                    return None
        except Exception as e:
            print(f"Failed to fetch donators due to error: {e}")
            return None

def is_donator():
    async def predicate(ctx):
        donators = await fetch_donators()
        if donators is not None:
            donator_ids = [donator['discord_id'] for donator in donators['data']]
            if str(ctx.author.id) in donator_ids:
                return True
            else:
                raise commands.CheckFailure("You need to be a Donator to use this bot's commands.")
        else:
            raise commands.CheckFailure("Failed to check donator status. Please try again later.")
    return commands.check(predicate)

# Ensure if there is guild confiuration in database
def ensure_server_config(server_id):
    if str(server_id) not in db.keys():
        db[str(server_id)] = {}
    return db[str(server_id)] 