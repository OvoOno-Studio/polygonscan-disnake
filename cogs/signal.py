import json
import aiohttp
import asyncio
import disnake
import seaborn as sns
from disnake.ext import commands
from disnake.ext.commands import has_permissions 
from config import get_signal_pair, set_signal_pair
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO 
# import os

class Signal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.signal_pair = None
        self.api_url = "https://ovoono-express-eofcu.ondigitalocean.app/crypto/"
        # self.bot.loop.create_task(self.send_signal())

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
                return json_data
        except Exception as e:
            print(f"Error in fetch_signal_data: {e}")
            return None
        
    async def generate_graph(self, signal_data):
        # Extract the data from the signal_data dictionary
        ema = signal_data['indicators']['ema']
        volume = signal_data['indicators']['volumes']
        macd = signal_data['indicators']['macd']['macd']
        signal = signal_data['indicators']['macd']['signal']
        rsi = signal_data['indicators']['rsi']['rsi']
        so = signal_data['indicators']['stochastic_scillator']

        # Create a new figure with 4 subplots, arranged vertically
        fig, axs = plt.subplots(4, figsize=(8,8))

        # Adjust the spacing between the subplots
        fig.subplots_adjust(hspace=0.5)

        # Set the Seaborn theme
        sns.set_theme()

        # Plot EMA
        sns.lineplot(ax=axs[0], x=np.arange(len(ema)), y=ema, label='EMA')
        axs[0].set_title('Exponential Moving Average (EMA)')
        axs[0].legend()
        axs[0].grid(True)  # Add grid

        # Plot Volume
        sns.lineplot(ax=axs[1], x=np.arange(len(volume)), y=volume, label='Volume')
        axs[1].bar(np.arange(len(volume)), volume, alpha=0.3)  # Overlay a bar chart on the line chart
        axs[1].set_title('Volume')
        axs[1].legend()
        axs[1].grid(True)  # Add grid

        # Create a color array for the histogram
        hist_colors = ['g' if (y >= 0) else 'r' for y in np.array(macd)-np.array(signal)]
        
        # Plot MACD and Signal line
        sns.lineplot(ax=axs[2], x=np.arange(len(macd)), y=macd, label='MACD')
        sns.lineplot(ax=axs[2], x=np.arange(len(signal)), y=signal, label='Signal')
        axs[2].bar(np.arange(len(macd)), np.array(macd)-np.array(signal), alpha=0.3, color=hist_colors)  # Overlay a histogram (MACD - Signal)
        axs[2].set_title('Moving Average Convergence Divergence (MACD)')
        axs[2].legend()
        axs[2].grid(True)  # Add grid

        # Plot RSI
        sns.lineplot(ax=axs[3], x=np.arange(len(rsi)), y=rsi, label='RSI')
        axs[3].set_title('Relative Strength Index (RSI)')
        axs[3].legend()
        axs[3].grid(True)  # Add grid

        # Save the plot to a BytesIO object and return it
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return buf

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
        buf = await self.generate_graph(signal_data) 
        for user_id in user_ids:
            try:
                user = await self.bot.fetch_user(user_id)
                if user:
                    print(f"Sending signal message to user {user.id}")  # Debugging print statement
                    # Reset the pointer to the start of the BytesIO object
                    buf.seek(0)
                    file = disnake.File(fp=buf, filename="signal_graph.png")
                    # Create an Embed object for the message
                    embed = disnake.Embed(title="📡 New Technical analysis Indicators", description=f"🪙Pair: **{self.signal_pair}/usdt**\n 💵Price: **{signal_data['indicators']['currentPrice']}$** \n 🔢Volume 24h: **{signal_data['indicators']['volume24h']}**\n\n", color=0x9C84EF, timestamp=datetime.now())
                    embed.set_image(url="attachment://signal_graph.png") 
                    embed.add_field(name="📊 EMA", value=f"{signal_mapping[signal_data['signal']['ema']][1]} {signal_mapping[signal_data['signal']['ema']][0]}") 
                    embed.add_field(name="📊 MACD", value=f"{signal_mapping[signal_data['signal']['macd']][1]} {signal_mapping[signal_data['signal']['macd']][0]}")
                    embed.add_field(name="📊 RSI", value=f"{signal_mapping[signal_data['signal']['rsi']][1]} {signal_mapping[signal_data['signal']['rsi']][0]}")
                    embed.add_field(name="📊 SO/MA", value=f"{signal_mapping[signal_data['signal']['so_ma']][1]} {signal_mapping[signal_data['signal']['so_ma']][0]}")
                    embed.add_field(name="📜 BB", value=f"{signal_mapping[signal_data['signal']['bollingerBands']][1]} {signal_mapping[signal_data['signal']['bollingerBands']][0]}")            
                    embed.add_field(name="📶 Final Signal", value=f"{signal_mapping[signal_data['finalSignal']][1]} {signal_mapping[signal_data['finalSignal']][0]}")
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
                    await self.send_signal_message(signal_data)
                else:
                    print("No signal data to send.")

                await asyncio.sleep(3600)  # 1 hour           
                
            except Exception as e:
                print(f"Error in send_signal: {e}")
                await asyncio.sleep(60)  # In case of an error, wait 1 minute before retrying

def setup(bot):
    bot.add_cog(Signal(bot))
