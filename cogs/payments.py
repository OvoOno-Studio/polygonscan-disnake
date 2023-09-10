import json
import requests
import time
import random
import aiomysql
from disnake.ext import commands, tasks
from config import API2Key, DBUser, DBPw

class Pay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.payment_wallet = '0x48D0eEE30ec5BF5C7E167036a8c7f3e4820c19fa'
        self.api = 'https://api.etherscan.io/api'
        self.pool = bot.loop.run_until_complete(self.init_pool())
        self.clean_inactive_payments.start()

    async def init_pool(self):
        try:
            return await aiomysql.create_pool(host='67.223.118.135', port=3306,
                                              user=DBUser, password=DBPw,
                                              db='ovoovtvo_bot_payments', loop=self.bot.loop)
        except Exception as e:
            print(f"Error creating database pool: {e}")
            return None

    async def execute(self, query, *args, many=False, commit=False):
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cur:
                    if many:
                        await cur.executemany(query, args)
                    else:
                        await cur.execute(query, args)
                    if commit:
                        await conn.commit()
                    return await cur.fetchall()
        except Exception as e:
            print(f"Database error: {e}")
            return None

    def generate_uid(self):
        return round(random.uniform(0.000001, 0.000009), 6)

    @tasks.loop(hours=12)
    async def clean_inactive_payments(self):
        current_time = time.time()
        past_time = current_time - 86400
        query = "DELETE FROM payments WHERE timestamp <= %s AND verified = 0"
        await self.execute(query, past_time, commit=True)

    @clean_inactive_payments.before_loop
    async def before_cleaner(self):
        await self.bot.wait_until_ready()

    @commands.slash_command(name='upgrade_version', description="Make request payment to upgrade your version.")
    async def upgrade_version(self, ctx): 
        uid = self.generate_uid()
        query = "INSERT INTO payments(user_id, timestamp, uid) VALUES (%s, %s, %s)"
        result = await self.execute(query, ctx.author.id, time.time(), uid, commit=True)

        if result:
            message = f"🟢 To upgrade, please send **0.088 + {uid} ETH** (for your unique ID) to `{self.payment_wallet}`.\nOnce done, confirm by typing `/confirm_payment <your_wallet> {uid}`."
            await ctx.response.send_message(content=message)
        else:
            await ctx.response.send_message(content="🔴 There was an error processing your request. Please try again later.")

    @commands.slash_command(name='confirm_payment', description="Confirm your payment.")
    async def confirm_payment(self, ctx, wallet_from: str, uid: float):
        query = "SELECT timestamp FROM payments WHERE user_id = %s AND uid = %s AND verified = 0"
        result = await self.execute(query, ctx.author.id, uid)
        if not result:
            await ctx.response.send_message(content="🔴 You haven't requested an upgrade or incorrect UID provided!")
            return

        timestamp = result[0][0]
        amount_with_uid = 0.088 + uid

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
                update_query = "UPDATE payments SET verified = 1 WHERE user_id = %s AND uid = %s"
                await self.execute(update_query, ctx.author.id, uid, commit=True)
                await ctx.response.send_message(content="✅ Payment verified! Welcome to the premium version.")
                return

        await ctx.response.send_message(content=f"🔴 Payment not found from wallet `{wallet_from}`. Ensure the correct amount and UID was used.")

    @commands.slash_command(name='help_payment', description="Help message")
    async def help_payment(self, ctx):
        message = """📘 **How to Upgrade Guide:**
            1. Use the `/upgrade_version` command to get your unique amount.
            2. Send the specified amount to the provided Ethereum address.
            3. Once sent, confirm your payment using `/confirm_payment <your_wallet> <uid>`.
            4. Enjoy your premium version!"""
        await ctx.response.send_message(content=message)

    def cog_unload(self):
        if self.pool:
            self.pool.close()
            self.bot.loop.run_until_complete(self.pool.wait_closed())

def setup(bot):
    bot.add_cog(Pay(bot))
