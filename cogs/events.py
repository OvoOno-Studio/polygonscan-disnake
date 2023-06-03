import asyncio
from disnake.ext import commands
from config import set_price_alert_channel, set_transaction_channel, set_wallet_address
from config import get_price_alert_channel, get_transaction_channel, get_wallet_address

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_settings_loop())

    async def check_settings_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild in self.bot.guilds:
                await self.check_and_send_default_settings_alert(guild)
            await asyncio.sleep(12 * 60 * 60)  # 12 hours
    
    @commands.Cog.listener()
    async def on_ready(self):  
        # Loop through each guild the bot is in
        for guild in self.bot.guilds:
            # Initialize the server's configuration in the database if not already done
            await self.check_and_send_default_settings_alert(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Initialize the server's configuration in the database
        await self.check_and_send_default_settings_alert(guild)

    async def check_and_send_default_settings_alert(self, guild):
        default_settings = {
            'default_wallet_address': get_wallet_address(guild.id),
            'default_transaction_channel': get_transaction_channel(guild.id),
            'default_price_alert_channel': get_price_alert_channel(guild.id),
        }

        # Check if any setting is still at its default value
        for setting, value in default_settings.items():
            if value is None:
                # Set the default value
                if setting == 'default_wallet_address':
                    set_wallet_address(guild.id, 'default_wallet_address')
                elif setting == 'default_transaction_channel':
                    set_transaction_channel(guild.id, 'default_transaction_channel')
                elif setting == 'default_price_alert_channel':
                    set_price_alert_channel(guild.id, 'default_price_alert_channel')

                # Send a message to the guild owner
                owner = guild.owner
                if owner is not None:
                    try:
                        await owner.send(
                            f"Hello {owner.name},\n"
                            f"It seems like your guild {guild.name} is using the default {setting.replace('default_', '')}. "
                            f"Please change it to your preferred setting. "
                        )
                    except Exception as e:
                        print(f"Failed to send message to guild owner {owner.name}: {e}") 

def setup(bot):
    bot.add_cog(Events(bot))
