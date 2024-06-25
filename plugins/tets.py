print("bot.py has been loaded")

from pyrogram import Client, filters
# The rest of your bot.py code

@client.on_message(filters.command('start'))
async def start(client, message):
    print("Start command received")  # Add this line
    await message.reply('Send me a YouTube link, and I will summarize that video for you in text format.')
    if not await db.is_inserted("users", message.chat.id):
        await db.insert("users", message.chat.id)
