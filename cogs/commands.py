import json
import requests
import disnake
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from datetime import datetime
from config import APIKey
from main import is_donator

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
    Define checkTrx() - check status of transaction by hash.
    """
    @commands.command()
    @has_permissions(administrator=True)
    @is_donator()
    async def checkTrx(self, ctx: commands.Context, hash: str): 
        author = ctx.author.mention
        api_key = self.key
        counter = 0
        endpoint = f'https://api.polygonscan.com/api?module=transaction&action=gettxreceiptstatus&txhash={str(hash)}&apikey={str(api_key)}'
        response = requests.get(endpoint)  
        data = json.loads(response.text)
        print(f"User - {author} trigger command checkTrx for {hash} transaction.")
        await ctx.send(f"Return status of transaction with {str(hash)} - sent DM to {author}") 

        status = ''
        if int(data['status']) == 1:
            status = 'Successful.'
        else:
            status = 'Failed.'
        
        embed = disnake.Embed(
            title=f"Status of transaction with hash {str(hash)}",
            description="Return status code of transaction.",
            color=0x9C84EF,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="Status transaction: ",
            value=f'\n {str(status)}',
            inline=False 
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}"
        )
         
        await ctx.author.send(embed=embed) 
    """
    Define getTrxHash() - return a link to for specific transaction hash.
    """
    @commands.command()
    async def getTrxHash(self, ctx: commands.Context, hash: str): 
        author = ctx.author.mention 
        # await ctx.send(f'https://polygonscan.com/tx/{str(hash)}') 
        print(f"User - {author} trigger command getTrxHash for {hash} transaction.")
        await ctx.send(f"Generating link for transaction with {str(hash)} - sent DM to {author}")
        embed = disnake.Embed(
            title="Get transaction by hash ID",
            description="Return a link to for specific transaction hash.",
            color=0x9C84EF,
            timestamp=datetime.now()
        ) 
        embed.add_field(
            name="Link of Transaction Hash:",
            value=f'https://polygonscan.com/tx/{str(hash)}',
            inline=False
        )   
        embed.set_footer(
            text=f"Requested by {ctx.author}"
        )        
        await ctx.author.send(embed=embed)

    """
    Define getTrx() - function that will fetch all normal transactions for specific address. 
    """
    @commands.command()
    async def getTrx(self, ctx: commands.Context, address: str, offset: str):
        if(int(offset) > 25):
            await ctx.send(f"Maximum offset must be lower then 25! Aborting the command.")
            return
        
        author = ctx.author.mention
        api_key = self.key    
        counter = 0
        endpoint = f'https://api.polygonscan.com/api?module=account&action=txlist&address={str(address)}&startblock=0&endblock=99999999&page=1&offset={str(offset)}&sort=desc&apikey={str(api_key)}'
        response = requests.get(endpoint)  
        data = json.loads(response.text)
        author = ctx.author.mention
        print(f"User - {author} trigger command getTrx for {address} wallet address.")
        await ctx.send(f"Listing last {offset} internal transactions for **{address}** - sent DM to {author}")
        embed = disnake.Embed(
            title=f"{str(offset)} transactions of {str(address)}",
            description="Return list of normal transaction.",
            color=0x9C84EF,
            timestamp=datetime.now()
        )   
        
        for each in data['result']:
            counter += 1     
            ts = int(each['timeStamp'])  
            dt = datetime.fromtimestamp(ts)   
            # string = '**Transaction #' + str(counter) + '**\nTransaction Hash: ' + str(each['hash']) + '\nFrom: ' + str(each['from']) + ' \nTo: ' + str(each['to']) + '\nWhen: ' + str(dt) + '\n--------------------------------------------------------------------'
            embed.add_field(
                name=f"Transaction #{str(counter)}",
                value=f'\nTransaction Hash: {str(each["hash"])} \nFrom: {str(each["from"])} \nTo: {str(each["to"])} \nWhen: {str(dt)}',
                inline=False 
            )

        embed.set_footer(
            text=f"Requested by {ctx.author}"
        )  

        await ctx.author.send(embed=embed)    
    
    """
    Define getBalance() - get amount in WEI for single address. 
    """
    @commands.command()
    async def getBalance(self, ctx: commands.Context, address: str): 
        api_key = self.key
        author = ctx.author.mention
        endpoint = f'https://api.polygonscan.com/api?module=account&action=balance&address={str(address)}&apikey={str(api_key)}'
        response = requests.get(endpoint)  
        data = json.loads(response.text) 
        amount = float(data['result']) / ( 10 ** 18 ) # Convert WEI to MATIC 
        print(f"User - {author} trigger command getBalance for {address} wallet address.")
        await ctx.send(f"Sending MATIC balance for **{address}** - sent DM to {author}") 
        embed = disnake.Embed(
            title=f"Get balance for {str(address)}",
            description="Return amount in WEI (converted) for single address",
            color=0x9C84EF,
            timestamp=datetime.now()
        ) 
        embed.add_field(
            name="Amount in MATIC:",
            value=amount,
            inline=False
        )   
        embed.set_footer(
            text=f"Requested by {ctx.author}"
        ) 

        await ctx.author.send(embed=embed) 

    """
    Define getErc20() - return list of ERC-20 transactions, can be filtered by specific smart contract address. 
    """
    @commands.command()
    async def getErc20(self, ctx: commands.Context, address: str, contract: str, offset: str, counter=0): 
        if(int(offset) > 25):
            await ctx.send(f"Maximum offset must be lower then 25! Aborting the command.")
            return
           
        if(contract == 'SAND'):
            contract = '0xbbba073c31bf03b8acf7c28ef0738decf3695683' 
        
        author = ctx.author.mention
        api_key = self.key
        endpoint = f'https://api.polygonscan.com/api?module=account&action=tokentx&contractaddress={str(contract)}&address={str(address)}&startblock=0&endblock=99999999&page=1&offset={str(offset)}&sort=desc&apikey={str(api_key)}'
        response = requests.get(endpoint)  
        data = json.loads(response.text) 
        print(f"User - {author} trigger command getErc20 for {address} wallet address.")
        await ctx.send(f"Listing last {offset} ERC-20 transactions for **{address}** - sent DM to {author}")
        embed = disnake.Embed(
            title=f"{str(offset)} ERC-20 transactions of {str(address)}",
            description="Return list of ERC-20 transaction.",
            color=0x9C84EF,
            timestamp=datetime.now()
        ) 
        for each in data['result']:
            counter += 1     
            value = int(each['value']) / 10 ** 18 # Convert WEI to SAND
            ts = int(each['timeStamp'])  
            dt = datetime.fromtimestamp(ts)   
            # string = '**Transaction #' + str(counter) + '**\nFrom: ' + str(each['from']) + ' \nTo: ' + str(each['to']) + '\nWhen: ' + str(dt) + '\nValue: ' + str(value) + '\n--------------------------------------------------------------------'
            embed.add_field(
                name=f"Transaction #{str(counter)}",
                value=f'\nTransaction Hash: {str(each["hash"])} \nFrom: {str(each["from"])} \nTo: {str(each["to"])} \nWhen: {str(dt)} \nValue: {str(value)}',
                inline=False 
            )
        
        embed.set_footer(
            text=f"Requested by {ctx.author}"
        ) 
        
        await ctx.author.send(embed=embed) 

    """
    Define getErc721() - return list of ERC-721(NFT) transactions, can be filtered by specific smart contract address. 
    """
    @commands.command()
    async def getErc721(self, ctx: commands.Context, address: str, contract: str, offset: str, counter=0):
        if(int(offset) > 25):
            await ctx.send(f"Maximum offset must be lower then 25! Aborting the command.")
            return

        if(contract == 'LAND'):
            contract = '0x9d305a42A3975Ee4c1C57555BeD5919889DCE63F'

        api_key = self.key
        endpoint = f'https://api.polygonscan.com/api?module=account&action=tokennfttx&contractaddress={str(contract)}&address={str(address)}&startblock=0&endblock=99999999&page=1&offset={str(offset)}&sort=desc&apikey={str(api_key)}'
        response = requests.get(endpoint)
        data = json.loads(response.text)
        author = ctx.author.mention
        print(f"User - {author} trigger command getErc721 for {address} wallet address.")
        await ctx.send(f"Listing last {offset} ERC-20 transactions for **{address}** - sent DM to {author}") 
        embed = disnake.Embed(
            title=f"{str(offset)} ERC-721 transactions of {str(address)}",
            description="Return list of ERC-721 transaction.",
            color=0x9C84EF,
            timestamp=datetime.now()
        ) 
        for each in data['result']:
            counter += 1 
            ts = int(each['timeStamp'])
            dt = datetime.fromtimestamp(ts)
            #string = '**Transaction #' + str(counter) + '**\nToken Name: ' + str(each['tokenName']) + '\nToken ID:' + str(each['tokenID']) + '\nFrom: ' + str(each['from']) + '\nTo: ' + str(each['to']) + '\nWhen' + str(dt)
            embed.add_field(
                name=f"Transaction #{str(counter)}",
                value=f'\nTransaction Name: {str(each["tokenName"])} \nToken ID: {str(each["tokenID"])} \nFrom: {str(each["from"])} \nTo: {str(each["to"])} \nWhen: {str(dt)}',
                inline=False 
            )

        embed.set_footer(
            text=f"Requested by {ctx.author}"
        ) 
        
        await ctx.send(embed=embed)

    """
    Define getErc1155() - return list of ERC-721 (NFT) transactions, can be filtered by specific smart contract address. 
    """
    @commands.command()
    async def getErc1155(self, ctx: commands.Context, address: str, contract: str, offset: str, counter=0):
        if(int(offset) > 25):
            await ctx.send(f"Maximum offset must be lower then 25! Aborting the command.")
            return
        
        api_key = self.key
        endpoint = f'https://api.etherscan.io/api?module=account&action=token1155tx&contractaddress={str(contract)}&address={str(address)}&page=1&{str(offset)}=100&startblock=0&endblock=99999999&sort=asc&apikey={str(api_key)}'
        response = requests.get(endpoint)
        data = json.loads(response.text)
        author = ctx.author.mention
        print(f"User - {author} trigger command getErc721 for {address} wallet address.")
        await ctx.send(f"Listing last {offset} ERC-1155 transactions for **{address}** - sent DM to {author}") 
        embed = disnake.Embed(
            title=f"{str(offset)} ERC-1155 transactions of {str(address)}",
            description="Return list of ERC-1155 transaction.",
            color=0x9C84EF,
            timestamp=datetime.now()
        ) 
        for each in data['result']:
            counter += 1 
            ts = int(each['timeStamp'])
            dt = datetime.fromtimestamp(ts)
            #string = '**Transaction #' + str(counter) + '**\nToken Name: ' + str(each['tokenName']) + '\nToken ID:' + str(each['tokenID']) + '\nFrom: ' + str(each['from']) + '\nTo: ' + str(each['to']) + '\nWhen' + str(dt)
            embed.add_field(
                name=f"Transaction #{str(counter)}",
                value=f'\nTransaction Name: {str(each["tokenName"])} \nToken ID: {str(each["tokenID"])} \nFrom: {str(each["from"])} \nTo: {str(each["to"])} \nWhen: {str(dt)}',
                inline=False 
            )
            
        await ctx.send(embed=embed)
    
def setup(bot):
    bot.add_cog(Commands(bot))