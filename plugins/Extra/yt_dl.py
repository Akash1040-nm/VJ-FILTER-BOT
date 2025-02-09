import os
import asyncio
import requests
from pyrogram import filters, Client
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL

@Client.on_message(filters.command(['song', 'mp3']) & filters.private)
async def song(client, message):
    user_id = message.from_user.id 
    user_name = message.from_user.first_name 
    rpk = f"[{user_name}](tg://user?id={str(user_id)})"
    query = ' '.join(message.command[1:])
    
    if not query:
        return await message.reply("Please provide a song name to search.")
    
    m = await message.reply(f"**Searching your song...!\n {query}**")
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await m.edit("No results found.")
        
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]       
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f'thumb{title}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)
        
        performer = "[VJ NETWORKS™]" 
        duration = results[0]["duration"]
        
        await m.edit("**Downloading your song...!**")
        
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        
        cap = "**BY›› [VJ NETWORKS™](https://t.me/vj_bots)**"
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        
        await message.reply_audio(
            audio_file,
            caption=cap,            
            quote=False,
            title=title,
            duration=dur,
            performer=performer,
            thumb=thumb_name
        )            
        await m.delete()
        
    except Exception as e:
        await m.edit("**🚫 ERROR 🚫**")
        print(e)
    
    finally:
        try:
            os.remove(audio_file)
            os.remove(thumb_name)
        except Exception as e:
            print(e)

@Client.on_message(filters.command(["video", "mp4"]))
async def vsong(client, message: Message):
    urlissed = ' '.join(message.command[1:])
    if not urlissed:
        return await message.reply("Please provide a video name to search.")
    
    pablo = await client.send_message(message.chat.id, f"**FINDING YOUR VIDEO** `{urlissed}`")
    
    try:
        search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
        mi = search.result()
        mio = mi["search_result"]
        if not mio:
            return await pablo.edit("No results found.")
        
        mo = mio[0]["link"]
        thum = mio[0]["title"]
        fridayz = mio[0]["id"]
        kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
        
        await asyncio.sleep(0.6)
        sedlyf = wget.download(kekme)
        
        opts = {
            "format": "best",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
            "outtmpl": "%(id)s.mp4",
            "logtostderr": False,
            "quiet": True,
        }
        
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(mo, download=True)
        
        file_stark = f"{ytdl_data['id']}.mp4"
        capy = f"""**TITLE :** [{thum}]({mo})\n**REQUESTED BY :** {message.from_user.mention}"""
        
        await client.send_video(
            message.chat.id,
            video=open(file_stark, "rb"),
            duration=int(ytdl_data["duration"]),
            file_name=str(ytdl_data["title"]),
            thumb=sedlyf,
            caption=capy,
            supports_streaming=True,        
            reply_to_message_id=message.id 
        )
        await pablo.delete()
        
    except Exception as e:
        await pablo.edit_text(f"**Download Failed Please Try Again..♥️** \n**Error :** `{str(e)}`")
    
    finally:
        for files in (sedlyf, file_stark):
            if files and os.path.exists(files):
                os.remove(files)