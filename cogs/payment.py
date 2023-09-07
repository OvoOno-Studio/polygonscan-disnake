import disnake
import json
import requests
from disnake.ext import commands
from config import APIKey

class Payment(commands.Cog):
    def _init_(self, bot):
        self.bot = bot
        self.payment_wallet = '0x48D0eEE30ec5BF5C7E167036a8c7f3e4820c19fa'
        self.api = 'https://api.etherscan.io/api'

    @commands.command(name='upgrade_version')
    async def upgrade(self, ctx):
        amount = 0.088
        message = f"Please send exactly {amount} ETH to the address {self.payment_wallet} and let me know once done by typing `!confirm`."
        await ctx.send(message)

    @commands.command(name='confirm')
    async def confirm(self, ctx, wallet_from: str):
        wallet = self.payment_wallet
        api = self.api
        amount = 0.088

        # Fetch the latest transactions for the address from Etherscan
        params = {
            "module": "account",
            "action": "txlist",
            "address": wallet,
            "startblock": 0,
            "endblock": 99999999, 
            "sort": "desc", 
            "apikey": APIKey
        }

        response = requests.get(api, params=params)
        data = response.json()

        if not data.get("result"):
            await ctx.send("I couldn't verify the payment at this time. Please try again later.")
            return

        for tx in data["result"]:
            # Verify transaction: from the user's specified address, correct amount, and to your address
            if tx["to"] == wallet and tx["from"] == wallet_from.lower() and float(tx["value"]) == amount * 10**18:  # Ethereum has 18 decimal places
                # Add user to donators.json
                with open("donators.json", "r+") as file:
                    donators = json.load(file)
                    
                    # Check if user is already in the donators list
                    if not any(d['user_id'] == ctx.author.id for d in donators):
                        new_donator = {
                            "user_id": ctx.author.id,
                            "username": ctx.author.name
                        }
                        donators.append(new_donator)
                        file.seek(0)
                        json.dump(donators, file)

                await ctx.send("Payment verified! You have been upgraded to the premium version.")
                return
        await ctx.send(f"Payment not found from wallet {wallet_from}. Ensure you've sent the correct amount to the right address.")  

def setup(bot):
    bot.add_cog(Payment(bot))