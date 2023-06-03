from replit import db

def create_connection():
    connection = db.connect()  # This creates a connection to your Replit database
    return connection

def fetch_guild_config(guild_id):
    # The key is assumed to be the guild_id
    guild_config = db.get(str(guild_id))
    return guild_config
