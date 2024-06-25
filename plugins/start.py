from Data import Data
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup


# Start Message
@Client.on_message(filters.private & filters.incoming & filters.command("start"))
async def start(unzipbot, msg):
    user = await unzipbot.get_me()
    await unzipbot.send_message(
        msg.chat.id,
        Data.START,
        reply_markup=InlineKeyboardMarkup(Data.buttons)
    )
