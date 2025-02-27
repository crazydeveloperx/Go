import os
import asyncio
import requests
from dotenv import load_dotenv
from gofile import uploadFile
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID", 25069425))
API_HASH = os.getenv("API_HASH", "41034e257e6449615faea5f18bbe1dd7")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7204693012:AAE3BsJPhgTm4K__kbV_IfHlsBpkrF-tbg0")

# Initialize bot client
Bot = Client(
    "GoFile-Bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
)

INSTRUCTIONS = """
I am a GoFile uploader Telegram bot. 
You can upload files to gofile.io with the following commands:

With media:
    Normal:
        `/upload`
    With token:
        `/upload token`
    With folder ID:
        `/upload token folderid`

Using Link:
    Normal:
        `/upload url`
    With token:
        `/upload url token`
    With folder ID:
        `/upload url token folderid`
"""

@Bot.on_message(filters.private & filters.command("start"))
async def start(bot, update):
    await update.reply_text(
        text=f"Hello {update.from_user.mention},\n\n{INSTRUCTIONS}",
        disable_web_page_preview=True,
        quote=True,
    )

@Bot.on_message(filters.private & filters.command("upload"))
async def upload_handler(_, update):
    message = await update.reply_text("`Processing...`", quote=True)

    text = update.text.replace("\n", " ")
    url, token, folderId = None, None, None

    if " " in text:
        text = text.split(" ", 1)[1]
        if update.reply_to_message:
            parts = text.split()
            token = parts[0] if len(parts) > 0 else None
            folderId = parts[1] if len(parts) > 1 else None
        else:
            parts = text.split()
            url = parts[0]
            token = parts[1] if len(parts) > 1 else None
            folderId = parts[2] if len(parts) > 2 else None

            if not (url.startswith("http://") or url.startswith("https://")):
                await message.edit_text("Error: `Invalid URL`")
                return
    elif not update.reply_to_message:
        await message.edit_text("Error: `No media or URL found`")
        return

    try:
        await message.edit_text("`Downloading...`")
        if url:
            response = requests.get(url)
            media = url.split("/")[-1]
            with open(media, "wb") as file:
                file.write(response.content)
        else:
            media = await update.reply_to_message.download()

        await message.edit_text("`Download complete. Uploading...`")
        response = uploadFile(file_path=media, token=token, folderId=folderId)
        await message.edit_text("`Upload successful!`")

        os.remove(media)

    except Exception as error:
        await message.edit_text(f"Error: `{error}`")
        return

    text = (
        f"**File Name:** `{response['name']}`\n"
        f"**File ID:** `{response['id']}`\n"
        f"**Parent Folder Code:** `{response['parentFolderCode']}`\n"
        f"**Guest Token:** `{response['guestToken']}`\n"
        f"**MD5:** `{response['md5']}`\n"
        f"**Download Page:** `{response['downloadPage']}`"
    )
    link = response["downloadPage"]
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Open Link", url=link),
         InlineKeyboardButton(text="Share Link", url=f"https://telegram.me/share/url?url={link}")],
        [InlineKeyboardButton(text="Feedback", url="https://telegram.me/FayasNoushad")]
    ])
    
    await message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)


if __name__ == "__main__":
   # asyncio.run(send_restart_message())
    print("Bot is started working!")
    Bot.run()
