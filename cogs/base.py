from disnake.ext import commands 
# from checks import update_donators_periodically

class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Welcome to the PolygonScan Tracker Bot!")
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})\n--------------------------------------------------------------------")
        # self.bot.loop.create_task(update_donators_periodically())

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
        await ctx.send (f"To access all features from PolygonScan Scrapper Bot and OvoOno Studio in globally, you can donate with one-time PayPal payment on next link: https://www.buymeacoffee.com/bezmir")

def setup(bot):
    bot.add_cog(BaseCog(bot))