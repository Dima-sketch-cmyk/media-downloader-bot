import os
import re
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def download_media(url: str):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "👋 **Привет! Я бот для скачивания видео.**\n\n"
        "🎬 Отправь мне ссылку на видео из **TikTok** или **YouTube**, и я пришлю его тебе!"
    )

@dp.message(F.text.regexp(r'https?://[^\s]+'))
async def handle_link(message: Message):
    url = message.text.strip()
    status_msg = await message.answer("⏳ Скачиваю видео, подожди немного...")
    
    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, download_media, url)
        
        await message.answer_video(video=open(file_path, 'rb'), caption="✅ Ваше видео готово!")
        await status_msg.delete()
        
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        await status_msg.edit_text("❌ Не удалось скачать видео. Проверь ссылку или попробуй позже.")

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
