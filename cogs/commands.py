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
        self.key = str(APIKey)

    """
    Define getTrxHash() - return a link to for specific transaction hash.
    """
    @commands.command()
    async def getTrxHash(self, ctx: commands.Context, hash: str):
        # endpoint = f'https://api.polygonscan.com/api?module=account&action=txlistinternal&txhash={str(hash)}&apikey={str(key)}'
        # response = requests.get(endpoint)
        # data = json.loads(response.text) 
        author = ctx.author.mention
        print(f"User - {author} trigger command getTrxHash for {hash}.")
        await ctx.send(f'https://polygonscan.com/tx/{str(hash)}')        

    """
    Define getTrx() - function that will fetch all normal transactions for specific address. 
    """
    @commands.command()
    async def getTrx(self, ctx: commands.Context, address: str, offset: str):
        counter = 0
        api_key = self.key    
        endpoint = f'https://api.polygonscan.com/api?module=account&action=txlist&address={str(address)}&startblock=0&endblock=99999999&page=1&offset={str(offset)}&sort=desc&apikey={str(api_key)}'
        response = requests.get(endpoint)  
        data = json.loads(response.text)
        author = ctx.author.mention
        print(f"User - {author} trigger command getTrx for {address} wallet address.")
        await ctx.send(f"Listing last {offset} internal transactions for **{address}** - by {author}") 
        for each in data['result']:
            counter += 1     
            ts = int(each['timeStamp'])  
            dt = datetime.fromtimestamp(ts)   
            string = '**Transaction #' + str(counter) + '**\nTransaction Hash: ' + str(each['hash']) + '\nFrom: ' + str(each['from']) + ' \nTo: ' + str(each['to']) + '\nWhen: ' + str(dt) + '\n--------------------------------------------------------------------'
            await ctx.send(string)

    """
    Define getBalance() - get amount in WEI for single address. 
    """
    @commands.command()
    async def getBalance(self, ctx: commands.Context, address: str): 
        api_key = self.key
        endpoint = f'https://api.polygonscan.com/api?module=account&action=balance&address={str(address)}&apikey={str(api_key)}'
        response = requests.get(endpoint)  
        data = json.loads(response.text) 
        amount = float(data['result']) / ( 10 ** 18 ) # Convert WEI to MATIC
        author = ctx.author.mention
        print(f"User - {author} trigger command getBalance for {address} wallet address.")
        await ctx.send(f"Listing MATIC balance for **{address}** - by {author}") 
        await ctx.send("Amount in **MATIC**: " + str(amount)) 

    """
    Define getErc20() - return list of ERC-20 transactions, can be filtered by specific smart contract address. 
    """
    @commands.command()
    async def getErc20(self, ctx: commands.Context, address: str, contract: str, offset: str, counter=0):
        api_key = self.key   
        if(contract == 'SAND'):
            contract = '0xbbba073c31bf03b8acf7c28ef0738decf3695683' 
        
        endpoint = f'https://api.polygonscan.com/api?module=account&action=tokentx&contractaddress={str(contract)}&address={str(address)}&startblock=0&endblock=99999999&page=1&offset={str(offset)}&sort=desc&apikey={str(api_key)}'
        response = requests.get(endpoint)  
        data = json.loads(response.text) 
        author = ctx.author.mention
        print(f"User - {author} trigger command getErc20 for {address} wallet address.")
        await ctx.send(f"Listing last {offset} ERC-20 transactions for **{address}** - by {author}") 
        for each in data['result']:
            counter += 1     
            value = int(each['value']) / 10 ** 18 # Convert WEI to SAND
            ts = int(each['timeStamp'])  
            dt = datetime.fromtimestamp(ts)   
            string = '**Transaction #' + str(counter) + '**\nFrom: ' + str(each['from']) + ' \nTo: ' + str(each['to']) + '\nWhen: ' + str(dt) + '\nValue: ' + str(value) + '\n--------------------------------------------------------------------'
            await ctx.send(string) 
    
    """
    Define getErc721() - return list of ERC-721 (NFT) transactions, can be filtered by specific smart contract address. 
    """
    @commands.command()
    async def getErc721(self, ctx: commands.Context, address: str, contract: str, offset: str, counter=0):
        api_key = self.key
        if(contract == 'LAND'):
            contract = '0x9d305a42A3975Ee4c1C57555BeD5919889DCE63F'

        endpoint = f'https://api.polygonscan.com/api?module=account&action=tokennfttx&contractaddress={str(contract)}&address={str(address)}&startblock=0&endblock=99999999&page=1&offset={str(offset)}&sort=desc&apikey={str(api_key)}'
        response = requests.get(endpoint)
        data = json.loads(response.text)
        author = ctx.author.mention
        print(f"User - {author} trigger command getErc721 for {address} wallet address.")
        await ctx.send(f"Listing last {offset} ERC-20 transactions for **{address}** - by {author}") 
        for each in data['result']:
            counter += 1 
            ts = int(each['timeStamp'])
            dt = datetime.fromtimestamp(ts)
            string = '**Transaction #' + str(counter) + '**\nToken Name: ' + str(each['tokenName']) + '\nToken ID:' + str(each['tokenID']) + '\nFrom: ' + str(each['from']) + '\nTo: ' + str(each['to']) + '\nWhen' + str(dt)
            await ctx.send(string)

    """
    Define getErc1155() - return list of ERC-721 (NFT) transactions, can be filtered by specific smart contract address. 
    """
    @commands.command()
    async def getErc1155(self, ctx: commands.Context, address: str, contract: str, offset: str, counter=0):
        api_key = self.key
        endpoint = f'https://api.etherscan.io/api?module=account&action=token1155tx&contractaddress={str(contract)}&address={str(address)}&page=1&{str(offset)}=100&startblock=0&endblock=99999999&sort=asc&apikey={str(api_key)}'
        response = requests.get(endpoint)
        data = json.loads(response.text)
        author = ctx.author.mention
        print(f"User - {author} trigger command getErc721 for {address} wallet address.")
        await ctx.send(f"Listing last {offset} ERC-1155 transactions for **{address}** - by {author}") 
        for each in data['result']:
            counter += 1 
            ts = int(each['timeStamp'])
            dt = datetime.fromtimestamp(ts)
            string = '**Transaction #' + str(counter) + '**\nToken Name: ' + str(each['tokenName']) + '\nToken ID:' + str(each['tokenID']) + '\nFrom: ' + str(each['from']) + '\nTo: ' + str(each['to']) + '\nWhen' + str(dt)
            await ctx.send(string)
    
def setup(bot):
    bot.add_cog(Commands(bot))