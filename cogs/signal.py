import json
import aiohttp
import asyncio
import disnake
from disnake.ext import commands 
import matplotlib.pyplot as plt
import os

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
                return json_data 
        except Exception as e:
            print(f"Error in fetch_signal_data: {e}")
            return None
        
    def generate_graph(self, data, title, filename):
        plt.figure(figsize=(14, 7))
        plt.plot(data, label=title)
        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.savefig(filename)
        plt.close()

    async def send_signal_message(self, signal_data, indicators_data):
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
        signal_mapping = {0: ('HODL', '🟡'), -1: ('SELL', '🔴'), 1: ('BUY', '🟢')}

        # Generate graphs for each indicator
        for indicator in ['macd', 'rsi', 'bollingerBands']:
            plt.figure(figsize=(14, 7))
            plt.plot(indicators_data[indicator], label=indicator)
            plt.title(f'{indicator} over time')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.legend()
            plt.grid(True)
            plt.savefig(f'{indicator}.png')
            plt.close()

        for user_id in user_ids:
            try:
                user = await self.bot.fetch_user(user_id)
                if user:
                    print(f"Sending signal message to user {user.id}")  # Debugging print statement
                    embed = disnake.Embed(
                        title="📡 New CryptoSignal Data for MATIC/USDT 📡",
                        description=(
                            f"**MACD:** {signal_mapping[signal_data['macd']][1]} {signal_mapping[signal_data['macd']][0]}\n"
                            f"**RSI:** {signal_mapping[signal_data['rsi']][1]} {signal_mapping[signal_data['rsi']][0]}\n"
                            f"**Bollinger Bands:** {signal_mapping[signal_data['bollingerBands']][1]} {signal_mapping[signal_data['bollingerBands']][0]}\n"
                        ),
                        color=disnake.Color.blue()
                    )
                    for indicator in ['macd', 'rsi', 'bollingerBands']:
                        file = disnake.File(f"{indicator}.png", filename=f"{indicator}.png")
                        embed.set_image(url=f"attachment://{indicator}.png")
                        await user.send(embed=embed, file=file)
                        print(f"Signal message sent to: {user}")  # Debugging print statement
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
                    
                await asyncio.sleep(14400)  # 4 hours
                
            except Exception as e:
                print(f"Error in send_signal: {e}")
                await asyncio.sleep(60)  # In case of an error, wait 1 minute before retrying

def setup(bot):
    bot.add_cog(Signal(bot))
