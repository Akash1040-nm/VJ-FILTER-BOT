import re, os, json, base64, logging
from utils import temp
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from info import ADMINS, LOG_CHANNEL, FILE_STORE_CHANNEL, PUBLIC_FILE_STORE
from database.ia_filterdb import unpack_new_file_id

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Allowed function to check if the user is allowed to generate links
async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

# Command to generate single file link
@Client.on_message(filters.command(['link', 'plink']) & filters.create(allowed))
async def gen_link_s(bot, message):
    vj = await bot.ask(chat_id=message.from_user.id, text="Now Send Me Your Message Which You Want To Store.")
    file_type = vj.media
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        return await vj.reply("Send me only video, audio, file, or document.")
    if message.has_protected_content and message.chat.id not in ADMINS:
        return await message.reply("okDa")
    file_id, ref = unpack_new_file_id((getattr(vj, file_type.value)).file_id)
    string = 'filep_' if message.text.lower().strip() == "/plink" else 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    await message.reply(f"Here is your Link:\nhttps://t.me/{temp.U_NAME}?start={outstr}")

# Command to generate batch link for multiple files
@Client.on_message(filters.command(['batch', 'pbatch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    if " " not in message.text:
        return await message.reply("Use correct format.\nExample <code>/batch https://t.me/rk_movies8/9 https://t.me/RK_Movies8/85</code>.")

    links = message.text.strip().split(" ")  # Split message to get all links
    if len(links) < 2:  # Ensure at least 2 links are provided
        return await message.reply("Use correct format.\nExample <code>/batch https://t.me/rk_movies8/9 https://t.me/rk_movies8/94</code>.")

    cmd = links[0]  # Command (either 'batch' or 'pbatch')
    file_links = links[1:]  # Extract the actual links

    all_file_ids = []

    regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")

    # Validate and process each link
    for link in file_links:
        match = regex.match(link)
        if not match:
            return await message.reply(f"Invalid link: {link}")

        chat_id = match.group(4)
        msg_id = int(match.group(5))

        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)

        try:
            msg = await bot.get_messages(chat_id, msg_id)
            if not msg.media:
                continue  # Skip if no media in the message
            
            file_type = msg.media
            file = getattr(msg, file_type.value)
            caption = getattr(msg, "caption", "")

            file_data = {
                "file_id": file.file_id,
                "caption": caption,
                "title": getattr(file, "file_name", ""),
                "size": file.file_size,
                "protect": cmd.lower().strip() == "/pbatch",
            }

            all_file_ids.append(file_data)

        except Exception as e:
            return await message.reply(f"Error processing {link}: {e}")

    # Save the list of files to JSON
    with open(f"batchmode_{message.from_user.id}.json", "w+") as out:
        json.dump(all_file_ids, out)

    # Send the file to LOG_CHANNEL
    post = await bot.send_document(LOG_CHANNEL, f"batchmode_{message.from_user.id}.json", file_name="Batch.json", caption="⚠️Generated for filestore.")
    os.remove(f"batchmode_{message.from_user.id}.json")

    # Generate a batch link for all files
    file_id, ref = unpack_new_file_id(post.document.file_id)
    await message.reply(f"Here is your link\nContains `{len(all_file_ids)}` files.\n https://t.me/{temp.U_NAME}?start=BATCH-{file_id}")