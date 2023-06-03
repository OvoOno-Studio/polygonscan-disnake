# config.py
from dotenv import load_dotenv
from replit import db
from checks import ensure_server_config
import os 

# This creates a connection to your Replit database
def create_connection():
    connection = db.connect()  
    return connection

def set_transaction_channel(server_id, channel_id):
  server_config = ensure_server_config(server_id)
  server_config["transaction_channel_id"] = channel_id

def get_transaction_channel(server_id):
  server_config = ensure_server_config(server_id)
  return server_config.get('price_alert_channel_id')

def set_price_alert_channel(server_id, channel_id):
  server_config = ensure_server_config(server_id)
  server_config["price_alert_channel_id"] = channel_id

def get_price_alert_channel(server_id):
  server_config = ensure_server_config(server_id)
  return server_config.get('price_alert_channel_id')

def set_wallet_address(server_id, wallet_address): 
  server_config = ensure_server_config(server_id)
  server_config["wallet_address"] = wallet_address 

def get_wallet_address(server_id):
  server_config = ensure_server_config(server_id)
  return str(server_config.get("wallet_address"))

load_dotenv()

AppId = os.getenv('APP_ID')
GuildId = os.getenv('GUILD_ID')
DiscordToken = os.getenv('DISCORD_TOKEN')
PublicKey = os.getenv('PUBLIC_KEY')
APIKey = os.getenv('API_KEY')
API2Key = os.getenv('API2_KEY')
# transaction_channel_id = db['GuildConfig']['transaction_channel_id']
# price_alert_channel_id = db['GuildConfig']["price_alert_channel_id"]
# wallet_address = db['GuildConfig']["wallet_address"]  