import aiohttp
import asyncio 
import csv
import io
import disnake
import urllib.parse
from config import get_price_alert_channel, get_wallet_address
from disnake.ext import commands 
from disnake import Option, OptionType 
from config import jwt, twitter_bearer
from datetime import datetime, timedelta
from checks import is_donator
from web3 import Web3

class Friend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  
        self.new_influencers = []
        self.last_alerted_tx = {}
        self.last_processed_block = None
        self.session = aiohttp.ClientSession()
        self.friend_api = 'https://prod-api.kosetto.com'
        self.basescan_api = 'https://api.basescan.org/api'
        self.w3 = Web3(Web3.HTTPProvider('https://base-mainnet.g.alchemy.com/v2/8XQtglDUSx3Sp7MuWwhk3K1X9x2vrhJo'))
        self.wallet_address = '0xCF205808Ed36593aa40a44F10c7f7C2F67d4A4d4'  
    
    def start_tasks(self):
        self.bot.loop.create_task(self.check_transactions())
        self.bot.loop.create_task(self.verify_x_users())
        # self.bot.loop.create_task(self.keys_alerts())

    async def check_transactions(self):
        await self.bot.wait_until_ready()
        print('check_transactions triggered.')
        if len(self.new_influencers) == 22:
            print('No need to check data. Sleeping...')
            await asyncio.sleep(30)
            return
        while not self.bot.is_closed():
            try:
                latest_block = self.w3.eth.block_number
                block = self.w3.eth.get_block(latest_block, full_transactions=True)

                for tx in block['transactions']:
                    tx_to = tx['to']
                    tx_value = int(tx['value'])
                    tx_from = tx['from']
                    # Check the destination address and value of the transaction
                    if (
                        tx_to is not None
                        and tx_to.lower() == self.wallet_address.lower()
                        and tx_value == 0
                    ):
                        await self.fetch_user_by_wallet(tx_from)

                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error checking transactions: {e}")

    async def fetch_user_by_wallet(self, wallet):
        endpoint = f'/users/{wallet}'
        url = self.friend_api + endpoint
        headers = {
                'Authorization': str(jwt),
                'Content-Type': 'application/json',
                'Accept': 'application json',
                'Referer': 'https://www.friend.tech/'
            }

        async with self.session.get(url, headers=headers) as response:
            status_code = response.status
            response_text = await response.text()

            if status_code != 200:
                #print(f"Failed to connect to FT API, status code: {status_code}, message: {response_text}")
                if status_code == 404 and "Address/User not found." in response_text:
                    await asyncio.sleep(.5)
                    return
                return None

            json_data = await response.json()
            await self.store_user_from_response(json_data)

    async def store_user_from_response(self, response):
        # print(len(self.new_influencers))
        if len(self.new_influencers) == 22:
            print('Data full!') 
            await asyncio.sleep(30) 
            return
        
        user_data = {
            "address": response.get("address"),
            "twitterUsername": response.get("twitterUsername"),
            "twitterName": response.get("twitterName"),
            "holderCount": response.get("holderCount"),
            "holdingCount": response.get("holdingCount"),
            "verified": False
        }

        if response.get("holderCount") > 10:
            # print('Not new account..')
            return 

        # Check if the user is already in the list
        if any(user["address"] == user_data["address"] for user in self.new_influencers):
            return

        # Add the user to the list
        self.new_influencers.append(user_data) 

    async def verify_x_users(self): 
        await self.bot.wait_until_ready()
        print('verify_x_users triggered.')
        while not self.bot.is_closed(): 
            if len(self.new_influencers) < 21:
                #print('Not enough not data!')
                #print('Sleeping for 360 seconds')
                await asyncio.sleep(60)
                continue
            
            x_handler = self.new_influencers
            for user in x_handler:
                handler = user["twitterUsername"]
                if user['verified'] == True:
                    print('User already checked!')
                    continue
                verified_user = await self.verify_user_by_twitter_handle(handler)
                if verified_user:
                    print(f"User {handler} is fetched!")
                    user["verified"] = True
                else:
                    print(f"User {handler} does not exist.")
                await asyncio.sleep(.8)
            self.new_influencers = []
            await asyncio.sleep(60)  # Sleep for 60 seconds before the next verification run

    async def verify_user_by_twitter_handle(self, handle):  
        endpoint = f"users/lookup.json?screen_name={urllib.parse.quote(handle)}" 
        url = f"https://api.twitter.com/1.1/{endpoint}" 
        headers = {
            'Authorization': f'Bearer {twitter_bearer}',
            'User-Agent': 'PScanner/1.0.1',
            'Content-Type': 'application/json',
        } 
        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f"Failed to connect to Twitter API, status code: {response.status}, response: {await response.text()}")
                return None

            json_data = await response.json()
            user_data = json_data[0] if json_data else None

            if user_data:
                # Check if user has 0 followers
                if user_data['followers_count'] == 0:
                    print('User has not any followers! Skipping...')
                    return

                # Check if user follows more than 60% of the number of their followers
                # if user_data['friends_count'] > 0.8 * user_data['followers_count']:
                #     print('User has not positive followers ratio! Skipping...')
                #     return

                # Check if the user's account is younger than 3 months
                account_creation_date = datetime.strptime(user_data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                three_months_ago = datetime.utcnow() - timedelta(days=90)
                if account_creation_date > three_months_ago:
                    print('Account too young!')
                    return

                # If none of the checks are true, print the user
                await self.send_embedded_message(user_data)

            return user_data

    async def send_embedded_message(self, user_data):
        # Create an embedded message with transaction details
        embed = disnake.Embed(
            title="New 𝕏 Influencer spotted! 🚨",
            color=0x9C84EF,
            description=f"{user_data['description']}"
        )
        friend_url = f'https://friend.tech/{user_data["screen_name"]}'
        embed.set_author(name="PS Scanner", url="https://polygonscan-scrapper.ovoono.studio/", icon_url="https://i.imgur.com/97feYXR.png") 
        embed.set_thumbnail(url=f"{user_data['profile_image_url']}")
        embed.add_field(name="𝕏 Handler:", value=f"[{user_data['screen_name']}]({friend_url})", inline=True)
        embed.add_field(name="𝕏 Name:", value=f"{user_data['name']}", inline=True)
        embed.add_field(name="Followers:", value=f"{user_data['followers_count']}", inline=True) 
        embed.set_footer(text=f"Powered by OvoOno Studio")
        # if user_data.get('profile_banner_url'):
        #     embed.set_image(url=f"{user_data['profile_banner_url']}")
        # print('Banner is:')
        # print(banner_url)
        # if banner_url:
        #     embed.set_image(url=f"{banner_url}")

        for guild in self.bot.guilds:
            channel_id = get_price_alert_channel(guild.id)
            channel = self.bot.get_channel(channel_id)
            
            if channel is not None:
                try:
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"Error sending message: {e}")
                    
    def confirmations(self, tx_hash):
        tx = self.w3.eth.get_transaction(tx_hash)
        return self.w3.eth.block_number - tx.blockNumber
    
    async def get_user_pfpurl(self, address):
        endpoint = f'/users/{address}'
        url = self.friend_api + endpoint
        headers = {
                'Authorization': str(jwt),
                'Content-Type': 'application/json',
                'Accept': 'application json',
                'Referer': 'https://www.friend.tech/'
            }

        async with self.session.get(url, headers=headers) as response:
            status_code = response.status
            response_text = await response.text()

            if status_code != 200:
                #print(f"Failed to connect to FT API, status code: {status_code}, message: {response_text}")
                if status_code == 404 and "Address/User not found." in response_text:
                    await asyncio.sleep(.5)
                    return
                return None

            json_data = await response.json()
            return json_data['twitterPfpUrl']

    async def keys_alerts(self):  
        await self.bot.wait_until_ready()
        print('keys_alerts triggered.')
        processed_txs = set()

        while not self.bot.is_closed():
            try:
                # latest_block = self.w3.eth.block_number
                # block = self.w3.eth.get_block(latest_block, full_transactions=True)
                if self.last_processed_block is None:
                    self.last_processed_block = self.w3.eth.block_number

                block = self.w3.eth.get_block(self.last_processed_block + 1, full_transactions=True)
                # print(f"Searching in block {block.number} with {len(block.transactions)} transactions")

                if block and block.transactions:
                    for transaction in block.transactions:
                        tx_hash = transaction['hash'].hex()

                        # Check if this transaction has already been processed
                        if tx_hash in processed_txs:
                            print(f"Transaction {tx_hash} already processed. Skipping.")
                            continue

                        tx = self.w3.eth.get_transaction(tx_hash)

                        for guild in self.bot.guilds:
                            guild_id = guild.id
                            wallet_address = get_wallet_address(guild_id)
                            if wallet_address == 'default_wallet_address':
                                continue

                            wallet_address = self.w3.to_checksum_address(wallet_address)
                            if tx.to and wallet_address and tx.to.lower() == wallet_address.lower() or tx['from'] and wallet_address and tx['from'].lower() == wallet_address.lower():
                                if tx.to.lower() == wallet_address.lower():
                                    # This is an incoming transaction
                                    description = f"Incoming transaction for: {self.w3.from_wei(tx['value'], 'ether')} ETH"
                                else:
                                    # This is an outgoing transaction
                                    description = f"Outgoing transaction of: {self.w3.from_wei(tx['value'], 'ether')} ETH"
                                print(f"Transaction found in block {block.number} for guild {guild_id} with {self.confirmations(tx_hash)} confirmations.")
                                channel_id = get_price_alert_channel(guild_id) 

                                if channel_id == 'default_price_alert_channel':
                                    continue

                                channel = self.bot.get_channel(channel_id) 
                                twitter_profile_url = await self.get_user_pfpurl(wallet_address)
                                if self.last_alerted_tx.get(guild_id) != tx_hash:
                                    self.last_alerted_tx[guild_id] = tx_hash

                                    tx_from = tx["from"]
                                    tx_to = tx["to"]
                                    transaction_url = f"https://basescan.org/tx/{tx_hash}" 
                                    address_url = f"https://basescan.org/address/"
                                    embed = disnake.Embed(
                                        title="Keys trade alert! 🚨",
                                        description=f"{description}",
                                        color=0x9C84EF)
                                    embed.set_thumbnail(url=f"{twitter_profile_url}")
                                    embed.set_author(name="PS Scanner", url="https://polygonscan-scrapper.ovoono.studio/", icon_url="https://i.imgur.com/97feYXR.png")
                                    embed.add_field(name="🧑 From Address:", value=f'[{tx_from}]({address_url}{tx_from})', inline=False)
                                    embed.add_field(name="👉 To Address:", value=f'[{tx_to}]({address_url}{tx_to})', inline=False)
                                    embed.add_field(name="🔗 Transaction Hash:", value=f"[{tx_hash}]({transaction_url})", inline=False)
                                    embed.set_footer(text="Powered by OvoOno Studio")

                                    if channel: 
                                        processed_txs.add(tx_hash)
                                        await channel.send(embed=embed)
                                    else:
                                        print(f"Invalid channel for guild_id: {guild_id}")
                        await asyncio.sleep(1.7)

                self.last_processed_block = block.number
            except Exception as e:
                print(f"Error while fetching new blocks: {e}")

            # Sleep for a duration based on Ethereum's average block time (around 15 seconds)
            await asyncio.sleep(7)
        
    @is_donator()
    @commands.slash_command(name="user", description="Get details about a user by address.")
    async def user_by_address(self, ctx, user_wallet):
        await ctx.response.defer()
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
                embed = disnake.Embed(title="User Details", color=0x9C84EF) 
                embed.set_author(name="PS Scanner", url="https://polygonscan-scrapper.ovoono.studio/", icon_url="https://i.imgur.com/97feYXR.png")
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
        thinking_embed = disnake.Embed(title='PScanner is thinking..', color=0x9C84EF)
        await ctx.edit_original_message(embed=thinking_embed)
        
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
        embed.set_author(name="PS Scanner", url="https://polygonscan-scrapper.ovoono.studio/", icon_url="https://i.imgur.com/97feYXR.png")
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
        await ctx.response.defer()
        
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
            embed.set_author(name="PS Scanner", url="https://polygonscan-scrapper.ovoono.studio/", icon_url="https://i.imgur.com/97feYXR.png")
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
                await ctx.author.followup.send(file=file, content=f"Search results for: {username}.")
                await ctx.followup.send(embed=embed)

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
        embed.set_author(name="PS Scanner", url="https://polygonscan-scrapper.ovoono.studio/", icon_url="https://i.imgur.com/97feYXR.png")
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
        await ctx.response.defer()
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
        
        # Once done, edit the deferred response
        await ctx.edit_original_message(embed='PScanner is thinking..')
    
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