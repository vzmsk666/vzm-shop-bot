import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
BASE_WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: Message):
    await message.answer("Привет! Это VZM SHOP бот. Всё работает.")

async def on_startup(app):
    await bot.set_webhook(BASE_WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

app = web.Application()
setup_application(app, dp, bot, webhook_path=WEBHOOK_PATH)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, port=port)