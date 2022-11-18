"""
Copyright © DevEmel 2022 - https://github.com/ml350 
Description:
Discord Bot based on PolygonScan API and Disnake lib for web scrapping data from PolygonScan. 
Version: 1.0
"""   
import disnake
from disnake.ext import commands 
from config import DiscordToken
import os, traceback

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("ps-"), intents=intents)

# Ping command that returns bot latency
@bot.command()
async def ping(ctx):
    await ctx.send (f"📶 {round(bot.latency * 1000)}ms") 

# Print the message in Python console once bot is ready for usage
@bot.event
async def on_ready():
    print("Welcome to the PolygonScan Tracker Bot!")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})\n--------------------------------------------------------------------")

# Display error on command
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("**Invalid command. Try using** `help` **to figure out commands!**")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Please pass in all requirements.**')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("**You dont have all the requirements or permissions for using this command :angry:**")

for file in os.listdir('./cogs'):
    if file.endswith('.py') and file != '__init__.py':
        try:
            bot.load_extension("cogs."+file[:-3])
            print(f"{file[:-3]} Loaded successfully.")
        except:
            print(f"Unable to load {file[:-3]}.")
            print(traceback.format_exc())

if __name__ == "__main__":
    bot.run(str(DiscordToken))