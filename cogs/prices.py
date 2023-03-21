import disnake
from disnake.ext import commands
import asyncio
import ccxt

class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.exchange = ccxt.binance()  # You can use any other supported exchange, e.g., ccxt.coinbasepro()

    async def get_crypto_price(self, symbol):
        ticker = self.exchange.fetch_ticker(symbol)
        return ticker['last']
    
    async def update_crypto_presence(self):
        while True:
            try:
                price = await self.get_crypto_price('matic/usdt')  # Fetch the price for Matic
                await self.bot.change_presence(
                    status=disnake.Status.online,
                    activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"MATIC: ${price:.2f}")
                )
            except Exception as e:
                print(f"Error updating presence: {e}")

            await asyncio.sleep(60)  # Update the presence every 60 seconds

    @commands.command()
    async def crypto(self, ctx, symbol: str = 'btc'):
        symbol = symbol.lower()
        if symbol in ['btc', 'eth', 'matic', 'sand']:
            try:
                price = await self.get_crypto_price(f'{symbol}/usdt')  # Fetch the price against USDT
                await ctx.send(f"Current {symbol.upper()} price: ${price:.2f}")
            except Exception as e:
                await ctx.send(f"Error fetching the price for {symbol.upper()}: {e}")
        else:
            await ctx.send("Invalid symbol. Please use 'btc', 'eth', 'matic', or 'sand'.")

def setup(bot):
    bot.add_cog(Crypto(bot))