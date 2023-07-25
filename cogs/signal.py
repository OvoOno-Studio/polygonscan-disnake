import json
import aiohttp
import asyncio
import disnake
from disnake.ext import commands
from disnake.ext.commands import has_permissions 
from config import get_signal_pair, set_signal_pair
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
# import os

class Signal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.signal_pair = None
        self.api_url = "https://ovoonoapi.azurewebsites.net/crypto/"
        self.bot.loop.create_task(self.send_signal())

    @commands.command(name="set_signal_pair")
    @has_permissions(administrator=True)
    async def set_signal_pair(self, ctx, signal_pair: str):
        set_signal_pair(ctx.guild.id, signal_pair)
        await ctx.send(f"Signal pair has been set to `{signal_pair}`/usdt")

    async def fetch_signal_data(self, pair):
        try: 
            url = self.api_url + pair 
            async with self.session.get(url) as response:
                if response.status != 200:
                    print(f"Failed to fetch signal data, status code: {response.status}, message: {await response.text()}")
                    return None
                json_data = await response.json()
                return json_data["signal"]
        except Exception as e:
            print(f"Error in fetch_signal_data: {e}")
            return None
        
    async def generate_graph(self, signal_data):
        # Extract the data from the signal_data dictionary
        macd = signal_data['indicators']['macd']['macd']
        rsi = signal_data['indicators']['rsi']['rsi']
        bb_upper = signal_data['indicators']['bollingerBands']['upper']
        bb_middle = signal_data['indicators']['bollingerBands']['middle']
        bb_lower = signal_data['indicators']['bollingerBands']['lower']

        # Create a new figure
        fig, axs = plt.subplots(3, figsize=(10, 15))

        # Plot MACD
        axs[0].plot(np.arange(len(macd)), macd, label='MACD')
        axs[0].set_title('MACD')
        axs[0].legend()

        # Plot RSI
        axs[1].plot(np.arange(len(rsi)), rsi, label='RSI')
        axs[1].set_title('RSI')
        axs[1].legend()

        # Plot Bollinger Bands
        axs[2].plot(np.arange(len(bb_upper)), bb_upper, label='Upper Band')
        axs[2].plot(np.arange(len(bb_middle)), bb_middle, label='Middle Band')
        axs[2].plot(np.arange(len(bb_lower)), bb_lower, label='Lower Band')
        axs[2].set_title('Bollinger Bands')
        axs[2].legend()

        # Save the figure to a file
        fig.savefig('signal_graph.png')

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
        file = disnake.File('signal_graph.png', filename="signal_graph.png")
        for user_id in user_ids:
            try:
                user = await self.bot.fetch_user(user_id)
                if user:
                    print(f"Sending signal message to user {user.id}")  # Debugging print statement
                    # Create an Embed object for the message
                    embed = disnake.Embed(title="📡 New Technical analysis Indicators 📡", description=f"💵Pair: **{self.signal_pair}/usdt**", color=0x9C84EF, timestamp=datetime.now())
                    embed.set_image(url="attachment://signal_graph.png")  # Use the image in the attachment
                    embed.add_field(name="📊 MACD", value=f"{signal_mapping[signal_data['macd']][1]} {signal_mapping[signal_data['macd']][0]}")
                    embed.add_field(name="📊 RSI", value=f"{signal_mapping[signal_data['rsi']][1]} {signal_mapping[signal_data['rsi']][0]}")
                    embed.add_field(name="📜 BB", value=f"{signal_mapping[signal_data['bollingerBands']][1]} {signal_mapping[signal_data['bollingerBands']][0]}")
                    embed.set_footer(text=f"Powered by OvoOno Studio")
                    # 
                    try:
                        await user.send(embed=embed, file=file)
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
                self.signal_pair = get_signal_pair(944377384872853555)
                signal_data = await self.fetch_signal_data(self.signal_pair)
                if signal_data is not None:
                    await self.generate_graph(signal_data)
                    await self.send_signal_message(signal_data)
                else:
                    print("No signal data to send.")

                await asyncio.sleep(3600)  # 1 hour           
                
            except Exception as e:
                print(f"Error in send_signal: {e}")
                await asyncio.sleep(60)  # In case of an error, wait 1 minute before retrying

def setup(bot):
    bot.add_cog(Signal(bot))
