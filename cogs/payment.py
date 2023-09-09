import disnake
import json
import requests
from disnake.ext import commands
from config import API2Key

class Payment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.payment_wallet = '0x48D0eEE30ec5BF5C7E167036a8c7f3e4820c19fa'
        self.api = 'https://api.etherscan.io/api'

    @commands.slash_command(name='upgrade_version')
    async def upgrade_version(self, ctx): 
        message = f"Please send exactly 0.088 ETH to the address {self.payment_wallet} and let me know once done by typing `/confirm_payment <your_wallet>`."
        await ctx.respond(content=message)

    @commands.slash_command(name='confirm_payment')
    async def confirm_payment(self, ctx, wallet_from: str):
        wallet = self.payment_wallet
        api = self.api
        amount = 0.088

        params = {
            "module": "account",
            "action": "txlist",
            "address": wallet,
            "startblock": 0,
            "endblock": 99999999, 
            "sort": "desc", 
            "apikey": API2Key
        }

        try:
            response = requests.get(api, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            await ctx.respond(content=f"Error fetching transaction details: {e}")
            return

        data = response.json()

        if not data.get("result"):
            await ctx.respond(content="I couldn't verify the payment at this time. Please try again later.")
            return

        for tx in data["result"]:
            if tx["to"] == wallet and tx["from"] == wallet_from.lower() and float(tx["value"]) == amount * 10**18:
                with open("donators.json", "r+") as file:
                    donators = json.load(file)

                    if not any(d['user_id'] == ctx.author.id for d in donators):
                        new_donator = {
                            "user_id": ctx.author.id,
                            "username": ctx.author.name
                        }
                        donators.append(new_donator)
                        file.seek(0)
                        json.dump(donators, file)

                await ctx.respond(content="Payment verified! You have been upgraded to the premium version.")
                return

        await ctx.respond(content=f"Payment not found from wallet {wallet_from}. Ensure you've sent the correct amount to the right address.")

def setup(bot):
    bot.add_cog(Payment(bot))