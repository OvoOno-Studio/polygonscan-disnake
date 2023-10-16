import aiohttp
import asyncio
import disnake
import requests
from disnake.ext import commands 
from config import jwt
from checks import is_donator

class Friend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.friend_api = 'https://prod-api.kosetto.com'
        
    @is_donator()
    @commands.slash_command(name="user", description="Get details about user by address.")
    async def user_by_address(self, ctx, user_wallet: str = None):
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
        
def setup(bot):
    bot.add_cog(Friend(bot))