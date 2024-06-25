import logging
from pyrogram import Client, idle
from config import Config

# Set the global logging level to DEBUG for detailed output
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Adjust specific logging levels for different libraries
logging.getLogger("pyrogram").setLevel(logging.DEBUG)
logging.getLogger("PIL").setLevel(logging.WARNING)

client = Client(
    "UnzipBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins"),  # Ensure plugins are loaded from this directory
)

# Run Bot
if __name__ == "__main__":
    client.start()
    uname = client.get_me().username
    print(f"@{uname} Started Successfully!")
    idle()
    client.stop()
    print("Bot stopped. Alvida!")
