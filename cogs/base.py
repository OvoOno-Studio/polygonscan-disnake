from disnake.ext import commands

class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
  
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

def setup(bot):
    bot.add_cog(BaseCog(bot))