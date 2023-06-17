import disnake 
from disnake.ext import commands 
from replit import db

# Define is donator to separate free and paied version
# async def fetch_donators():
#     headers = {
#         'accept': 'application/json',
#         'Authorization': 'Bearer ' + config.BearerToken,
#         'client_id': config.ClientID,
#         'client_secret': config.Secret,
#     }

#     async with aiohttp.ClientSession() as session:
#         async with session.get('https://developers.buymeacoffee.com/api/v1/subscriptions?status=active', headers=headers) as resp:
#             # Check the status of the response
#             if resp.status != 200:
#                 # Print response text for debugging if status is not 200
#                 print(f"Failed to fetch donators. HTTP status code: {resp.status}, response: {await resp.text()}")
#                 return None
#             print('Donators fetched...')
#             data = await resp.text()

#     # Load the data into a dictionary
#     donators_data = json.loads(data)

#     # Write the data into a JSON file
#     with open('donators.json', 'w') as json_file:
#         json.dump(donators_data, json_file)

#     return donators_data

# def is_donator():
#     async def predicate(ctx):
#         # Load the donators data from the JSON file
#         with open('donators.json', 'r') as json_file:
#             donators = json.load(json_file)

#         # Add error handling for when fetch_donators fails
#         if not donators:
#             raise commands.CheckFailure("Failed to verify donator status due to an internal error.")
        
#         donator_ids = [donator['discord_id'] for donator in donators['data']]
#         if str(ctx.author.id) in donator_ids:
#             return True
#         else:
#             raise commands.CheckFailure("You need to be a Donator to use this bot's commands.")
#     return commands.check(predicate) 

# Define is donator to separate free and paied version

def is_donator():
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

# # Run the fetch_donators function every 30 minutes
# async def update_donators_periodically():
#     while True:
#         await fetch_donators()
#         await asyncio.sleep(30*60)  # wait 30 minutes