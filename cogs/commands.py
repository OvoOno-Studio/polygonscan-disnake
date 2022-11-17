import json
import requests
import disnake
from disnake.ext import commands  
from datetime import datetime
from config import APIKey

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True
key = str(APIKey)  
bot = commands.Bot(command_prefix=commands.when_mentioned_or("ps-"), intents=intents)


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    Define getTrx() - function that will fetch all normal transactions for specific address.
    - Return 10 transaction.
    """
    @commands.command()
    async def getTrx(self, ctx: commands.Context, address: str, key=key, counter=0):    
        endpoint = 'https://api.polygonscan.com/api?module=account&action=txlist&address=' + str(address) + '&startblock=0&endblock=99999999&page=1&offset=10&sort=desc&apikey=' + str(key)
        response = requests.get(endpoint)  
        data = json.loads(response.text)
        
        for each in data['result']:
            counter += 1     
            ts = int(each['timeStamp'])  
            dt = datetime.fromtimestamp(ts)   
            string = 'Transaction #' + str(counter) + '\nFrom: ' + str(each['from']) + ' \nTo: ' + str(each['to']) + '\nWhen: ' + str(dt) + '\n--------------------------------------------------------------------'
            await ctx.send(string)

    """
    Define getBalance() - get amount in WEI for single address. 
    """
    @commands.command()
    async def getBalance(self, ctx: commands.Context, address: str, key=key): 
        endpoint = f'https://api.polygonscan.com/api?module=account&action=balance&address={str(address)}&apikey={str(key)}'
        response = requests.get(endpoint)  
        data = json.loads(response.text) 
        amount = float(data['result']) / ( 10 ** 18 ) # Convert WEI to MATIC
        await ctx.send("Amount in MATIC: " + str(amount)) 

    """
    Define getErc20() - return list of ERC-20 transactions, can be filtered by specific smart contract address. 
    """
    @commands.command()
    async def getErc20(self, ctx: commands.Context, address: str, contract: str, key=key, counter=0):
        if(contract == 'SAND'):
            contract = '0xbbba073c31bf03b8acf7c28ef0738decf3695683'
        else:
            return 
        endpoint = f'https://api.polygonscan.com/api?module=account&action=tokentx&contractaddress={str(contract)}&address={str(address)}&startblock=0&endblock=99999999&page=1&offset=5&sort=desc&apikey={str(key)}'
        response = requests.get(endpoint)  
        data = json.loads(response.text)  
        for each in data['result']:
            counter += 1     
            value = int(each['value']) / 10 ** 18 # Convert WEI to SAND
            ts = int(each['timeStamp'])  
            dt = datetime.fromtimestamp(ts)   
            string = 'Transaction #' + str(counter) + '\nFrom: ' + str(each['from']) + ' \nTo: ' + str(each['to']) + '\nWhen: ' + str(dt) + '\nValue: ' + str(value) + '\n--------------------------------------------------------------------'
            await ctx.send(string) 

def setup(bot):
    bot.add_cog(Commands(bot))

