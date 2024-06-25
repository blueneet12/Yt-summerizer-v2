import os
import re
import asyncio
import speech_recognition as sr
from pydub import AudioSegment
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from groq import Groq
from pyrogram import Client, filters
from youtube_transcript_api.formatters import JSONFormatter
from config import Config, Ai, Telegram
from database import db


@Client.on_message(filters.command('start'))
async def start(client, message):
    await message.reply('Send me a YouTube link, and I will summarize that video for you in text format.')
    if not await db.is_inserted("users", message.chat.id):
        await db.insert("users", message.chat.id)

@Client.on_message(filters.command('users') & filters.user(Telegram.AUTH_USER_ID))
async def users(client, message):
    try:
        users = len(await db.fetch_all("users"))
        await message.reply(f'Total Users: {users}')
    except Exception as e:
        print(f"Error fetching users: {e}")

@Client.on_message(filters.command('bcast') & filters.user(Telegram.AUTH_USER_ID))
async def bcast(client, message):
    if not message.reply_to_message:
        return await message.reply(
            "Please use `/bcast` as reply to the message you want to broadcast."
        )
    msg = message.reply_to_message
    xx = await message.reply("In progress...")
    users = await db.fetch_all('users')
    done = error = 0
    for user_id in users:
        try:
            await client.send_message(
                int(user_id),
                msg.text.format(user=(await client.get_users(int(user_id))).first_name),
                file=msg.media,
                buttons=msg.buttons,
                disable_web_page_preview=True,
            )
            done += 1
        except Exception as brd_er:
            print(f"Broadcast error:\nChat: {int(user_id)}\nError: {brd_er}")
            error += 1
    await xx.edit(f"Broadcast completed.\nSuccess: {done}\nFailed: {error}")
