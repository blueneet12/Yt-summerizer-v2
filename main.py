import logging
from pyrogram import Client, idle
from config import Config

# Set the global logging level to WARNING to show only warnings and errors
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Adjust specific logging levels for different libraries
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

app = Client(
    "UnzipBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins"),
)

# Run Bot
if __name__ == "__main__":
    client.start()  # Not using run as wanna print...
    uname = client.get_me().username
    print(f"@{uname} Started Successfully!")
    idle()
    client.stop()
    print("Bot stopped. Alvida!")
