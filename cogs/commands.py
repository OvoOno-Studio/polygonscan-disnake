import json
import requests
import disnake
# from disnake import Embed
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from datetime import datetime
import csv
import io
from config import APIKey
from checks import is_donator

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
    Define handle_erc_transactions - check CSV file for transaction.
    """
    async def handle_erc_transactions(self, ctx, address, contract, offset, contract_type, counter=0):
        print(f"Inside handle_erc_transactions - Contract: {contract_type}")  # Add this print statement
        if contract_type == 'ERC20':
            if contract == 'SAND':
                contract = '0xbbba073c31bf03b8acf7c28ef0738decf3695683'
            endpoint = f'https://api.polygonscan.com/api?module=account&action=tokentx&contractaddress={str(contract)}&address={str(address)}&startblock=0&endblock=99999999&page=1&offset={str(offset)}&sort=desc&apikey={str(self.key)}'
        elif contract_type == 'ERC721':
            if contract == 'LAND':
                contract = '0x9d305a42A3975Ee4c1C57555BeD5919889D9aB1F'
            endpoint = f'https://api.polygonscan.com/api?module=account&action=tokennfttx&contractaddress={str(contract)}&address={str(address)}&startblock=0&endblock=99999999&page=1&offset={str(offset)}&sort=desc&apikey={str(self.key)}'
        elif contract_type == 'ERC1155':
            if contract == 'ITEMS':
                contract = '0x10162c83AfcE2cA121eCA75A6Ae32A28D1d0145C'
            endpoint = f'https://api.polygonscan.com/api?module=account&action=token1155tx&contractaddress={str(contract)}&address={str(address)}&startblock=0&endblock=99999999&page=1&offset={str(offset)}&sort=desc&apikey={str(self.key)}'

        r = requests.get(endpoint)
        data = json.loads(r.text) 

        if data['status'] != '1':
            return await ctx.send(f":x: Error fetching {contract_type} transactions for {address}")

        # Build the message with Markdown formatting
        message_lines = [
            f"**__{contract_type} Transactions for {address}__** :sparkles:",
            "",  # Empty line for spacing
        ]

        for each in data['result']:
            counter += 1
            ts = int(each['timeStamp'])
            dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            value = ''
            if contract_type == 'ERC20':
                value = f"Value: **{int(each['value']) / 10 ** 18:.8f}**"
            elif contract_type == 'ERC721' or contract_type == 'ERC1155':
                value = f"Token Name: **{each['tokenName']}** | Token ID: **{each['tokenID']}**"

            line = f"**{counter}.** `{each['hash'][:6]}...{each['hash'][-4:]}`\nFrom: `{each['from'][:6]}...{each['from'][-4:]}` | To: `{each['to'][:6]}...{each['to'][-4:]}` | When: **{dt}** | {value}"
            message_lines.append(line)

        # Split the message into chunks of 4000 characters or fewer
        def split_message(lines, max_length=4000):
            chunks = []
            current_chunk = []
            current_length = 0

            for line in lines:
                line_length = len(line) + 1  # Add 1 for the newline character
                if current_length + line_length <= max_length:
                    current_chunk.append(line)
                    current_length += line_length
                else:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = [line]
                    current_length = line_length

            if current_chunk:
                chunks.append("\n".join(current_chunk))

            return chunks

        message_chunks = split_message(message_lines)

        # Send each chunk as a separate message
        for chunk in message_chunks:
            try:
                await ctx.author.send(content=chunk)
            except Exception as e:
                print(f"Error while sending formatted message chunk: {e}")

    """
    Define checkTrx() - check status of transaction by hash.
    """
    @commands.command() 
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
    @has_permissions(administrator=True)
    @is_donator()
    @commands.command() 
    async def getErc20(self, ctx, address: str, contract: str = 'SAND', offset: int = 100):
        await self.handle_erc_transactions(ctx, address, contract, offset, 'ERC20')

    """
    Define getErc721() - return list of ERC-721(NFT) transactions, can be filtered by specific smart contract address. 
    """
    @commands.command()
    async def getErc721(self, ctx, address: str, contract: str = 'LAND', offset: int = 30):
        await self.handle_erc_transactions(ctx, address, contract, offset, 'ERC721')

    """
    Define getErc1155() - return list of ERC-721 (NFT) transactions, can be filtered by specific smart contract address. 
    """
    @commands.command()
    async def getErc1155(self, ctx, address: str, contract: str = 'ITEMS', offset: int = 30):
        await self.handle_erc_transactions(ctx, address, contract, offset, 'ERC1155')
    
def setup(bot):
    bot.add_cog(Commands(bot))