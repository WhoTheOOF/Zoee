from dotenv import load_dotenv
import os
import pathlib

load_dotenv()

DISCORD_API_SECRET = os.getenv('DISCORD_API_TOKEN')

BASE_DIR = pathlib.Path(__file__).parent

COG_DIR = BASE_DIR / "cogs"

MAX_EMBED_LENGHT = 10

LAVALINK_INFO = {
    "server": "http://lavalink.silverblare.com:2333",
    "password": "youshallnotpass"
}