import disnake
import json
import requests
import time
import random
from disnake.ext import commands
from config import API2Key

class Payment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.payment_wallet = '0x48D0eEE30ec5BF5C7E167036a8c7f3e4820c19fa'
        self.api = 'https://api.etherscan.io/api'

    def generate_uid(self):
        # Generate a UID in the format of 0.00000x where x is a random number between 1 to 9
        return round(random.uniform(0.000001, 0.000009), 6)

    @commands.slash_command(name='upgrade_version')
    async def upgrade_version(self, ctx): 
        uid = self.generate_uid()
        amount_with_uid = 0.088 + uid
        with open("donators.json", "r+") as file:
            donators = json.load(file)
            donators.append({
                "user_id": ctx.author.id,
                "timestamp": time.time(),
                "uid": uid
            })
            file.seek(0)
            json.dump(donators, file)

        message = f"Please send exactly {amount_with_uid} ETH (0.088 + {uid} for your unique ID) to the address {self.payment_wallet} and let me know once done by typing `/confirm_payment <your_wallet>`."
        await ctx.response.send_message(content=message)

    @commands.slash_command(name='confirm_payment')
    async def confirm_payment(self, ctx, wallet_from: str):
        wallet = self.payment_wallet
        api = self.api

        with open("payments.json", "r") as file:
            donators = json.load(file)
            user_data = next((item for item in donators if item["user_id"] == ctx.author.id), None)
            if not user_data:
                await ctx.response.send_message(content="You haven't requested an upgrade!")
                return

        uid = user_data["uid"]
        amount_with_uid = 0.088 + uid
        timestamp = user_data["timestamp"]

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
            await ctx.response.send_message(content=f"Error fetching transaction details: {e}")
            return

        data = response.json()

        if not data.get("result"):
            await ctx.response.send_message(content="I couldn't verify the payment at this time. Please try again later.")
            return

        for tx in data["result"]:
            if tx["to"] == wallet and tx["from"] == wallet_from.lower() and int(tx["timeStamp"]) > timestamp and float(tx["value"]) == amount_with_uid * 10**18:
                # Remove the user's data from donators.json to mark UID as used
                donators = [item for item in donators if item["user_id"] != ctx.author.id]
                with open("donators.json", "w") as file:
                    json.dump(donators, file)

                await ctx.response.send_message(content="Payment verified! You have been upgraded to the premium version.")
                return

        await ctx.response.send_message(content=f"Payment not found from wallet {wallet_from}. Ensure you've sent the correct amount to the right address and included the UID.")

def setup(bot):
    bot.add_cog(Payment(bot))