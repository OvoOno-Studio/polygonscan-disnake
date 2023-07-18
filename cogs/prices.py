import aiohttp
import asyncio
import disnake
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from config import set_transaction_channel, set_price_alert_channel, set_wallet_address, APIKey
from config import get_transaction_channel, get_price_alert_channel, get_wallet_address

class Moni(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.api_url = "https://api.coingecko.com/api/v3/simple/price?ids=matic-network&vs_currencies=usd&include_24hr_change=true"
        self.polygon_scan_api_url = f"https://api.polygonscan.com/api?module=account&action=tokentx&apikey={APIKey}"
        self.sand_contract_address = "0xBbba073C31bF03b8ACf7c28EF0738DeCF3695683"  
        self.wallet_address = None
        self.previous_matic_price = None
        self.last_known_transaction = None
        self.semaphore = asyncio.Semaphore(4)  
        self.bot.loop.create_task(self.price_check_and_alert())
        self.bot.loop.create_task(self.update_crypto_presence())
        self.bot.loop.create_task(self.monitor_wallet_transactions())

    @commands.command(name="set_transaction_channel")
    @has_permissions(administrator=True)
    async def set_transaction_channel(self, ctx, channel: disnake.TextChannel):
        set_transaction_channel(ctx.guild.id, channel.id)
        await ctx.send(f"Transaction channel has been set to {channel.mention}")

    @commands.command(name="set_price_alert_channel")
    @has_permissions(administrator=True)
    async def set_price_alert_channel(self, ctx, channel: disnake.TextChannel):
        set_price_alert_channel(ctx.guild.id, channel.id)
        await ctx.send(f"Price alert channel has been set to {channel.mention}") 

    @commands.command(name="set_wallet_address")
    @has_permissions(administrator=True)
    async def set_wallet_address(self, ctx, address: str):
        set_wallet_address(ctx.guild.id, address)
        await ctx.send(f"Wallet address has been set to `{address}`")

    async def get_coin_data(self):
        try:
            async with self.session.get("https://api.coingecko.com/api/v3/coins/matic-network") as response:
                if response.status != 200:
                    print(f"Failed to fetch coin data, status code: {response.status}, message: {await response.text()}")
                    return None
                json_data = await response.json()
                return json_data
        except Exception as e:
            print(f"Error in get_coin_data: {e}")
            return None

    async def get_crypto_price_data(self):
        coin_data = await self.get_coin_data()
        if coin_data is not None:
            usd_price = coin_data['market_data']['current_price']['usd']
            price_change_24h = coin_data['market_data']['price_change_percentage_24h']
            volume_24h = coin_data['market_data']['total_volume']['usd']
            price_high_24h = coin_data['market_data']['high_24h']['usd']
            price_low_24h = coin_data['market_data']['low_24h']['usd']
            market_cap = coin_data['market_data']['market_cap']['usd']
            total_volume = coin_data['market_data']['total_volume']['usd']
            return usd_price, price_change_24h, volume_24h, price_high_24h, price_low_24h, market_cap, total_volume
        else:
            return None, None, None, None, None, None, None

    async def check_and_send_alert(self, current_price, coin_data):
        try:
            if self.previous_matic_price is None:
                self.previous_matic_price = current_price
                return

            price_change = (current_price - self.previous_matic_price) / self.previous_matic_price * 100 
            direction = "up" if price_change >= 0 else "down"
            arrow_emoji = "🟢" if price_change >= 0 else "🔴"
            
            price_high_24h = coin_data['market_data']['high_24h']['usd']
            price_low_24h = coin_data['market_data']['low_24h']['usd']
            volume_24h = coin_data['market_data']['total_volume']['usd']
            market_cap = coin_data['market_data']['market_cap']['usd']

            for guild in self.bot.guilds:
                price_alert_channel_id = get_price_alert_channel(guild.id)
                channel = self.bot.get_channel(price_alert_channel_id)
                if channel is not None:
                    print(f'Sending price alert to: {channel}')
                    await channel.send(
                        f".\n\n"
                        f"🚨 **PRICE CHANGE ALERT** 🚨\n\n"
                        f"💵 **MATIC Price:** ${current_price:.2f} {arrow_emoji} ({abs(price_change):.2f}% change)\n"
                        f"📈 **24h High:** ${price_high_24h:.2f}\n"
                        f"📉 **24h Low:** ${price_low_24h:.2f}\n"
                        f"💼 **24h Volume:** ${volume_24h:.2f}\n"
                        f"💰 **Market Cap:** ${market_cap:.2f}\n"
                    )
                else:
                    print('No channel optimized')

            self.previous_matic_price = current_price
        except Exception as e:
            print(f"Error in check_and_send_alert: {e}")
            await asyncio.sleep(1)  # Add delay here

    async def price_check_and_alert(self):
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            try:
                current_price, _, _, _, _, _, _ = await self.get_crypto_price_data()
                coin_data = await self.get_coin_data()
                if current_price is not None:
                    await self.check_and_send_alert(current_price, coin_data)
                else:
                    print("No price data to check.")
                    
                await asyncio.sleep(14400)  # 3 hours
                
            except Exception as e:
                print(f"Error in price_check_and_alert: {e}")
                await asyncio.sleep(360)  # In case of an error, wait 1 minute before retrying
    
    async def update_crypto_presence(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                price, price_change_percent, coin_data, *_ = await self.get_crypto_price_data()
                if price is None or price_change_percent is None or coin_data is None:
                    await asyncio.sleep(60)
                    continue
 
                arrow_emoji = "🟢" if price_change_percent > 0 else "🔴"
                status_text = f"MATIC: ${price:.2f} {arrow_emoji}({price_change_percent:.2f}%)"
                await self.bot.change_presence(
                    status=disnake.Status.online,
                    activity=disnake.Activity(
                        type=disnake.ActivityType.watching,
                        name=status_text,
                    ),
                ) 

            except Exception as e:
                print(f"Error updating presence: {e}")
                await asyncio.sleep(1)  # Add delay here

            await asyncio.sleep(30)

    async def limited_get(self, url):
        async with self.semaphore:  # Limit the number of concurrent requests
            async with self.session.get(url) as response:
                return await response.json()

    async def fetch_wallet_transactions(self):
        for guild in self.bot.guilds:
            self.wallet_address = get_wallet_address(guild.id)
            if self.wallet_address is None or len(self.wallet_address) != 42 or not self.wallet_address.startswith('0x'):
                # print(f"Skipping guild {guild.name} due to invalid wallet address: {self.wallet_address}")
                continue
            url = f"{self.polygon_scan_api_url}&address={self.wallet_address}&contractaddress={self.sand_contract_address}&sort=desc"
            try:
                json_data = await self.limited_get(url)
                if json_data and "result" in json_data:
                    return json_data["result"]
                else:
                    print(f"Error in fetch_wallet_transactions: {json_data}")
                    return None
            except Exception as e:
                print(f"Error in fetch_wallet_transactions: {e}")
                return None

    async def send_transaction_message(self, transaction):
        for guild in self.bot.guilds:
            self.wallet_address = get_wallet_address(guild.id)
            self.transaction_channel_id = get_transaction_channel(guild.id)

            # Check if transaction_channel_id is not a valid Discord snowflake
            if not str(self.transaction_channel_id).isnumeric():
                print(f"Invalid channel ID: {self.transaction_channel_id}")
                continue

            try:
                channel = await self.bot.fetch_channel(self.transaction_channel_id)
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
                    else:
                        print('No channel optimized!')
            except disnake.NotFound:
                print(f"Channel with ID {self.transaction_channel_id} not found.")
            except disnake.Forbidden:
                print(f"Bot does not have permission to access channel with ID {self.transaction_channel_id}.")
            except disnake.HTTPException as e:
                if e.status == 429:  # Handle rate limit error
                    print("Rate limit reached, sleeping for a bit...")
                    await asyncio.sleep(10)  # sleep for 10 seconds before trying again
                else:
                    print(f"Error fetching channel with ID {self.transaction_channel_id}: {e}")

    async def monitor_wallet_transactions(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            for guild in self.bot.guilds:
                self.wallet_address = get_wallet_address(guild.id)
                self.transaction_channel_id = get_transaction_channel(guild.id)
                try:
                    transactions = await self.fetch_wallet_transactions()

                    if not transactions or isinstance(transactions, str):
                        print(f"Error in transactions response: {transactions}")
                        await asyncio.sleep(1)  # Add delay here
                        continue

                    print(f"Transaction hash: {transactions[0]['hash']}")

                    last_transaction = None
                    for transaction in transactions:
                        if transaction["to"].lower() == self.wallet_address.lower():
                            last_transaction = transaction
                            await asyncio.sleep(1)  # Add delay here
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
                    
                    await asyncio.sleep(30)

                except Exception as e:
                    print(f"Error monitoring wallet transactions: {e}")
                    await asyncio.sleep(1)

                await asyncio.sleep(60)

def setup(bot):
    bot.add_cog(Moni(bot))