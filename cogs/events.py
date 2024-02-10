import json
import disnake
from disnake import Member
from disnake.ext import commands
from db import set_price_alert_channel, set_transaction_channel, set_wallet_address
from db import get_price_alert_channel, get_transaction_channel, get_wallet_address

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     # Loop through each guild the bot is in
    #     # for guild in self.bot.guilds:
    #     #     # Initialize the server's configuration in the database if not already done
    #     #     await self.check_and_send_default_settings_alert(guild)

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
                # Set the default value to NULL
                if setting == 'default_wallet_address':
                    set_wallet_address(guild.id, None)
                elif setting == 'default_transaction_channel':
                    set_transaction_channel(guild.id, None)
                elif setting == 'default_price_alert_channel':
                    set_price_alert_channel(guild.id, None)

                # Send a message to the guild owner
                owner = guild.owner
                if owner is not None:
                    embed = disnake.Embed(
                        title=f"Hey {owner}!",
                        description="You have just installed the BlockScan on your server. Make sure to set it up.",
                        color=0x9C84EF
                    )
                    embed.set_author(name="BlockScan", url="https://polygonscan-scrapper.ovoono.studio/", icon_url="https://i.imgur.com/bDrIHdo.png")
                    embed.add_field(
                        name="Set transaction channel",
                        value='/set_transaction_channel <channel_id>',
                        inline=False
                    )
                    embed.add_field(
                        name="Set price alert channel",
                        value='/set_price_alert_channel <channel_id>',
                        inline=False
                    )
                    embed.add_field(
                        name="Set wallet address",
                        value='/set_wallet_address <address>',
                        inline=False
                    )
                    embed.add_field(
                        name="Set moni token",
                        value='/set_moni_token <token_string>',
                        inline=False
                    )
                    embed.set_footer(
                        text="Powered by OvoOno Studio"
                    )
                    try:
                        await owner.send(embed=embed)
                    except Exception as e:
                        print(f"Failed to send message to guild owner {owner.name}: {e}")

def setup(bot):
    bot.add_cog(Events(bot))