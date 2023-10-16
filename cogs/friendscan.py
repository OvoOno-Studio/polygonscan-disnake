import aiohttp
import csv
import io
import disnake
import requests
from disnake.ext import commands 
from disnake import Option, OptionType, Embed, Color
from config import jwt
from checks import is_donator

class Friend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.friend_api = 'https://prod-api.kosetto.com'
        
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

                # Add fields to the embed for user details
                embed.add_field(name="User Address", value=json_data.get("address", ""), inline=False)
                embed.add_field(name="Twitter Username", value=json_data.get("twitterUsername", ""), inline=True)
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