import json
import requests
import time
import random
from decimal import Decimal
from disnake.ext import commands, tasks
from config import API2Key
from replit import db

class Pay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.payment_wallet = '0x48D0eEE30ec5BF5C7E167036a8c7f3e4820c19fa'
        #self.api = 'https://api.etherscan.io/api'
        self.api = ' https://api-goerli.etherscan.io/api'
        if not self.cleanup_inactive_payments.is_running():
            self.cleanup_inactive_payments.start()

    def generate_uid(self):
        uid_decimal = Decimal(random.uniform(0.000001, 0.000009))
        return uid_decimal.quantize(Decimal('0.000001'))
    
    @staticmethod 
    def ensure_user_table(user_id):
        if not db.get("payment_" + str(user_id)):
            db["payment_" + str(user_id)] = {}

    def save_payment(self, user_id, timestamp, uid):
        self.ensure_user_table(user_id)
        user_payments = db.get("payment_" + str(user_id), {})
        user_payments[str(uid)] = {"timestamp": timestamp, "verified": False}
        db["payment_" + str(user_id)] = user_payments

    def get_payment(self, user_id, uid):
        return db.get("payment_" + str(user_id), {}).get(str(uid), None)

    def verify_payment(self, user_id, uid):
        user_payments = db.get("payment_" + str(user_id), {})
        if str(uid) in user_payments:
            user_payments[str(uid)]["verified"] = True
            db["payment_" + str(user_id)] = user_payments

    def cog_unload(self):
        self.cleanup_inactive_payments.cancel()

    @tasks.loop(hours=13)
    async def cleanup_inactive_payments(self):
        cutoff_time = time.time() - (12 * 3600)
        keys = [key for key in db.keys() if key.startswith("payment_")]
        
        for key in keys:
            try:
                user_payments = db.get(key)
                inactive_keys = [k for k, v in user_payments.items() if v["timestamp"] < cutoff_time and not v["verified"]]
                
                for inactive_key in inactive_keys:
                    del user_payments[inactive_key]
                
                if user_payments:
                    db[key] = user_payments
                else:
                    del db[key]
            except Exception as e:
                print(f"Error cleaning up payments for key {key}: {e}")

    @commands.slash_command(name='upgrade_version', description="Make request payment to upgrade your version.")
    async def upgrade_version(self, ctx): 
        uid = self.generate_uid()
        self.save_payment(ctx.author.id, time.time(), uid)
        message = f"🟢 To upgrade, please send **0.008 + {uid} ETH** (for your unique ID) to `{self.payment_wallet}`.\nOnce done, confirm by typing `/confirm_payment <your_wallet> {uid}`."
        await ctx.response.send_message(content=message)

    @commands.slash_command(name='confirm_payment', description="Confirm your payment.")
    async def confirm_payment(self, ctx, wallet_from: str, uid: str):
        uid_decimal = Decimal(uid).quantize(Decimal('1e-18'))  # Ensure 18 decimal places
        payment = self.get_payment(ctx.author.id, uid)
        if not payment:
            await ctx.response.send_message(content="🔴 You haven't requested an upgrade or incorrect UID provided!")
            return
        timestamp = payment["timestamp"]
        amount_with_uid = (Decimal(0.008) + uid_decimal).quantize(Decimal('1e-18'))  # Ensure 18 decimal places
        amount_with_uid_wei = int((amount_with_uid * Decimal(10**18)).quantize(Decimal('1')))  # Convert to integer wei value

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
            data = response.json()

            if data.get("status") != "1":
                await ctx.response.send_message(content="🔴 Error fetching transaction details from Etherscan.")
                return

        except requests.RequestException as e:
            await ctx.response.send_message(content=f"🔴 Error fetching transaction details: `{e}`")
            return

        for tx in data["result"]:
            tx_value = int(tx["value"])  # Convert tx_value to integer for comparison 
            if (tx["to"] == self.payment_wallet and 
                tx["from"] == wallet_from.lower() and 
                int(tx["timeStamp"]) > timestamp and 
                tx_value == amount_with_uid_wei):
                self.verify_payment(ctx.author.id, uid)
                await ctx.response.send_message(content="✅ Payment verified! Welcome to the premium version.")
                return

        await ctx.response.send_message(content=f"🔴 Payment not found from wallet `{wallet_from}`. Ensure the correct amount and UID was used.")

    @commands.slash_command(name='help_payment', description="Help message")
    async def help_payment(self, ctx):
        message = (
            "📘 **How to Upgrade Guide:**\n"
            "1. Use the `/upgrade_version` command to get your unique amount.\n"
            "2. Send the specified amount to the provided Ethereum address.\n"
            "3. Once sent, confirm your payment using `/confirm_payment <your_wallet> <uid>`.\n"
            "4. Enjoy your premium version!"
        )
        await ctx.response.send_message(content=message)

def setup(bot):
    bot.add_cog(Pay(bot))