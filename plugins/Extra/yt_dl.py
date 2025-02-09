from __future__ import unicode_literals
import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pyrogram Client
app = Client(
    "YouTubeBot",
    api_id=os.environ.get("API_ID"),  # Replace with your API ID
    api_hash=os.environ.get("API_HASH"),  # Replace with your API HASH
    bot_token=os.environ.get("BOT_TOKEN")  # Replace with your Bot Token
)

# Song Downloader
@app.on_message(filters.command(['song', 'mp3']) & filters.private)
async def song_downloader(client, message: Message):
    logger.info(f"Received command: {message.text}")
    try:
        query = " ".join(message.command[1:])
        if not query:
            return await message.reply("❗ **Please provide a song name to search.**")

        progress = await message.reply("🔍 **Searching your song...**")
        
        # Search YouTube
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await progress.edit("❌ **No results found. Try different keywords.**")
            
        # Get song details
        song_data = results[0]
        youtube_url = f"https://youtube.com{song_data['url_suffix']}"
        title = song_data["title"][:40]
        thumbnail = song_data["thumbnails"][0]
        duration = song_data["duration"]

        # Download thumbnail
        thumb_file = f"{message.message_id}.jpg"
        with open(thumb_file, "wb") as thumb:
            thumb.write(requests.get(thumbnail).content)

        await progress.edit("⬇️ **Downloading your song...**")
        
        # Download audio
        ydl_opts = {
            "format": "bestaudio[ext=m4a]",
            "outtmpl": f"{title}.%(ext)s",
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a"
            }]
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            audio_file = ydl.prepare_filename(info).replace(".webm", ".m4a")

        # Send audio
        await progress.edit("📤 **Uploading your song...**")
        await message.reply_audio(
            audio=audio_file,
            duration=int(info["duration"]),
            performer="YouTube Music",
            title=info["title"],
            thumb=thumb_file,
            caption=f"🎵 **{info['title']}**\n\n➖➖➖➖➖➖➖\n⚡ **Powered By [VJ NETWORKS™](https://t.me/vj_bots)**"
        )
        await progress.delete()

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await progress.edit(f"❌ **Download Failed**\n`{str(e)}`")
    finally:
        # Cleanup
        files = [audio_file, thumb_file]
        for file in files:
            if file and os.path.exists(file):
                os.remove(file)

# Video Downloader
@app.on_message(filters.command(["video", "mp4"]))
async def video_downloader(client, message: Message):
    logger.info(f"Received command: {message.text}")
    try:
        query = " ".join(message.command[1:])
        if not query:
            return await message.reply("❗ **Please provide a video name to search.**")

        progress = await message.reply("🔍 **Searching your video...**")
        
        # Search YouTube
        search = SearchVideos(query, offset=1, mode="dict", max_results=1)
        result = search.result()
        if not result.get("search_result"):
            return await progress.edit("❌ **No results found. Try different keywords.**")
            
        video_data = result["search_result"][0]
        youtube_url = video_data["link"]
        title = video_data["title"]
        video_id = video_data["id"]

        # Download thumbnail
        thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        thumb_file = f"{message.message_id}.jpg"
        wget.download(thumb_url, thumb_file)

        await progress.edit("⬇️ **Downloading your video...**")
        
        # Download video
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "outtmpl": f"{title}.%(ext)s",
            "quiet": True
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_file = ydl.prepare_filename(info)

        # Send video
        await progress.edit("📤 **Uploading your video...**")
        await message.reply_video(
            video=video_file,
            duration=int(info["duration"]),
            thumb=thumb_file,
            caption=f"🎥 **{info['title']}**\n\n➖➖➖➖➖➖➖\n⚡ **Powered By [VJ NETWORKS™](https://t.me/vj_bots)**"
        )
        await progress.delete()

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await progress.edit(f"❌ **Download Failed**\n`{str(e)}`")
    finally:
        # Cleanup
        files = [video_file, thumb_file]
        for file in files:
            if file and os.path.exists(file):
                os.remove(file)

# Handle Raw YouTube Links
@app.on_message(filters.regex(r"https?://(www\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+"))
async def handle_youtube_link(client, message: Message):
    logger.info(f"Received YouTube link: {message.text}")
    try:
        youtube_url = message.text
        progress = await message.reply("🔍 **Processing your YouTube link...**")
        
        # Download video
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "outtmpl": "%(title)s.%(ext)s",
            "quiet": True
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            video_file = ydl.prepare_filename(info)

        # Send video
        await progress.edit("📤 **Uploading your video...**")
        await message.reply_video(
            video=video_file,
            caption=f"🎥 **{info['title']}**\n\n➖➖➖➖➖➖➖\n⚡ **Powered By [VJ NETWORKS™](https://t.me/vj_bots)**"
        )
        await progress.delete()

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await progress.edit(f"❌ **Download Failed**\n`{str(e)}`")
    finally:
        # Cleanup
        if os.path.exists(video_file):
            os.remove(video_file)

if __name__ == "__main__":
    logger.info("⚡ Bot Started!")
    app.run()