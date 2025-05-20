import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
import sqlite3
import config

# --- FSM ---
class Order(StatesGroup):
    platform = State()
    login = State()
    password = State()
    wait_for_payment = State()
    wait_for_check = State()

# --- База данных ---
def init_db():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            credits INTEGER,
            price INTEGER,
            platform TEXT,
            login TEXT,
            password TEXT,
            status TEXT DEFAULT 'waiting'
        )''')
        conn.commit()

# --- Запуск ---
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

# --- Старт ---
@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="500 кр - 450₽", callback_data="credits_500")
    kb.button(text="1100 кр - 800₽", callback_data="credits_1100")
    kb.button(text="3000 кр - 1800₽", callback_data="credits_3000")
    kb.button(text="6500 кр - 3600₽", callback_data="credits_6500")
    kb.adjust(2)
    await message.answer("Привет! Выбери нужное количество кредитов:", reply_markup=kb.as_markup())

# --- Выбор тарифа ---
@dp.callback_query(F.data.startswith("credits_"))
async def choose_credits(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("_")
    credits_map = {
        "500": 450,
        "1100": 800,
        "3000": 1800,
        "6500": 3600,
    }
    credits = int(data[1])
    price = credits_map[str(credits)]
    await state.update_data(credits=credits, price=price)
    await callback.message.answer(f"Ты выбрал {credits} кредитов за {price}₽\nУкажи платформу (Epic, Steam, PS, Xbox):")
    await state.set_state(Order.platform)

@dp.message(Order.platform)
async def get_platform(message: Message, state: FSMContext):
    await state.update_data(platform=message.text.strip())
    await message.answer("Отправь логин от аккаунта:")
    await state.set_state(Order.login)

@dp.message(Order.login)
async def get_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text.strip())
    await message.answer("Теперь отправь пароль:")
    await state.set_state(Order.password)

@dp.message(Order.password)
async def get_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text.strip())
    data = await state.get_data()
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO orders (user_id, username, credits, price, platform, login, password) VALUES (?, ?, ?, ?, ?, ?, ?)", (
            message.from_user.id,
            message.from_user.username,
            data['credits'],
            data['price'],
            data['platform'],
            data['login'],
            data['password'],
        ))
        order_id = c.lastrowid
        conn.commit()
    await message.answer(
        f"🔔 Переведите <b>{data['price']}₽</b> на карту: <code>2204 2401 7179 1066</code>\n"
        f"💬 В комментарии укажите: <b>#{order_id:04}</b>\n"
        f"📷 После оплаты отправьте скриншот сюда."
    )
    await state.update_data(order_id=order_id)
    await state.set_state(Order.wait_for_check)

@dp.message(Order.wait_for_check, F.photo)
async def get_payment_check(message: Message, state: FSMContext):
    data = await state.get_data()
    admin_id = config.OPERATOR_ID
    caption = (
        f"🆕 Новый заказ #{data['order_id']:04}\n\n"
        f"👤 Пользователь: @{message.from_user.username}\n"
        f"💳 Кредитов: {data['credits']}\n💰 Цена: {data['price']}₽\n"
        f"🕹 Платформа: {data['platform']}\n🔑 Логин: {data['login']}\n🔐 Пароль: {data['password']}\n"
    )
    photo_id = message.photo[-1].file_id
    await bot.send_photo(admin_id, photo_id, caption=caption)
    await message.answer("✅ Скрин отправлен оператору. Ожидайте подтверждение.")
    await state.clear()

# --- Запуск ---
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())