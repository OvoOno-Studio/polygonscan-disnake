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

    # Print headers for debugging (remove or comment this out in production!)
    print(f"Headers: {headers}")

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.upgrade.chat/v1/users', headers=headers) as resp:
            # Check the status of the response
            if resp.status != 200:
                # Print response text for debugging if status is not 200
                print(f"Failed to fetch donators. HTTP status code: {resp.status}, response: {await resp.text()}")
                return None

            data = await resp.text()

    return json.loads(data)

def is_donator():
    async def predicate(ctx):
        donators = await fetch_donators()
        
        # Add error handling for when fetch_donators fails
        if not donators:
            raise commands.CheckFailure("Failed to verify donator status due to an internal error.")
        
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