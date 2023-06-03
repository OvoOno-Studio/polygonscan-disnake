# config.py
from dotenv import load_dotenv
from replit import db
import os
import json

CONFIG_FILE = "config.json"

def _load_config():
  with open(CONFIG_FILE, "r") as f:
    return json.load(f)

# def _save_config(config):
#   with open(CONFIG_FILE, "w") as f:
#     json.dump(config, f, indent=4)

def set_transaction_channel(channel_id):
  # Ensure 'GuildConfig' exists in db and is a dictionary
  if "GuildConfig" not in db or not isinstance(db["GuildConfig"], dict):
    print('No database!')

  # Update the channel for price allerts
  db["GuildConfig"]["transaction_channel_id"] = transaction_channel_id

def set_price_alert_channel(channel_id):
  # Ensure 'GuildConfig' exists in db and is a dictionary
  if "GuildConfig" not in db or not isinstance(db["GuildConfig"], dict):
    print('No database!')

  # Update the channel for price allerts
  db["GuildConfig"]["price_alert_channel_id"] = price_alert_channel_id 

def set_wallet_address(wallet_address):
  # Ensure 'GuildConfig' exists in db and is a dictionary
  if "GuildConfig" not in db or not isinstance(db["GuildConfig"], dict):
    print('No database!')

  # Update the wallet address
  db["GuildConfig"]["wallet_address"] = wallet_address 

config = _load_config()

load_dotenv()

AppId = os.getenv('APP_ID')
GuildId = os.getenv('GUILD_ID')
DiscordToken = os.getenv('DISCORD_TOKEN')
PublicKey = os.getenv('PUBLIC_KEY')
APIKey = os.getenv('API_KEY')
API2Key = os.getenv('API2_KEY')
transaction_channel_id = db['GuildConfig']['transaction_channel_id']
price_alert_channel_id = db['GuildConfig']["price_alert_channel_id"]
wallet_address = db['GuildConfig']["wallet_address"]  