from disnake.ext import commands
from config import set_price_alert_channel, set_transaction_channel, set_wallet_address

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Initialize the server's configuration in the database
        print('testing...')
        set_wallet_address(guild.id, 'default_wallet_address')
        set_transaction_channel(guild.id, 'default_transaction_channel')
        set_price_alert_channel(guild.id, 'default_price_alert_channel')

def setup(bot):
    bot.add_cog(Events(bot))