import aiohttp
import asyncio
import disnake
from disnake.ext import commands
from config import get_transaction_channel

class Signal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.api_url = "https://ovoonoapi.azurewebsites.net/crypto/matic"
        self.bot.loop.create_task(self.send_signal())

    async def fetch_signal_data(self):
        try:
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
        for guild in self.bot.guilds:
            self.transaction_channel_id = get_transaction_channel(guild.id)
            try:
                channel = await self.bot.fetch_channel(self.transaction_channel_id)
                if channel:
                    print(f"Sending signal message to channel {channel.id}")  # Debugging print statement
                    message = (
                        f"📡 **New Signal Data** 📡\n"
                        f"MACD: {signal_data['macd']}\n"
                        f"RSI: {signal_data['rsi']}\n"
                        f"Bollinger Bands: {signal_data['bollingerBands']}\n"
                    )
                    try:
                        await channel.send(message)
                        print(f"Signal message sent to: {channel}") # Debugging print statement
                    except disnake.HTTPException as e:
                        print(f"Error sending signal message to channel with ID {self.transaction_channel_id}: {e}")
                else:
                    print('No channel optimized!')
            except disnake.NotFound:
                print(f"Channel with ID {self.transaction_channel_id} not found.")
            except disnake.Forbidden:
                print(f"Bot does not have permission to access channel with ID {self.transaction_channel_id}.")
            except disnake.HTTPException as e:
                print(f"Error fetching channel with ID {self.transaction_channel_id}: {e}")

    async def send_signal(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                signal_data = await self.fetch_signal_data()
                if signal_data is not None:
                    await self.send_signal_message(signal_data)
                else:
                    print("No signal data to send.")
                    
                await asyncio.sleep(60)  # 4 hours
                
            except Exception as e:
                print(f"Error in send_signal: {e}")
                await asyncio.sleep(60)  # In case of an error, wait 1 minute before retrying

def setup(bot):
    bot.add_cog(Signal(bot))