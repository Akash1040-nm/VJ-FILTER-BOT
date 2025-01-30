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
    vj = await bot.ask(
        chat_id=message.from_user.id,
        text="Send me the files (photos, videos, audio, or documents) that you want to store. Send all at once."
    )

    # Allowed media types (including images)
    allowed_media_types = [
        enums.MessageMediaType.VIDEO,
        enums.MessageMediaType.AUDIO,
        enums.MessageMediaType.DOCUMENT,
        enums.MessageMediaType.PHOTO  # Now supports images/photos
    ]

    # Ensure that the message contains valid media
    if not vj.media_group_id and vj.media not in allowed_media_types:
        return await vj.reply("Please send only photos, videos, audio files, or documents.")

    # If multiple files are sent, fetch all messages in the media group
    messages = [vj]
    if vj.media_group_id:
        messages = await bot.get_media_group(vj.chat.id, vj.media_group_id)

    links = []  # List to store generated links

    for msg in messages:
        file_type = msg.media
        if file_type in allowed_media_types:
            file = getattr(msg, file_type.value)  # Get the actual file object
            file_id, ref = unpack_new_file_id(file.file_id)

            # Generate the link format
            string = 'filep_' if message.text.lower().strip() == "/plink" else 'file_'
            string += file_id
            outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")

            links.append(f"https://t.me/{temp.U_NAME}?start={outstr}")

    # Send the generated links in one message
    await message.reply("Here are your links:\n" + "\n".join(links))