import json
import requests
import disnake
import time 
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from disnake import Option, OptionType, Embed, Color
from datetime import datetime
import csv
import io
import os
from io import StringIO
from config import APIKey, API2Key
from checks import is_donator 

class Scrape(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.key = str(APIKey)

    @staticmethod
    def get_token_holders(token_address, num_transactions=1000, page_size=100, num_pages=40):
        holders = set() 
        key = str(APIKey)
        for page in range(1, num_pages + 1):
            url = f'https://api.polygonscan.com/api?module=account&action=tokentx&contractaddress={token_address}&page={page}&offset={page_size}&sort=desc&apikey={key}'
            response = requests.get(url)
            data = json.loads(response.text)

            print(f"Fetching page {page}: {url}")

            if data['status'] == '1':
                transactions = data['result']
                page_holders = {tx['from'] for tx in transactions}.union({tx['to'] for tx in transactions})
                holders.update(page_holders)
            else:
                break

            time.sleep(1.5)  # Add a delay between requests

        print(f"Total token holders fetched: {len(holders)}")
        return holders if holders else None
    
    async def send_csv(self, ctx, holders):
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow(['Address'])

        for address in holders:
            csv_writer.writerow([address])

        csv_buffer.seek(0)
        file = disnake.File(csv_buffer, "token_holders.csv")
        await ctx.author.send("Here is the list of token holders:", file=file) 

    """
    Define get_token_holder - send CSV file as DM of token holders wallets .
    """
    @is_donator()
    @commands.slash_command(name='get_token_holders', description="Send CSV file of token holders as DM")
    async def get_token_holder(self, ctx, token_address: str = None):
        if token_address is None:
            await ctx.send("Please provide a valid token address.")
            return

        holders = self.get_token_holders(token_address)
        if holders is None:
            await ctx.send("Failed to fetch token holders. Please check the token address and try again.")
        else:
            print("Sending CSV file...") 
            await self.send_csv(ctx, holders)
            await ctx.send("Token holders list sent as a CSV file in a direct message.")

    """
    Define load_contract_addresses - load contracts.json file for token/contract addresses.
    """
    def load_contract_addresses(self):
        with open('contracts.json', 'r') as f:
            return json.load(f)
    
    """
    Define generate_csv() - generate csv file for donators.
    """
    async def generate_csv(self, data, contract_type, contract_address, address):
        address_lower = address.lower()
        print(f'Generating CSV file... for {contract_type}')
        csvfile = io.StringIO()
        fieldnames = [
            'Transaction Hash',
            'Block number',
            'Unix Timestamp',
            'Date time',
            'From',
            'To',
            'Contract Address',
            'Transaction Type',
        ]

        if contract_type == 'ERC20':
            fieldnames.extend(['Transfered token value', 'Token name'])
        else:
            fieldnames.append('Token ID')

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()

        for each in data['result']:
            ts = int(each['timeStamp'])
            dt = datetime.fromtimestamp(ts)

            # Determine transaction type for ERC20, ERC721, and ERC1155
            if contract_type == 'ERC20':
                transaction_type = 'incoming' if each['to'] == address_lower else 'outgoing'
            else:
                transaction_type = 'incoming' if each['to'] == address_lower else 'outgoing'
                if each['from'] == '0x0000000000000000000000000000000000000000':
                    transaction_type = 'mint'

            # Skip transactions that do not involve the user's address
            if each['from'] != address_lower and each['to'] != address_lower:
                continue

            row = {
                'Transaction Hash': each['hash'],
                'Block number': each['blockNumber'],
                'Unix Timestamp': each['timeStamp'],
                'Date time': dt,
                'From': each['from'],
                'To': each['to'],
                'Contract Address': contract_address,
                'Transaction Type': transaction_type,
            }

            if contract_type == 'ERC20':
                value = int(each['value']) / 10 ** 18
                row['Transfered token value'] = value
                row['Token name'] = each['tokenName']
            else:
                row['Token ID'] = each['tokenID']

            writer.writerow(row)

        csvfile.seek(0)
        print("CSV generated.")
        return disnake.File(csvfile, f'{contract_type}_transactions_{address_lower}.csv')
    
    """
    Define handle_erc_transactions - check CSV file for transaction.
    """
    async def handle_erc_transactions(self, ctx, address, contract, offset, contract_type, counter=0):
        print(f"Inside handle_erc_transactions - Contract: {contract_type}")  # Add this print statement
        contracts_data = self.load_contract_addresses() 
        contract_address = contracts_data.get(contract_type, {}).get(contract, None)
        if not contract_address:
            return await ctx.send(f"Unknown contract '{contract}' for type {contract_type}")
        
        action = ''
        if contract_type == "ERC20":
            action = "tokentx"
        if contract_type == "ERC721":
            action = "tokennfttx"
        if contract_type == "ERC1155":
            action = "token1155tx"
        
        endpoint = f'https://api.polygonscan.com/api?module=account&action={str(action)}&contractaddress={str(contract_address)}&address={str(address)}&startblock=0&endblock=99999999&page=1&offset={str(offset)}&sort=desc&apikey={str(self.key)}'
        r = requests.get(endpoint)
        data = json.loads(r.text) 

        if data['status'] != '1':
            if data['status'] == '0':
                return await ctx.send(f"😑 Not found any {contract_type} transactions for {address}") 
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
                value = f"💰 Value: **{int(each['value']) / 10 ** 18:.8f}**"
            elif contract_type == 'ERC721' or contract_type == 'ERC1155':
                value = f"💸 Token Name: **{each['tokenName']}** | 🆔 Token ID: **{each['tokenID']}**"

            line = f"**{counter}.** `{each['hash']}`\n 🧑 From: `{each['from']}` \n 👉 To: `{each['to']}` \n ⏲️ When: **{dt}** | {value}"
            message_lines.append(line)

        # Split the message into chunks of 2000 characters or fewer
        def split_message(lines, max_length=2000):
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

        if is_donator():
            print("Calling generate_csv...")
            # Call the generate_csv() method to create the CSV file
            csv_file = await self.generate_csv(data, contract_type, contract, address) 
            await ctx.send(content="User donator ..sending CSV file as DM!") 
            # Send the CSV file as an attachment
            await ctx.author.send(file=csv_file) 

            return

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
    Define balance() - get amount in WEI for single address. 
    """
    @commands.command()
    async def balance(self, ctx: commands.Context, address: str): 
        api_key = self.key
        author = ctx.author.mention
        endpoint = f'https://api.polygonscan.com/api?module=account&action=balance&address={str(address)}&apikey={str(api_key)}'
        response = requests.get(endpoint)  
        data = json.loads(response.text) 
        amount = float(data['result']) / ( 10 ** 18 ) # Convert WEI to MATIC  
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
    Define creator() - Returns a contract's deployer address and transaction hash it was created, up to 5 at a time. 
    """    
    @commands.command()
    async def creator(self, ctx: commands.Context, *addresses: str):
        author = ctx.author.mention

        # Concatenate all addresses into a comma-separated string
        addresses_str = ','.join(addresses)

        # Fetch the contract creation data from the API
        url = f"https://api.polygonscan.com/api?module=contract&action=getcontractcreation&contractaddresses={addresses_str}&apikey={str(APIKey)}"
        response = requests.get(url)
        data = json.loads(response.text)
        results = data['result']

        message = f"**Contract Creator and Creation Tx Hash**\n"

        # Loop through results to format the message
        for result in results:
            contractAddress = result['contractAddress']
            contractCreator = result['contractCreator']
            txHash = result['txHash']

            message += (
                f"\n"
                f"🔹 **Contract Address**: {contractAddress}\n"
                f"👤 **Contract Creator**: {contractCreator}\n"
                f"🔗 **TxHash**: {txHash}\n"
                f"------------------------------------------\n"
            )

        # Send DM to the author
        await ctx.send(f"Sending Contract Creator and Creation Tx Hash for **{addresses_str}** - sent DM to {ctx.author}") 
        await ctx.author.send(message)

    """
    Define abi() - Returns the contract Application Binary Interface ( ABI ) of a verified smart contract. 
    """
    @commands.command()
    async def abi(self, ctx: commands.Context, address: str):
        key = APIKey
        url = f"https://api.polygonscan.com/api?module=contract&action=getabi&address={str(address)}&apikey={str(key)}"
        response = requests.get(url)
        data = json.loads(response.text)

        # Parse the 'result' string into a Python object
        abi = json.loads(data['result'])
        pretty_abi = json.dumps(abi, indent=4)
        
        # Create a temporary file
        temp_file = f'abi_{address}.json'

        # Write the ABI to the file
        with open(temp_file, 'w') as f:
            f.write(pretty_abi)

        # Send the file in a direct message to the user
        try:
            with open(temp_file, 'rb') as f:
                await ctx.send(f"Sending ABI JSON  for **{address}** - sent DM to {ctx.author}") 
                await ctx.author.send(file=disnake.File(f))
        except Exception as e:
            print(f"An error occurred when trying to send a message: {e}")

        # Cleanup: Remove the temporary file after it's used
        os.remove(temp_file)
    
    """
    Define gas() - Returns the current Safe, Proposed and Fast gas prices
    """ 
    @commands.slash_command(
        name="gas",
        description="Returns the current Safe, Proposed and Fast gas prices",
        options=[
            Option(
                name="blockchain",
                description="Choose Ethereum or Polygon",
                type=OptionType.string,
                choices=["ethereum", "polygon"],
                required=True
            )
        ]
    )
    async def gas(self, inter, blockchain: str):
        key = APIKey
        key2 = API2Key

        if blockchain.lower() == "ethereum":
            url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={key2}"
            blockchain_name = "Ethereum"
            color = Color.blue()  # You can choose a color to represent Ethereum
        elif blockchain.lower() == "polygon":
            url = f"https://api.polygonscan.com/api?module=gastracker&action=gasoracle&apikey={key}"
            blockchain_name = "Polygon"
            color = Color.red()  # You can choose a color to represent Polygon
        else:
            await inter.response.send_message("Invalid blockchain choice, choose either Ethereum or Polygon")
            return
        
        response = requests.get(url)
        data = json.loads(response.text)

        try:
            safe_gas = float(data['result']['SafeGasPrice'])
            propose_gas = float(data['result']['ProposeGasPrice'])
            fast_gas = float(data['result']['FastGasPrice'])
        except ValueError:
            await inter.response.send_message("Unable to retrieve valid gas prices from the API.")
            return
        
        conclusion = "Low"
        if any(gas > 100 for gas in [safe_gas, propose_gas, fast_gas]):
            conclusion = "High"
        elif any(gas > 50 for gas in [safe_gas, propose_gas, fast_gas]):
            conclusion = "Medium"
        
        embed = Embed(title=f":fuelpump: {blockchain_name} Gas Oracle", color=color)
        embed.set_author(name="PS Scanner", url="https://polygonscan-scrapper.ovoono.studio/", icon_url="https://i.imgur.com/97feYXR.png")
        embed.add_field(name="Last Block", value=data['result']['LastBlock'], inline=False)
        embed.add_field(name="Safe Gas Price", value=f"{safe_gas} Gwei", inline=True)
        embed.add_field(name="Propose Gas Price", value=f"{propose_gas} Gwei", inline=True)
        embed.add_field(name="Fast Gas Price", value=f"{fast_gas} Gwei", inline=True)
        embed.add_field(name="Suggested Base Fee", value=data['result']['suggestBaseFee'], inline=False)
        embed.add_field(name="Gas Used Ratio", value=data['result']['gasUsedRatio'], inline=False)
        embed.add_field(name="Conclusion", value=f"Gas is {conclusion}", inline=False)
        embed.set_footer(text=f"Powered by OvoOno Studio")
        
        if 'UsdPrice' in data['result']:
            embed.add_field(name="USD Price", value=f"${data['result']['UsdPrice']}", inline=True)
        
        await inter.response.send_message(embed=embed)

    """
    Define getErc20() - return list of ERC-20 transactions, can be filtered by specific smart contract address. 
    """
    @is_donator()
    @commands.slash_command(
        name="get_erc20_transactions", 
            description="Return list of ERC-20 transactions, can be filtered by specific smart contract address",
            options=[
                disnake.Option("address", "Address for scrapping.", type=disnake.OptionType.string, required=True),
                disnake.Option("contract", "ERC-20 smart contract", type=disnake.OptionType.string, required=True) 
            ]
        ) 
    async def getErc20(self, ctx, address: str, contract: str = 'SAND', offset: int = 100):
        await self.handle_erc_transactions(ctx, address, contract, offset, 'ERC20')

    """
    Define getErc721() - return list of ERC-721(NFT) transactions, can be filtered by specific smart contract address. 
    """
    @is_donator()
    @commands.slash_command(
        name="get_erc_721_transactions",
        description="Return list of ERC-721 transactions, can be filtered by specific smart contract address",
        options=[
            disnake.Option("address", "Address for scrapping.", type=disnake.OptionType.string, required=True),
            disnake.Option("contract", "ERC-721 smart contract", type=disnake.OptionType.string, required=True)
        ]
    )
    async def getErc721(self, ctx, address: str, contract: str, offset: int = 30, contract_type: str = 'ERC721'):
        await self.handle_erc_transactions(ctx, address, contract, offset, contract_type)

    """
    Define getErc1155() - return list of ERC-721 (NFT) transactions, can be filtered by specific smart contract address. 
    """
    @is_donator()
    @commands.slash_command(
        name="get_erc_1155_transactions",
        description="Return list of ERC-1155 transactions, can be filtered by specific smart contract address",
        options=[
            disnake.Option("address", "Address for scrapping.", type=disnake.OptionType.string, required=True),
            disnake.Option("contract", "ERC-1155 smart contract", type=disnake.OptionType.string, required=True)
        ]
    )
    async def getErc1155(self, ctx, address: str, contract: str = 'ITEMS', offset: int = 30):
        await self.handle_erc_transactions(ctx, address, contract, offset, 'ERC1155')
    
def setup(bot):
    bot.add_cog(Scrape(bot))