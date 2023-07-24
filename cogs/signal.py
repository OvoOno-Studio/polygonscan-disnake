import json
import aiohttp
import asyncio
import disnake
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from config import get_signal_pair, set_signal_pair
# import matplotlib.pyplot as plt
# import os

class Signal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.signal_pair = None
        self.api_url = f"https://ovoonoapi.azurewebsites.net/crypto/`{self.signal_pair}`"
        self.bot.loop.create_task(self.send_signal())

    @commands.command(name="set_signal_pair")
    @has_permissions(administrator=True)
    async def set_signal_pair(self, ctx, signal_pair: str):
        set_signal_pair(ctx.guild.id, signal_pair)
        await ctx.send(f"Signal pair has been set to `{signal_pair}`/USDT")

    async def fetch_signal_data(self):
        try:
            for guild in self.bot.guilds:
                self.signal_pair = get_signal_pair(guild.id)
                if self.signal_pair is None:
                    self.signal_pair = 'matic'
                    
                async with self.session.get(self.api_url) as response:
                    if response.status != 200:
                        print(f"Failed to fetch signal data, status code: {response.status}, message: {await response.text()}")
                        return None
                    json_data = await response.json()
                    return json_data["signal"]
        except Exception as e:
            print(f"Error in fetch_signal_data: {e}")
            return None 

    async def send_signal_message(self, signal_data):
        try:
            with open('donators.json', 'r') as f:
                donators = json.load(f)
        except FileNotFoundError:
            print("File 'donators.json' not found.")
            return
        except json.JSONDecodeError:
            print("Error decoding JSON from 'donators.json'.")
            return

        user_ids = [donator['user_id'] for donator in donators]
        signal_mapping = {0: ('🟡', 'HODL'), -1: ('🔴', 'SELL'), 1: ('🟢', 'BUY')}

        for user_id in user_ids:
            try:
                user = await self.bot.fetch_user(user_id)
                if user:
                    print(f"Sending signal message to user {user.id}")  # Debugging print statement
                    message = (
                        f".\n\n"
                        f"📡 **New Technical analysis Indicators: ** 📡\n\n"
                        f"**Pair:** {self.signal_pair}/usdt\n\n"
                        f"**MACD:** {signal_mapping[signal_data['macd']][1]} {signal_mapping[signal_data['macd']][0]}\n"
                        f"**RSI:** {signal_mapping[signal_data['rsi']][1]} {signal_mapping[signal_data['rsi']][0]}\n"
                        f"**BB:** {signal_mapping[signal_data['bollingerBands']][1]} {signal_mapping[signal_data['bollingerBands']][0]}\n"
                    )
                    try:
                        await user.send(message)
                        print(f"Signal message sent to: {user}")  # Debugging print statement
                    except disnake.HTTPException as e:
                        print(f"Error sending signal message to user with ID {user_id}: {e}")
                else:
                    print(f"User with ID {user_id} not found.")
            except disnake.NotFound:
                print(f"User with ID {user_id} not found.")
            except disnake.Forbidden:
                print(f"Bot does not have permission to send messages to user with ID {user_id}.")
            except disnake.HTTPException as e:
                print(f"Error fetching user with ID {user_id}: {e}")

    async def send_signal(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                signal_data = await self.fetch_signal_data()
                if signal_data is not None:
                    await self.send_signal_message(signal_data)
                else:
                    print("No signal data to send.")
                    
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                print(f"Error in send_signal: {e}")
                await asyncio.sleep(60)  # In case of an error, wait 1 minute before retrying

def setup(bot):
    bot.add_cog(Signal(bot))
