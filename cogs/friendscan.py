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
    @commands.slash_command(name="user", description="Get details about user by address.")
    async def user_by_address(self, ctx, user_wallet):
        if user_wallet is None:
            await ctx.send("Please provide a valid user_wallet!.")
            return
        
        try:
            endpoint = f'{str(self.friend_api)}/users/{str(user_wallet)}' 
            headers = {
                'Authorization': str(jwt),
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Referer': 'https://www.friend.tech/'
            }
            async with self.session.get(endpoint, headers=headers) as response:
                if response.status != 200:
                    print(f"Failed to connect to API, status code: {response.status}, message: {await response.text()}")
                    return None
                json_data = await response.json()
                await ctx.send(json_data)  
        except Exception as e:
            print(f"Error in get_user by ID: {e}")
            return None
        
    @is_donator()
    @commands.slash_command(name="holdings_activity", description="Gets a history of trades for a user.")
    async def holdings_activity(self, ctx, user_wallet):
        if user_wallet is None:
            await ctx.send("Please provide a valid user_wallet!.")
            return
        
        try:
            endpoint = f'{str(self.friend_api)}/holdings-activity/{str(user_wallet)}' 
            async with self.session.get(endpoint) as response:
                if response.status != 200:
                    print(f"Failed to connect to API, status code: {response.status}, message: {await response.text()}")
                    return None
                json_data = await response.json()
                await ctx.send(json_data)  
        except Exception as e:
            print(f"Error in get_user by ID: {e}")
            return None 
    
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
        try:
            endpoint = f'{str(self.friend_api)}/events' 
            async with self.session.get(endpoint) as response:
                if response.status != 200:
                    print(f"Failed to connect to API, status code: {response.status}, message: {await response.text()}")
                    return None
                json_data = await response.json()
                await ctx.send(json_data)  
        except Exception as e:
            print(f"Error in events: {e}")
            return None
        
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
                print(json_data)
                await ctx.send('Works')  
        except Exception as e:
            print(f"Error in get_user by ID: {e}")
            return None
    
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