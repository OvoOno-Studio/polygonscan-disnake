"""
<<<<<<< HEAD
Copyright © OvoOno Studio 2022 - https://github.com/ml350 
Description:
Discord Bot based on PolygonScan API, CoinGecko API and Disnake lib for web scrapping data from PolygonScan. 
Powered by PolygonScan APIs.
=======
Copyright © OvoOno Studio 2022 - https://github.com/OvoOno-Studio/polygonscan-disnake
Description:
Discord Bot based on PolygonScan, CoingGecko, Binance APIs and Disnake lib for web scrapping data from PolygonScan. 
>>>>>>> c98f2209f9dd7a6527d6718c33e0fd9ac4625a41
Version: 1.0
"""   
import disnake
from disnake.ext import commands 
from config import DiscordToken
import os, traceback

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("ps-"), intents=disnake.Intents.all())

        for file in os.listdir('./cogs'):
            if file.endswith('.py') and file != '__init__.py':
                try:
                    self.load_extension(f"cogs.{file[:-3]}")
                    print(f"{file[:-3]} Loaded successfully.")
                except:
                    print(f"Unable to load {file[:-3]}.")
                    print(traceback.format_exc())

def main():
    bot = Bot()
    bot.run(DiscordToken)

if __name__ == "__main__":
    main()