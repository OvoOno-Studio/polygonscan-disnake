from dotenv import load_dotenv  
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
BearerToken = os.getenv('TOKEN')
ClientID = os.getenv('CLIENT')
Secret = os.getenv('SECRET')