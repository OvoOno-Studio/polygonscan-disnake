from dotenv import load_dotenv
from replit import db
from checks import ensure_server_config
import os 

load_dotenv()

AppId = os.getenv('APP_ID')
GuildId = os.getenv('GUILD_ID')
DiscordToken = os.getenv('DISCORD_TOKEN')
PublicKey = os.getenv('PUBLIC_KEY')
APIKey = os.getenv('API_KEY')
API2Key = os.getenv('API2_KEY')
API3Key = os.getenv('API3_KEY')
jwt = os.getenv('JWT')
twitter_bearer = os.getenv('TWITTER_BEARER')
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
# Upgrate.Chat API 
BearerToken = os.getenv('TOKEN')
ClientID = os.getenv('CLIENT')
Secret = os.getenv('SECRET')

DBUser = os.getenv('DBUser')
DBPw = os.getenv('DBPw')

# This creates a connection to your Replit database
def create_connection():
    connection = db.connect()  
    return connection

def set_transaction_channel(server_id, channel_id):
    server_config = ensure_server_config(server_id)
    server_config["transaction_channel_id"] = channel_id
    db[str(server_id)] = server_config

def get_transaction_channel(server_id):
    server_config = ensure_server_config(server_id)
    return server_config.get('transaction_channel_id')

def set_price_alert_channel(server_id, channel_id):
    server_config = ensure_server_config(server_id)
    server_config["price_alert_channel_id"] = channel_id
    db[str(server_id)] = server_config

def get_price_alert_channel(server_id):
    server_config = ensure_server_config(server_id)
    return server_config.get('price_alert_channel_id')

def set_wallet_address(server_id, wallet_address): 
    server_config = ensure_server_config(server_id)
    server_config["wallet_address"] = wallet_address 
    db[str(server_id)] = server_config

def get_wallet_address(server_id):
    server_config = ensure_server_config(server_id)
    return server_config.get("wallet_address")

def set_moni_token(server_id, token):
    server_config = ensure_server_config(server_id)
    server_config["token"] = token
    return server_config.get("token")

def get_moni_token(server_id):
    server_config = ensure_server_config(server_id)
    return server_config.get("token")

def set_signal_pair(server_id, signal_pair):
    server_config = ensure_server_config(server_id)
    server_config["signal_pair"] = signal_pair
    db[str(server_id)] = server_config

def get_signal_pair(server_id):
    server_config = ensure_server_config(server_id)
    return server_config.get("signal_pair")