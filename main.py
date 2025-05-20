import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import setup_application
from aiogram.types import Message

# Получаем токен и адрес вебхука
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Обработчик сообщений
@dp.message()
async def echo_handler(message: Message):
    await message.answer("Привет! Это VZM SHOP бот — всё работает ✅")

# Webhook на старте
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

# Очистка при завершении
async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

# Настройка Aiohttp + Webhook
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
setup_application(app=app, dispatcher=dp, bot=bot, webhook_path=WEBHOOK_PATH)

# Запуск
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, port=port)

