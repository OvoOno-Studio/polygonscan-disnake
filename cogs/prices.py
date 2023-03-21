import disnake
from disnake.ext import commands
import aiohttp
import asyncio

class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.api_url = "https://api.binance.com/api/v3/ticker/price?symbol="

        self.bot.loop.create_task(self.update_crypto_presence())

    async def get_crypto_price(self, symbol: str):
        async with self.session.get(self.api_url + symbol.upper()) as response:
            json_data = await response.json()
            price = float(json_data['price'])
            return price

    async def update_crypto_presence(self):
        while True:
            try:
                price = await self.get_crypto_price('MATICUSDT')  # Fetch the price for MATIC
                await self.bot.change_presence(
                    status=disnake.Status.online,
                    activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"MATIC: ${price:.2f}")
                )
            except Exception as e:
                print(f"Error updating presence: {e}")

            await asyncio.sleep(60)  # Update the presence every 60 seconds

def setup(bot):
    bot.add_cog(Crypto(bot))