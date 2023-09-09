import json
import requests
import time
import random
from disnake.ext import commands
from config import API2Key

class Pay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.payment_wallet = '0x48D0eEE30ec5BF5C7E167036a8c7f3e4820c19fa'
        self.api = 'https://api.etherscan.io/api'
    
    def generate_uid(self):
        return round(random.uniform(0.000001, 0.000009), 6)
    
    @commands.slash_command(name='upgrade_version', description="Make request payment to upgrade your version.")
    async def upgrade_version(self, ctx): 
        uid = self.generate_uid()
        with open("payments.json", "r+") as file:
            donators = json.load(file)
            donators.append({
                "user_id": ctx.author.id,
                "timestamp": time.time(),
                "uid": uid
            })
            file.seek(0)
            json.dump(donators, file)

        message = f"🟢 To upgrade, please send **0.088 + {uid} ETH** (for your unique ID) to `{self.payment_wallet}`.\nOnce done, confirm by typing `/confirm_payment <your_wallet> {uid}`."
        await ctx.response.send_message(content=message)

    @commands.slash_command(name='confirm_payment')
    async def confirm_payment(self, ctx, wallet_from: str, uid: float):
        with open("payments.json", "r") as file:
            payments = json.load(file)
            user_data = next((item for item in payments if item["user_id"] == ctx.author.id and item["uid"] == uid), None)
            if not user_data:
                await ctx.response.send_message(content="🔴 You haven't requested an upgrade or incorrect UID provided!")
                return

        timestamp = user_data["timestamp"]
        amount_with_uid = 0.088 + uid

        # Remove inactive payments (older than 24 hours)
        current_time = time.time()
        payments = [item for item in payments if current_time - item["timestamp"] <= 86400]
        with open("payments.json", "w") as file:
            json.dump(payments, file)

        params = {
            "module": "account",
            "action": "txlist",
            "address": self.payment_wallet,
            "startblock": 0,
            "endblock": 99999999, 
            "sort": "desc", 
            "apikey": API2Key
        }

        try:
            response = requests.get(self.api, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            await ctx.response.send_message(content=f"🔴 Error fetching transaction details: `{e}`")
            return

        data = response.json()

        if not data.get("result"):
            await ctx.response.send_message(content="🔴 I couldn't verify the payment at this time. Please try again later.")
            return

        for tx in data["result"]:
            if tx["to"] == self.payment_wallet and tx["from"] == wallet_from.lower() and int(tx["timeStamp"]) > timestamp and float(tx["value"]) == amount_with_uid * 10**18:
                await ctx.response.send_message(content="✅ Payment verified! Welcome to the premium version.")
                return

        await ctx.response.send_message(content=f"🔴 Payment not found from wallet `{wallet_from}`. Ensure the correct amount and UID was used.")

    @commands.slash_command(name='help_payment')
    async def help_payment(self, ctx):
        message = """📘 **How to Upgrade Guide:**
            1. Use the `/upgrade_version` command to get your unique amount.
            2. Send the specified amount to the provided Ethereum address.
            3. Once sent, confirm your payment using `/confirm_payment <your_wallet> <uid>`.
            4. Enjoy your premium version!"""
        await ctx.response.send_message(content=message)

def setup(bot):
    bot.add_cog(Pay(bot))
