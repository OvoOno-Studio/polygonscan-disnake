import disnake
from disnake.ext import commands
import aiohttp
import asyncio
from config import APIKey

class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.api_url = "https://api.binance.com/api/v3/ticker/price?symbol="
        self.polygon_scan_api_url = f"https://api.polygonscan.com/api?module=account&action=tokentx&apikey={APIKey}"
        self.wallet_address = "0x0ece356189Ba7106Fe3F02ed05fFB1A5F5a366De"  # Replace this with the wallet address you want to monitor
        self.sand_contract_address = "0xC6d54D2f624bc83815b49d9c2203b1330B841cA0"  # SAND token contract address on Polygon
        self.transaction_channel_id = 944377385682341921  # Replace this with the channel ID where you want to send transaction messages

        self.previous_matic_price = None
        self.last_known_transaction = None

        self.bot.loop.create_task(self.update_crypto_presence())
        self.bot.loop.create_task(self.monitor_wallet_transactions()) 

    async def fetch_wallet_transactions(self):
        url = f"{self.polygon_scan_api_url}&address={self.wallet_address}&contractaddress={self.sand_contract_address}"
        async with self.session.get(url) as response:
            json_data = await response.json()
            return json_data["result"]

    async def send_transaction_message(self, transaction):
        channel = self.bot.get_channel(self.transaction_channel_id)

        if channel:
            message = (
                f"New incoming SAND token transaction to {self.wallet_address}:\n"
                f"Transaction Hash: {transaction['hash']}\n"
                f"From: {transaction['from']}\n"
                f"To: {transaction['to']}\n"
                f"Value: {float(transaction['value']) / (10 ** 18)} SAND\n"
                f"Block Number: {transaction['blockNumber']}\n"
                f"Transaction Index: {transaction['transactionIndex']}"
            )
            await channel.send(message)

    async def monitor_wallet_transactions(self):
        while True:
            try:
                transactions = await self.fetch_wallet_transactions()

                if self.last_known_transaction is None:
                    self.last_known_transaction = transactions[0]

                for transaction in transactions:
                    if transaction["hash"] == self.last_known_transaction["hash"]:
                        break

                    if transaction["to"].lower() == self.wallet_address.lower():
                        await self.send_transaction_message(transaction)

                self.last_known_transaction = transactions[0]
            except Exception as e:
                print(f"Error monitoring wallet transactions: {e}")

            await asyncio.sleep(60)  # Check for new transactions every 60 seconds

def setup(bot):
    bot.add_cog(Crypto(bot))