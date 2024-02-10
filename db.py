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

def update_config_value(server_id, column_name, value):
    conn = create_connection()
    with conn.cursor() as cur:
        if value is None:
            cur.execute(f"UPDATE server_configs SET {column_name} = NULL WHERE server_id = %s", (server_id,))
        else:
            cur.execute(f"UPDATE server_configs SET {column_name} = %s WHERE server_id = %s", (value, server_id))
        conn.commit()

# Set the transaction channel
def set_transaction_channel(server_id, channel_id):
    update_config_value(server_id, "transaction_channel_id", channel_id)

# Get the transaction channel
def get_transaction_channel(server_id):
    return ensure_server_config(server_id).get('transaction_channel_id')

# Set the price alert channel
def set_price_alert_channel(server_id, channel_id):
    update_config_value(server_id, "price_alert_channel_id", channel_id)

# Get the price alert channel
def get_price_alert_channel(server_id):
    return ensure_server_config(server_id).get('price_alert_channel_id')

# Set the wallet address
def set_wallet_address(server_id, wallet_address):
    update_config_value(server_id, "wallet_address", wallet_address)

# Get the wallet address
def get_wallet_address(server_id):
    return ensure_server_config(server_id).get("wallet_address")

# Set the monitoring token
def set_moni_token(server_id, token):
    update_config_value(server_id, "token", token)

# Get the monitoring token
def get_moni_token(server_id):
    return ensure_server_config(server_id).get("token")

# Set the signal pair
def set_signal_pair(server_id, signal_pair):
    update_config_value(server_id, "signal_pair", signal_pair)

# Get the signal pair
def get_signal_pair(server_id):
    return ensure_server_config(server_id).get("signal_pair")