# PolygonScan Tracker Discord Bot

"""
Discord Bot based on PolygonScan API and Disnake lib for web scrapping data from PolygonScan. 

"""

import os 
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import disnake
from disnake.ext import commands

load_dotenv()
API_KEY = os.getenv('API_KEY') # PolygonScan API Key
intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("."), intents=intents)
  
# Define getTrx - get transactions function that will fetch all normal transactions for specific address
# Maximum of 10000 records
@bot.command()
async def getTrx(ctx: commands.Context, address: str, key=API_KEY, counter=0): 
    trx = []
    endpoint = 'https://api.polygonscan.com/api?module=account&action=txlist&address=' + str(address) + '&startblock=0&endblock=99999999&page=1&offset=10&sort=desc&apikey=' + str(key)
    response = requests.get(endpoint)  
    data = json.loads(response.text) 
    for each in data['result']:
        counter += 1
        print(each['value'])
        ts = each['timeStamp']
        print(ts)
        # dt = datetime.fromtimestamp(ts) 
        string = 'Transaction #' + str(counter) + '\nFrom: ' + str(each['from']) + ' nTo: ' + str(each['to']) + '\n--------'
        await ctx.send(string)

    """ Return Normal Transactions """
    # string = "Transaction Hash: " + data['result']['hash']
    # await ctx.send('Done')

# Print the message in Python console once bot is ready for usage
@bot.event
async def on_ready():
    print(f"Welcome to the PolygonScan Tracker Bot!")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n------")


if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN')) 