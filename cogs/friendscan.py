import aiohttp
import asyncio
import disnake
import requests
from disnake.ext import commands 
from config import APIKey, API2Key
from checks import is_donator

class Friend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.friend_api = 'https://prod-api.kosetto.com'
        
    @is_donator()
    @commands.slash_command(name="user", description="Get details about user by address.")
    async def user_by_address(self, ctx, user_wallet: str = None):
        if user_wallet is None:
            await ctx.send("Please provide a valid user_wallet!.")
            return
        
        endpoint = f'{str(self.friend_api)}/users/{str(user_wallet)}'
        response = requests.get(endpoint)
        await ctx.send(response)
        
def setup(bot):
    bot.add_cog(Friend(bot))