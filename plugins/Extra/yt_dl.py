from __future__ import unicode_literals

import os
import requests
import asyncio
import re
from pyrogram import filters, Client
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL


# Function to sanitize filenames
def safe_filename(title):
    return re.sub(r'[^A-Za-z0-9]+', '_', title)[:20]


# Song Downloader Handler
@Client.on_message(filters.command(['song', 'mp3']) & filters.private)
async def song(client, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("Example: `/song vaa vaathi song`")

    m = await message.reply(f"**Searching for your song... 🎵\n{query}**")

    try:
        # Searching for the song
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await m.edit("🚫 No results found. Try another song!")

        # Extracting video details
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = safe_filename(results[0]['title'])
        duration = results[0]['duration']
        thumbnail_url = results[0]['thumbnails'][0]

        # Downloading the thumbnail
        thumb_name = f"thumb_{title}.jpg"
        thumb_data = requests.get(thumbnail_url).content
        with open(thumb_name, "wb") as thumb_file:
            thumb_file.write(thumb_data)

    except Exception as e:
        return await m.edit(f"🚫 Error in search: `{str(e)}`")

    await m.edit("**Downloading your song... ⏳**")

    try:
        # Downloading the audio
        ydl_opts = {"format": "bestaudio/best", "outtmpl": f"{title}.m4a"}
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            audio_file = f"{info_dict['id']}.m4a"

        # Converting duration to seconds
        dur = sum(int(x) * (60 ** i) for i, x in enumerate(reversed(duration.split(":"))))

        # Sending the audio
        caption = "**🎵 Song Downloaded by VJ NETWORKS™**"
        await message.reply_audio(
            audio_file,
            caption=caption,
            title=title,
            duration=dur,
            performer="VJ NETWORKS™",
            thumb=thumb_name
        )

        await m.delete()

    except Exception as e:
        return await m.edit(f"🚫 Error: `{str(e)}`")

    finally:
        # Cleaning up temporary files
        for file in [audio_file, thumb_name]:
            if os.path.exists(file):
                os.remove(file)


# Function to extract text after command
def get_text(message: Message):
    if message.text and " " in message.text:
        return message.text.split(None, 1)[1]
    return None


# Video Downloader Handler
@Client.on_message(filters.command(["video", "mp4"]) & filters.private)
async def vsong(client, message: Message):
    query = get_text(message)
    if not query:
        return await message.reply("Example: `/video <video name>`")

    m = await message.reply(f"**Searching for your video... 🎥\n{query}**")

    try:
        # Searching for the video
        search = SearchVideos(query, offset=1, mode="dict", max_results=1)
        results = search.result()["search_result"]
        if not results:
            return await m.edit("🚫 No video found. Try another search!")

        # Extracting video details
        video_url = results[0]["link"]
        video_title = safe_filename(results[0]["title"])
        video_id = results[0]["id"]
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

        # Downloading the thumbnail
        thumb_name = f"thumb_{video_title}.jpg"
        thumb_data = requests.get(thumbnail_url).content
        with open(thumb_name, "wb") as thumb_file:
            thumb_file.write(thumb_data)

    except Exception as e:
        return await m.edit(f"🚫 Error in search: `{str(e)}`")

    await m.edit("**Downloading your video... ⏳**")

    try:
        # Downloading the video
        ydl_opts = {
            "format": "best",
            "outtmpl": f"{video_id}.mp4",
            "quiet": True,
        }
        with YoutubeDL(ydl_opts) as ytdl:
            ytdl_data = ytdl.extract_info(video_url, download=True)

        video_file = f"{ytdl_data['id']}.mp4"

        # Checking file size before uploading
        file_size = os.path.getsize(video_file) / (1024 * 1024)
        if file_size > 2000:  # 2GB limit
            return await message.reply("🚫 The video is too large to upload on Telegram.")

        # Sending the video
        caption = f"**🎥 Title:** [{video_title}]({video_url})\n**Requested by:** {message.from_user.mention}"
        await client.send_video(
            message.chat.id,
            video=open(video_file, "rb"),
            duration=int(ytdl_data["duration"]),
            file_name=str(ytdl_data["title"]),
            thumb=thumb_name,
            caption=caption,
            supports_streaming=True,
            reply_to_message_id=message.id
        )

        await m.delete()

    except Exception as e:
        return await m.edit(f"🚫 Download Failed. Error: `{str(e)}`")

    finally:
        # Cleaning up temporary files
        for file in [video_file, thumb_name]:
            if os.path.exists(file):
                os.remove(file)