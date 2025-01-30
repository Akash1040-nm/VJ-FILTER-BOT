import re, os, json, base64, logging
from utils import temp
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from info import ADMINS, LOG_CHANNEL, FILE_STORE_CHANNEL, PUBLIC_FILE_STORE
from database.ia_filterdb import unpack_new_file_id

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Function to check if user is allowed to generate links
async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

# Command to generate links for multiple files & images
@Client.on_message(filters.command(['link', 'plink']) & filters.create(allowed))
async def gen_link_s(bot, message):
    await message.reply("📩 **Send me the files (photos, videos, audio, or documents) that you want to store. Send all at once.**")

    # Listen for next messages from user
    collected_messages = []
    while True:
        vj = await bot.listen(message.chat.id, timeout=30)  # Wait for 30 seconds
        if vj.text and vj.text.lower() == "done":
            break  # Stop listening if user sends "done"
        if vj.media:
            collected_messages.append(vj)

    if not collected_messages:
        return await message.reply("⚠ **No media files were received. Please send valid files.**")

    # Allowed media types (including images)
    allowed_media_types = [
        enums.MessageMediaType.VIDEO,
        enums.MessageMediaType.AUDIO,
        enums.MessageMediaType.DOCUMENT,
        enums.MessageMediaType.PHOTO  # Now supports images/photos
    ]

    links = []  # List to store generated links

    for msg in collected_messages:
        file_type = msg.media
        if file_type in allowed_media_types:
            file = getattr(msg, file_type.value)  # Get the actual file object
            
            # Extract file_id properly for each file
            file_id, ref = unpack_new_file_id(file.file_id)

            # Generate the link format
            string = 'filep_' if message.text.lower().strip() == "/plink" else 'file_'
            string += file_id
            outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")

            # Handle missing `file_name` for images
            file_name = getattr(file, "file_name", "Photo" if file_type == enums.MessageMediaType.PHOTO else "File")

            # Append generated link to the list
            links.append(f"📂 **{file_name}**\n🔗 [Click Here](https://t.me/{temp.U_NAME}?start={outstr})\n")

    # Send all generated links in one message
    await message.reply("✅ **Here are your generated links:**\n\n" + "\n".join(links), disable_web_page_preview=True)