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
        self.wallet_address = "0xbdd6477fc6f742d37d1A8e5C3C5b069f237b6aFe"  # Replace this with the wallet address you want to monitor
        self.sand_contract_address = "0xbbba073c31bf03b8acf7c28ef0738decf3695683"  # SAND token contract address on Polygon
        self.transaction_channel_id = 944377385682341921  # Replace this with the channel ID where you want to send transaction messages
        self.price_alert_channel_id = 944377385682341921
        self.threshold = 0.05 # 5% threshhold
        self.previous_matic_price = None
        self.last_known_transaction = None

        self.bot.loop.create_task(self.update_crypto_presence())
        self.bot.loop.create_task(self.monitor_wallet_transactions())

    async def get_crypto_price(self, symbol: str):
        async with self.session.get(self.api_url + symbol.upper()) as response:
            json_data = await response.json()
            price = float(json_data['price'])
            return price

    async def check_and_send_alert(self, current_price):
        if self.previous_matic_price is None:
            self.previous_matic_price = current_price
            return

        price_change = (current_price - self.previous_matic_price) / self.previous_matic_price

        if abs(price_change) >= self.threshold:
            channel = self.bot.get_channel(self.price_alert_channel_id)

            if channel:
                direction = "up" if price_change > 0 else "down"
                await channel.send(f"@everyone MATIC price has changed by more than 5%! It's now {direction} to ${current_price:.2f}")

            self.previous_matic_price = current_price

    async def update_crypto_presence(self):
        await self.bot.wait_until_ready()  # Add this line

        while not self.bot.is_closed():
            try:
                price = await self.get_crypto_price('MATICUSDT')  # Fetch the price for MATIC
                await self.check_and_send_alert(price)
                await self.bot.change_presence(
                    status=disnake.Status.online,
                    activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"MATIC: ${price:.2f}")
                )
            except Exception as e:
                print(f"Error updating presence: {e}")

            await asyncio.sleep(60)  # Update the presence every 60 seconds

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
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                transactions = await self.fetch_wallet_transactions()

                if self.last_known_transaction is None:
                    self.last_known_transaction = transactions[0]

                print(f"Checking transactions for wallet {self.wallet_address}")
                for transaction in transactions:
                    if transaction["hash"] == self.last_known_transaction["hash"]:
                        break

                    if transaction["to"].lower() == self.wallet_address.lower():
                        print(f"Sending transaction message for {transaction['hash']}")
                        await self.send_transaction_message(transaction)

                self.last_known_transaction = transactions[0]
            except Exception as e:
                print(f"Error monitoring wallet transactions: {e}")

            await asyncio.sleep(60)  # Check for new transactions every 60 seconds

def setup(bot):
    bot.add_cog(Crypto(bot))