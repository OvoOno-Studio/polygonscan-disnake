import aiohttp
import asyncio
import csv
import io
import disnake 
from config import get_transaction_channel, get_price_alert_channel, get_wallet_address
from disnake.ext import commands 
from disnake import Option, OptionType, Embed, Color
from config import jwt
from checks import is_donator
from web3 import Web3

class Friend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.friend_api = 'https://prod-api.kosetto.com'
        self.w3 = Web3(Web3.HTTPProvider('https://base-mainnet.g.alchemy.com/v2/8XQtglDUSx3Sp7MuWwhk3K1X9x2vrhJo'))
        self.wallet_address = '0xCF205808Ed36593aa40a44F10c7f7C2F67d4A4d4' 
        self.guild_data = {}
        self.bot.loop.create_task(self.check_transactions())
        self.bot.loop.create_task(self.keys_alerts())
     
    async def check_transactions(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                latest_block = self.w3.eth.block_number
                block = self.w3.eth.get_block(latest_block, full_transactions=True)

                for tx in block['transactions']:
                    tx_to = tx['to']
                    tx_value = int(tx['value'])

                    # Check the destination address and value of the transaction
                    if (
                        tx_to.lower() == self.wallet_address.lower()
                        and tx_value == 0
                    ):
                        await self.send_embedded_message(tx)

                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error checking transactions: {e}")

    async def send_embedded_message(self, transaction):
        # Create an embedded message with transaction details
        embed = disnake.Embed(
            title="New user registered! 🆕",
            color=0x9C84EF,
            description="New 'Buy Shares' transaction method with 0 ETH."
        )
        embed.add_field(name="From Address", value=transaction['from'], inline=False)
        embed.add_field(name="To Address", value=transaction['to'], inline=False)

        # Format the transaction hash as a clickable link
        transaction_hash = transaction['hash'].hex()
        transaction_url = f"https://basescan.org/tx/{transaction_hash}"
        embed.add_field(name="Transaction Hash", value=f"[{transaction_hash}]({transaction_url})", inline=False)

        embed.add_field(name="Gas Price", value=f"{transaction['gasPrice']} Wei", inline=False) 

        for guild in self.bot.guilds:
            channel_id = get_transaction_channel(guild.id)
            channel = self.bot.get_channel(channel_id)
            
            if channel is not None:
                try:
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"Error sending message: {e}")
                
    async def keys_alerts(self):  
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild in self.bot.guilds:
                guild_id = guild.id
                wallet_address = get_wallet_address(guild_id)
                channel_id = get_price_alert_channel(guild_id)
                channel = self.bot.get_channel(channel_id)  
                try:
                    latest_block = self.w3.eth.block_number 
                    block = self.w3.eth.get_block(latest_block, full_transactions=True)
                    # print('Block:')
                    # print(block)
                    for tx in block['transactions']:
                        tx_to = tx['to']
                        tx_from = tx['from'] 
                        print(tx)
                        if tx_to.lower() == wallet_address.lower() or tx_from.lower() == wallet_address.lower(): 
                            print('Creating embed message..')
                            embed = disnake.Embed(
                                title="Transaction Alert",
                                description="Incoming or outgoing transaction detected!",
                                color=0x9C84EF
                            )
                            embed.add_field(name="From Address", value=f'{str(tx_from)}', inline=False)
                            embed.add_field(name="To Address", value=f'{str(tx_to)}', inline=False)
                            embed.add_field(name="Transaction Hash", value=tx['hash'].hex(), inline=False)
                            embed.add_field(name="Gas Price", value=f"{tx['gasPrice']} Wei", inline=False)
                            
                            await channel.send(embed=embed)
                    await asyncio.sleep(60)  # Check every 60 seconds
                except Exception as e:
                    print(f"Error checking transactions: {e}")
        
    @is_donator()
    @commands.slash_command(name="user", description="Get details about a user by address.")
    async def user_by_address(self, ctx, user_wallet):
        if user_wallet is None:
            await ctx.send("Please provide a valid user_wallet.")
            return

        try:
            endpoint = f'{str(self.friend_api)}/users/{str(user_wallet)}'
            headers = {
                'Authorization': str(jwt),
                'Content-Type': 'application/json',
                'Accept': 'application json',
                'Referer': 'https://www.friend.tech/'
            }

            async with self.session.get(endpoint, headers=headers) as response:
                if response.status != 200:
                    print(f"Failed to connect to API, status code: {response.status}, message: {await response.text()}")
                    return None

                json_data = await response.json()

                # Create an embedded message
                embed = disnake.Embed(title="User Details", color=0x9C84EF)  # Set the embed title and color (Discord blue)
                twitter_username = json_data.get("twitterUsername", "")
                twitter_url = f"https://x.com/{twitter_username}"
                # Add fields to the embed for user details
                embed.add_field(name="User Address", value=json_data.get("address", ""), inline=False)
                embed.add_field(name="Twitter Username", value=f"[{twitter_username}]({twitter_url})", inline=True)
                embed.add_field(name="Twitter Name", value=json_data.get("twitterName", ""), inline=True)
                embed.add_field(name="Twitter User ID", value=json_data.get("twitterUserId", ""), inline=False)
                embed.add_field(name="Last Online", value=json_data.get("lastOnline", ""), inline=False)
                embed.add_field(name="Holder Count", value=json_data.get("holderCount", ""), inline=True)
                embed.add_field(name="Holding Count", value=json_data.get("holdingCount", ""), inline=True)
                embed.add_field(name="Share Supply", value=json_data.get("shareSupply", ""), inline=False)
                embed.add_field(name="Display Price", value=json_data.get("displayPrice", ""), inline=False)
                embed.add_field(name="Lifetime Fees Collected", value=json_data.get("lifetimeFeesCollectedInWei", ""), inline=False)

                # Add the Twitter profile picture as the embed thumbnail
                embed.set_thumbnail(url=json_data.get("twitterPfpUrl", ""))

                # Send the embedded message to the channel
                await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error in user_by_address: {e}")
            await ctx.send('User not found!')
        
    @is_donator()
    @commands.slash_command(name="holdings_activity", description="Gets a history of trades for a user.")
    async def holdings_activity(self, ctx, user_wallet):
        if user_wallet is None:
            await ctx.send("Please provide a valid user_wallet.")
            return

        embed = disnake.Embed(
                title=f"Holding activity for: {user_wallet}",
                description="Gets a history of trades for a user.",
                color=0x9C84EF
            )
        embed.add_field(
            name="Response status:",
            value=f'CSV file sent!',
            inline=False 
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}"
        )

        try:
            endpoint = f'{str(self.friend_api)}/holdings-activity/{str(user_wallet)}'

            async with self.session.get(endpoint) as response:
                if response.status != 200:
                    print(f"Failed to connect to API, status code: {response.status}, message: {await response.text()}")
                    return None

                json_data = await response.json()

                # Create a CSV string from the JSON data
                csv_data = io.StringIO()
                csv_writer = csv.writer(csv_data)
                csv_writer.writerow(["Trader Address", "Trader Username", "Subject Address", "Subject Username", "Is Buy", "Share Amount", "ETH Amount", "Created At"])

                for event in json_data.get("events", []):
                    trader = event.get("trader", {})
                    subject = event.get("subject", {})
                    csv_writer.writerow([trader.get("address", ""), trader.get("username", ""),
                                        subject.get("address", ""), subject.get("username", ""),
                                        event.get("isBuy", ""), event.get("shareAmount", ""),
                                        event.get("ethAmount", ""), event.get("createdAt", "")])

                # Reset the file-like object for reading
                csv_data.seek(0)

                # Send the CSV file as a direct message (DM)
                file = disnake.File(csv_data, filename="holdings_activity.csv") # type: ignore
                await ctx.author.send(file=file, content="Here is the CSV file with the holdings activity.")
                await ctx.send(embed=embed)
        except Exception as e:
            print(f"Error in holdings_activity: {e}")
    
    @is_donator()
    @commands.slash_command(name="search_friends", description="Search users by their twitter handle.")
    async def search_friends(self, ctx, username):
        if username is None:
            await ctx.send("Please provide a valid username!")
            return

        try:
            endpoint = f'{str(self.friend_api)}/search/users?username={str(username)}'
            headers = {
                'Authorization': str(jwt),
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Referer': 'https://www.friend.tech/',
                'Accept-Encoding': 'gzip'
            }
            embed = disnake.Embed(
                title=f"Search friends for: {username}",
                description="Search users by their twitter handle.",
                color=0x9C84EF
            )
            embed.add_field(
                name="Response status:",
                value=f'CSV file sent!',
                inline=False 
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}"
            )

            async with self.session.get(endpoint, headers=headers) as response:
                if response.status != 200:
                    print(f"Failed to connect to API, status code: {response.status}, message: {await response.text()}")
                    return None

                json_data = await response.json()

                # Create a CSV string from the JSON data
                csv_data = io.StringIO()
                csv_writer = csv.writer(csv_data)
                csv_writer.writerow(["Address", "Twitter Username", "Twitter Name", "Twitter Pfp URL", "Twitter User ID"])
                
                for user in json_data.get("users", []):
                    csv_writer.writerow([user.get("address", ""), user.get("twitterUsername", ""),
                                        user.get("twitterName", ""), user.get("twitterPfpUrl", ""),
                                        user.get("twitterUserId", "")])

                # Reset the file-like object for reading
                csv_data.seek(0)

                # Send the CSV file as a direct message (DM)
                file = disnake.File(csv_data, filename="friends.csv") # type: ignore
                await ctx.author.send(file=file, content=f"Search results for: {username}.")
                await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error in search_friends: {e}")
      
    @is_donator()
    @commands.slash_command(name="events", description="Gets a history of the 200 most recent trades.")
    async def events(self, ctx):
        embed = disnake.Embed(
            title=f"Result of events.",
            description="Search users by their twitter handle.",
            color=0x9C84EF
        )
        embed.add_field(
            name="Response status:",
            value=f'CSV file sent!',
            inline=False 
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}"
        )
        try:
            endpoint = f'{str(self.friend_api)}/events'
            async with self.session.get(endpoint) as response:
                if response.status != 200:
                    print(f"Failed to connect to API, status code: {response.status}, message: {await response.text()}")
                    return

                json_data = await response.json()

                # Create a CSV string from the JSON data
                csv_data = io.StringIO()
                csv_writer = csv.writer(csv_data)
                csv_writer.writerow(["ID", "Blurred URL", "Is NSFW", "Caption", "Value", "Surplus", "Previous Owner",
                                    "Stealer", "Creator", "Previous Owner PFP URL", "Previous Owner Username",
                                    "Stealer PFP URL", "Stealer Username", "Creator PFP URL", "Creator Username"])

                for event in json_data.get("events", []):
                    csv_writer.writerow([
                        event.get("id", ""),
                        event.get("blurredUrl", ""),
                        event.get("isNSFW", ""),
                        event.get("caption", ""),
                        event.get("value", ""),
                        event.get("surplus", ""),
                        event.get("previousOwner", ""),
                        event.get("stealer", ""),
                        event.get("creator", ""),
                        event.get("previousOwnerPfpUrl", ""),
                        event.get("previousOwnerUsername", ""),
                        event.get("stealerPfpUrl", ""),
                        event.get("stealerUsername", ""),
                        event.get("creatorPfpUrl", ""),
                        event.get("creatorUsername", "")
                    ])

                # Reset the file-like object for reading
                csv_data.seek(0)

                # Send the CSV file as a direct message (DM)
                file = disnake.File(csv_data, filename="events.csv") # type: ignore
                await ctx.author.send(file=file, content="Here is the CSV file with the recent events.")
                await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error in events: {e}")
        
    @is_donator()
    @commands.slash_command(
        name="lists", 
        description="Gets a list of users by their token price or trending.",
        options=[
            Option(
                name="filters",
                description="Choose Token Price or Trending list.",
                type=OptionType.string,
                choices=["price", "trending"],
                required=True
            )
        ])
    async def lists(self, ctx, filters): 
        if filters is None:
            return
        
        t = ''
        if filters.lower() == 'price':
            t = 'top-by-price'
        if filters.lower() == 'trending':
            t = 'trending'

        try:
            endpoint = f'{str(self.friend_api)}/lists/{str(t)}'  
            async with self.session.get(endpoint) as response:
                if response.status != 200:
                    print(f"Failed to connect to API, status code: {response.status}, message: {await response.text()}")
                    return None

                json_data = await response.json()

                # Check the endpoint type (price or trending) and call the respective function
                if t == 'top-by-price':
                    await self.send_csv_as_dm(ctx, json_data, "top-by-price.csv")
                elif t == 'trending':
                    await self.send_csv_as_dm(ctx, json_data, "trending.csv")
                else:
                    await ctx.send("Invalid endpoint type.")

        except Exception as e:
            print(f"Error in lists: {e}")
            return None
    
    @staticmethod
    async def send_csv_as_dm(ctx, json_data, filename):
        embed = disnake.Embed(
            title=f"Result of lists.",
            description="Gets a list of users by their token price or trending.",
            color=0x9C84EF
        )
        embed.add_field(
            name="Response status:",
            value=f'CSV file sent!',
            inline=False 
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}"
        )
        try:
            # Create a CSV string from the JSON data
            csv_data = io.StringIO()
            csv_writer = csv.writer(csv_data)
            
            # Write the header row
            header = list(json_data["users"][0].keys())
            csv_writer.writerow(header)
            
            for user in json_data.get("users", []):
                csv_writer.writerow([user.get(key, "") for key in header])

            # Reset the file-like object for reading
            csv_data.seek(0)

            # Send the CSV file as a direct message (DM)
            file = disnake.File(csv_data, filename=filename)
            await ctx.author.send(file=file, content=f"Here is the CSV file for {filename}.")
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error in sending CSV as DM: {e}")
    
    # @is_donator()
    # @commands.slash_command(name="portfolio", description="Gets a history of friends-related activity for a user.")
    # async def portfolio(self, ctx, user_wallet):
    #     if user_wallet is None:
    #         await ctx.send("Please provide a valid user_wallet!.")
    #         return

    #     try:
    #         endpoint = f'{str(self.friend_api)}/portfolio/{str(user_wallet)}' 
    #         headers = {
    #             'Authorization': str(jwt),
    #             'Content-Type': 'application/json',
    #             'Accept': 'application/json',
    #             'Referer': 'https://www.friend.tech/'
    #         }
    #         async with self.session.get(endpoint, headers=headers) as response:
    #             if response.status != 200:
    #                 print(f"Failed to connect to API, status code: {response.status}, message: {await response.text()}")
    #                 return None
    #             json_data = await response.json()
    #             await ctx.send(json_data)  
    #     except Exception as e:
    #         print(f"Error in get_user by ID: {e}")
    #         return None
        
    # @is_donator()
    # @commands.slash_command(name="points", description="Gets the points for a user (potentially used for an airdrop).")
    # async def points(self, ctx, user_wallet):
    #     if user_wallet is None:
    #         await ctx.send("Please provide a valid user_wallet!.")
    #         return

    #     try:
    #         endpoint = f'{str(self.friend_api)}/portfolio/{str(user_wallet)}'  
    #         async with self.session.get(endpoint) as response:
    #             if response.status != 200:
    #                 print(f"Failed to connect to API, status code: {response.status}, message: {await response.text()}")
    #                 return None
    #             json_data = await response.json()
    #             await ctx.send(json_data)  
    #     except Exception as e:
    #         print(f"Error in get_user by ID: {e}")
    #         return None
    
def setup(bot):
    bot.add_cog(Friend(bot))