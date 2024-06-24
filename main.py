import os
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytube import YouTube
import speech_recognition as sr
from pydub import AudioSegment
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from config import Telegram, Ai
from database import db

system_prompt = """
Do NOT repeat unmodified content.
Do NOT mention anything like "Here is the summary:" or "Here is a summary of the video in 2-3 sentences:" etc.
User will only give you youtube video subtitles, For summarizing YouTube video subtitles:
- No word limit on summaries.
- Use Telegram markdowns for better formatting: **bold**, *italic*, `monospace`, ~~strike~~, <u>underline</u>, <pre language="c++">code</pre>.
- Try to cover every concept that are covered in the subtitles.

For song lyrics, poems, recipes, sheet music, or short creative content:
- Do NOT repeat the full content verbatim.
- This restriction applies even for transformations or translations.
- Provide short snippets, high-level summaries, analysis, or commentary.

Be helpful without directly copying content."""

# Initialize the Pyrogram client
app = Client("bot", api_id=Telegram.API_ID, api_hash=Telegram.API_HASH, bot_token=Telegram.BOT_TOKEN)

# Speech recognizer
recognizer = sr.Recognizer()

async def extract_youtube_transcript(youtube_url):
    try:
        video_id_match = re.search(r"(?<=v=)[^&]+|(?<=youtu.be/)[^?|\n]+", youtube_url)
        video_id = video_id_match.group(0) if video_id_match else None
        if video_id is None:
            return "no transcript"
        loop = asyncio.get_event_loop()
        transcript_list = await loop.run_in_executor(None, YouTubeTranscriptApi.list_transcripts, video_id)
        transcript = transcript_list.find_transcript(['en', 'ja', 'ko', 'de', 'fr', 'ru', 'it', 'es', 'pl', 'uk', 'nl', 'zh-TW', 'zh-CN', 'zh-Hant', 'zh-Hans'])
        transcript_text = ' '.join([item['text'] for item in transcript.fetch()])
        return transcript_text
    except Exception as e:
        print(f"Error: {e}")
        return "no transcript"

async def get_groq_response(user_prompt, system_prompt):
    try:
        client = Groq(api_key=Ai.GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error getting Groq response: {e}")
        return "Error getting AI response."

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply('Send me a YouTube link, and I will summarize that video for you in text format.')
    if not await db.is_inserted("users", message.from_user.id):
        await db.insert("users", message.from_user.id)

@app.on_message(filters.command("users") & filters.user(Telegram.AUTH_USER_ID))
async def users(client, message: Message):
    try:
        users = await db.fetch_all("users")
        await message.reply(f'Total Users: {len(users)}')
    except Exception as e:
        print(e)

@app.on_message(filters.command("bcast") & filters.user(Telegram.AUTH_USER_ID))
async def bcast(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Please use `/bcast` as a reply to the message you want to broadcast.")
    msg = message.reply_to_message
    xx = await message.reply("In progress...")
    users = await db.fetch_all('users')
    done = error = 0
    for user_id in users:
        try:
            await app.send_message(int(user_id), msg.text, reply_markup=msg.reply_markup)
            done += 1
        except Exception as brd_er:
            print(f"Broadcast error:\nChat: {int(user_id)}\nError: {brd_er}")
            error += 1
    await xx.edit_text(f"Broadcast completed.\nSuccess: {done}\nFailed: {error}")

@app.on_message(filters.text & ~filters.command)
async def handle_message(client, message: Message):
    url = message.text
    if message.text.startswith('/start'):
        return
    print(f"Received URL: {url}")

    # Check if the message is a YouTube link
    if 'youtube.com' in url or 'youtu.be' in url:
        x = await message.reply('Attempting to download captions from the YouTube video...')
        print("Attempting to download captions from YouTube...")

        try:
            # Try to get the transcript first
            transcript_text = await extract_youtube_transcript(url)
            if transcript_text != "no transcript":
                print("Transcript fetched successfully.")
                await x.edit_text('Captions found and downloaded. Summarizing the text...')

                summary = await get_groq_response(transcript_text, system_prompt)
                await x.edit_text(f'{summary}')
            else:
                # No transcript available, fallback to audio transcription
                await x.edit_text('No captions found. Downloading audio from the YouTube video...')
                print("No captions found. Downloading audio from YouTube...")

                loop = asyncio.get_event_loop()
                yt = await loop.run_in_executor(None, YouTube, url)
                audio_stream = yt.streams.filter(only_audio=True).first()
                output_file = await loop.run_in_executor(None, audio_stream.download, 'audio.mp4')
                print(f"Downloaded audio to {output_file}")

                await x.edit_text('Converting audio to text...')
                print("Converting audio to text...")

                # Convert audio to WAV format
                try:
                    audio = AudioSegment.from_file(output_file)
                    wav_file = "audio.wav"
                    audio.export(wav_file, format="wav")
                    print(f"Converted audio to {wav_file}")

                    # Convert audio to text
                    with sr.AudioFile(wav_file) as source:
                        recognizer.adjust_for_ambient_noise(source)
                        audio_data = recognizer.record(source)
                        try:
                            text = recognizer.recognize_google(audio_data)
                            print(f"Transcribed text: {text}")

                            # Summarize the transcribed text
                            await x.edit_text('Summarizing the text...')
                            summary = await get_groq_response(text, system_prompt)
                            print(f"Summary: {summary}")
                            await x.edit_text(f'{summary}')
                        except sr.RequestError:
                            print("API unavailable.")
                            await x.edit_text('API unavailable.')
                        except sr.UnknownValueError:
                            print("Unable to recognize speech.")
                            await x.edit_text('Unable to recognize speech.')
                except Exception as e:
                    print(f"Error during transcription: {str(e)}")
                    await x.edit_text(f'Error during transcription: {str(e)}')
                finally:
                    # Clean up files
                    if os.path.exists(output_file):
                        os.remove(output_file)
                        print(f"Deleted file: {output_file}")
                    if os.path.exists(wav_file):
                        os.remove(wav_file)
                        print(f"Deleted file: {wav_file}")
        except Exception as e:
            print(f"Error: {str(e)}")
            await x.edit_text(f'Error: {str(e)}')
    else:
        print("Invalid YouTube link.")
        await message.reply('Please send a valid YouTube link.')

async def main():
    await app.start()
    print("Bot is running...\nHit 🌟 on github repo if you liked my work and please follow on github for more such repos.")
    await idle()

if __name__ == '__main__':
    asyncio.run(main())
