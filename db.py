import psycopg2
import os

# Establishes a connection to the PostgreSQL database
def create_connection():
    DATABASE_URL = os.environ['DATABASE_URL']  # Replace with your database URL
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Helper function to get or create server configuration
def ensure_server_config(server_id):
    conn = create_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM server_configs WHERE server_id = %s", (server_id,))
        config = cur.fetchone()
        if config is None:
            cur.execute("INSERT INTO server_configs (server_id) VALUES (%s)", (server_id,))
            conn.commit()
            return {}
        else:
            return {
                "transaction_channel_id": config[1],
                "price_alert_channel_id": config[2],
                "wallet_address": config[3],
                "token": config[4],
                "signal_pair": config[5]
            }

# Set the transaction channel
def set_transaction_channel(server_id, channel_id):
    conn = create_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE server_configs SET transaction_channel_id = %s WHERE server_id = %s", (channel_id, server_id))
        conn.commit()

# Get the transaction channel
def get_transaction_channel(server_id):
    config = ensure_server_config(server_id)
    return config.get('transaction_channel_id')

# Set the price alert channel
def set_price_alert_channel(server_id, channel_id):
    conn = create_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE server_configs SET price_alert_channel_id = %s WHERE server_id = %s", (channel_id, server_id))
        conn.commit()

# Get the price alert channel
def get_price_alert_channel(server_id):
    config = ensure_server_config(server_id)
    return config.get('price_alert_channel_id')

# Set the wallet address
def set_wallet_address(server_id, wallet_address):
    conn = create_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE server_configs SET wallet_address = %s WHERE server_id = %s", (wallet_address, server_id))
        conn.commit()

# Get the wallet address
def get_wallet_address(server_id):
    config = ensure_server_config(server_id)
    return config.get("wallet_address")

# Set the monitoring token
def set_moni_token(server_id, token):
    conn = create_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE server_configs SET token = %s WHERE server_id = %s", (token, server_id))
        conn.commit()

# Get the monitoring token
def get_moni_token(server_id):
    config = ensure_server_config(server_id)
    return config.get("token")

# Set the signal pair
def set_signal_pair(server_id, signal_pair):
    conn = create_connection()
    with conn.cursor() as cur:
        cur.execute("UPDATE server_configs SET signal_pair = %s WHERE server_id = %s", (signal_pair, server_id))
        conn.commit()

# Get the signal pair
def get_signal_pair(server_id):
    config = ensure_server_config(server_id)
    return config.get("signal_pair")