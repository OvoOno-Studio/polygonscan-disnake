# config.py
from dotenv import load_dotenv
import os
import json

CONFIG_FILE = "config.json"

def _load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def _save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def set_transaction_channel(channel_id):
    config = _load_config()
    config["transaction_channel_id"] = channel_id
    _save_config(config)

def set_price_alert_channel(channel_id):
    config = _load_config()
    config["price_alert_channel_id"] = channel_id
    _save_config(config)

def set_wallet_address(wallet_address):
    config = _load_config()
    config["wallet_address"] = wallet_address
    _save_config(config)

config = _load_config()

load_dotenv()

AppId = os.getenv('APP_ID')
GuildId = os.getenv('GUILD_ID')
DiscordToken = os.getenv('DISCORD_TOKEN')
PublicKey = os.getenv('PUBLIC_KEY')
APIKey = os.getenv('API_KEY')
transaction_channel_id = config["transaction_channel_id"]
price_alert_channel_id = config["price_alert_channel_id"]
wallet_address = config["wallet_address"]