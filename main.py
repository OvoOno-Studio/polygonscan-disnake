"""
Copyright © DevEmel 2022 - https://github.com/ml350 
Description:
Discord Bot based on PolygonScan API, CoingGecko API and Disnake lib for web scrapping data from PolygonScan. 
Powered by PolygonScan APIs.
Version: 1.0
"""   
import disnake
from disnake.ext import commands 
from config import DiscordToken
import os, traceback

class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Welcome to the PolygonScan Tracker Bot!")
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})\n--------------------------------------------------------------------")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("**Invalid command. Try using** `help` **to figure out commands!**")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('**Please pass in all requirements.**')
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("**You dont have all the requirements or permissions for using this command :angry:**")

    @commands.command()
    async def ping(self, ctx):
        await ctx.send (f"📶 {round(self.bot.latency * 1000)}ms")

    @commands.command()
    async def donate(self, ctx):
        await ctx.send (f"To access all features from PolygonScan Scrapper Bot and OvoOno Studio in globally, you can donate with one-time PayPal payment on next link: https://upgrade.chat/ovoono-studio/p/ovodonator ")

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("ps-"), intents=disnake.Intents.all())

        self.add_cog(BaseCog(self))

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