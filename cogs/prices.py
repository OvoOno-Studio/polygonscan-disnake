import aiohttp
import asyncio
import disnake
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from config import set_transaction_channel, set_price_alert_channel, set_wallet_address
from config import APIKey, transaction_channel_id, price_alert_channel_id, wallet_address

class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.api_url = "https://api.coingecko.com/api/v3/simple/price?ids=matic-network&vs_currencies=usd&include_24hr_change=true"
        self.polygon_scan_api_url = f"https://api.polygonscan.com/api?module=account&action=tokentx&apikey={APIKey}"
        self.wallet_address = wallet_address
        self.sand_contract_address = "0xBbba073C31bF03b8ACf7c28EF0738DeCF3695683" 
        self.transaction_channel_id = transaction_channel_id 
        self.price_alert_channel_id = price_alert_channel_id
        #self.threshold = 0.02
        self.previous_matic_price = None
        self.last_known_transaction = None
        self.semaphore = asyncio.Semaphore(4)  
        self.bot.loop.create_task(self.price_check_and_alert())
        print('Scheduled price_check_and_alert every 3 hours')
        self.bot.loop.create_task(self.update_crypto_presence())
        print('Scheduled update_crypto_presence every 30 seconds')
        self.bot.loop.create_task(self.monitor_wallet_transactions())
        print('Scheduled monitor_wallet_transactions every 60 seconds')

    @commands.command(name="set_transaction_channel")
    @has_permissions(administrator=True)
    async def set_transaction_channel(self, ctx, channel: disnake.TextChannel):
        set_transaction_channel(channel.id)
        self.transaction_channel_id = channel.id
        await ctx.send(f"Transaction channel has been set to {channel.mention}")

    @commands.command(name="set_price_alert_channel")
    @has_permissions(administrator=True)
    async def set_price_alert_channel(self, ctx, channel: disnake.TextChannel):
        set_price_alert_channel(channel.id)
        self.price_alert_channel_id = channel.id
        await ctx.send(f"Price alert channel has been set to {channel.mention}")

    @commands.command(name="set_wallet_address")
    @has_permissions(administrator=True)
    async def set_wallet_address(self, ctx, address: str):
        set_wallet_address(address)
        self.wallet_address = address
        await ctx.send(f"Wallet address has been set to `{address}`") 

    async def get_crypto_price_data(self):
        try:
            async with self.session.get(self.api_url) as response:
                if response.status != 200:
                    print(f"Failed to fetch crypto price data, status code: {response.status}, message: {await response.text()}")
                    return None, None
                json_data = await response.json()
                return json_data['matic-network']['usd'], json_data['matic-network']['usd_24h_change']
        except Exception as e:
            print(f"Error in get_crypto_price_data: {e}")
            return None, None

    async def check_and_send_alert(self, current_price):
        try:
            print('Checking MATIC price...')
            if self.previous_matic_price is None:
                self.previous_matic_price = current_price
                return

            price_change = (current_price - self.previous_matic_price) / self.previous_matic_price * 100 
            print(f'New price: {price_change}') 
            direction = "up" if price_change >= 0 else "down"
            arrow_emoji = "🟢" if price_change >= 0 else "🔴"
            channel = self.bot.get_channel(self.price_alert_channel_id)
            if channel is not None:
                print(f'Sendning price alert to: {channel}')
                await channel.send(f"📢 PRICE CHANGE ALERT 📢\n**MATIC** price has changed by {abs(price_change):.2f}%!\n\nIt's now **{direction.upper()}** to **${current_price:.2f}** {arrow_emoji}\n")
            else:
                print('No channel optimized')
            self.previous_matic_price = current_price
        except Exception as e:
            print(f"Error in check_and_send_alert: {e}")

    async def price_check_and_alert(self):
        while not self.bot.is_closed():
            try:
                current_price, price_change_24h = await self.get_crypto_price_data()
                if current_price is not None:
                    await self.check_and_send_alert(current_price)
                else:
                    print("No price data to check.")
                await asyncio.sleep(3 * 60 * 60)  # 10 minutes
            except Exception as e:
                print(f"Error in price_check_and_alert: {e}")
                await asyncio.sleep(60)  # In case of an error, wait 10 minutes before retrying
    
    async def update_crypto_presence(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                price, price_change_percent = await self.get_crypto_price_data()
                if price is None or price_change_percent is None:
                    await asyncio.sleep(60)
                    continue

                color = disnake.Color.green() if price_change_percent >= 0 else disnake.Color.red()
                arrow_emoji = "🟢" if price_change_percent > 0 else "🔴"
                status_text = f"MATIC: ${price:.2f} {arrow_emoji}({price_change_percent:.2f}%)"
                print(f'Updating crypto presencace: {price}')
                await self.bot.change_presence(
                    status=disnake.Status.online,
                    activity=disnake.Activity(
                        type=disnake.ActivityType.watching,
                        name=status_text,
                    ),
                ) 

            except Exception as e:
                print(f"Error updating presence: {e}")

            await asyncio.sleep(30)

    async def limited_get(self, url):
        async with self.semaphore:  # Limit the number of concurrent requests
            async with self.session.get(url) as response:
                return await response.json()

    async def fetch_wallet_transactions(self):
        url = f"{self.polygon_scan_api_url}&address={self.wallet_address}&contractaddress={self.sand_contract_address}&sort=desc"
        try:
            json_data = await self.limited_get(url)
            # print(f"fetch_wallet_transactions response: {json_data}")  # Log the response for debugging
            if json_data and "result" in json_data:
                return json_data["result"]
            else:
                print(f"Error in fetch_wallet_transactions: {json_data}")
                return None
        except Exception as e:
            print(f"Error in fetch_wallet_transactions: {e}")
            return None

    async def send_transaction_message(self, transaction):
        try:
            channel = await self.bot.fetch_channel(self.transaction_channel_id)
        except disnake.NotFound:
            print(f"Channel with ID {self.transaction_channel_id} not found.")
            return
        except disnake.Forbidden:
            print(f"Bot does not have permission to access channel with ID {self.transaction_channel_id}.")
            return
        except disnake.HTTPException as e:
            print(f"Error fetching channel with ID {self.transaction_channel_id}: {e}")
            return

        if channel:
            print(f"Sending message to channel {channel.id}")  # Debugging print statement
            message = (
                f"🚨 New incoming SAND token transaction to `{self.wallet_address}` 🚨\n"
                f"💰 Value: {float(transaction['value']) / (10 ** 18):.2f} SAND\n"
                f"🧑 From: `{transaction['from']}`\n"
                f"👉 To: `{transaction['to']}`\n"
                f"🔗 Transaction Hash: [`{transaction['hash']}`](https://polygonscan.com/tx/{transaction['hash']})\n"
                f"🧱 Block Number: `{transaction['blockNumber']}`\n"
                f"🔢 Transaction Index: `{transaction['transactionIndex']}`"
            )
            try:
                await channel.send(message)
                print(f"Message sent to: {channel}") # Debugging print statement
            except disnake.HTTPException as e:
                print(f"Error sending message to channel with ID {self.transaction_channel_id}: {e}")

    async def monitor_wallet_transactions(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                transactions = await self.fetch_wallet_transactions()

                if not transactions or isinstance(transactions, str):
                    print(f"Error in transactions response: {transactions}")
                    continue

                print(f"Transaction hash: {transactions[0]['hash']}")

                last_transaction = None
                for transaction in transactions:
                    if transaction["to"].lower() == self.wallet_address.lower():
                        last_transaction = transaction
                        break

                if last_transaction is None:
                    print(f"No incoming transactions found for wallet {self.wallet_address}")
                    continue

                if self.last_known_transaction is None:
                    self.last_known_transaction = last_transaction
                else:
                    if self.last_known_transaction["hash"] != last_transaction["hash"]:
                        print(f"New incoming transaction found: {last_transaction}")
                        print(f"Sending transaction message for {last_transaction['hash']}")
                        await self.send_transaction_message(last_transaction)
                        self.last_known_transaction = last_transaction
                    else:
                        print(f"No new incoming transactions found for wallet {self.wallet_address}")

            except Exception as e:
                print(f"Error monitoring wallet transactions: {e}")

            await asyncio.sleep(5 * 60)

    async def send_no_transactions_message(self):
        channel = self.bot.get_channel(self.transaction_channel_id)

        if channel:
            message = f"No transactions found for wallet {self.wallet_address}."
            await channel.send(message)

def setup(bot):
    bot.add_cog(Crypto(bot))