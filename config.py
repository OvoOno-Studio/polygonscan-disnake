import os
from dotenv import load_dotenv

load_dotenv()

AppId = os.getenv('APP_ID')
GuildId = os.getenv('GUILD_ID')
DiscordToken = os.getenv('DISCORD_TOKEN')
PublicKey = os.getenv('PUBLIC_KEY')
APIKey = os.getenv('API_KEY')