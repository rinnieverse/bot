import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# 🔑 Встав свій токен 
BOT_TOKEN = "8629820470:AAEsWdQzWEN0OZ5EI5k_c4SZa-qCBTDxi60"

# 🔹 Встав свій Telegram ID
ADMIN_ID = 8580601018

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

users = {}

class Form(StatesGroup):
    waiting_for_nickname = State()

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ввести таємне ім'я")],
        [KeyboardButton(text="Залишитися анонімним")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Обери, як ти хочеш відображатися в боті:",
        reply_markup=start_kb
    )

@dp.message(F.text == "Ввести таємне ім'я")
async def choose_nickname(message: Message, state: FSMContext):
    await message.answer("Напиши свій псевдонім:")
    await state.set_state(Form.waiting_for_nickname)

@dp.message(Form.waiting_for_nickname)
async def save_nickname(message: Message, state: FSMContext):
    users[message.from_user.id] = message.text
    await message.answer(
        f"Готово! Твій псевдонім: {message.text}. Тепер ти можеш писати сюди пльотки.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

@dp.message(F.text == "Залишитися анонімним")
async def anonymous(message: Message):
    users[message.from_user.id] = None
    await message.answer(
        "Ти залишаєшся повністю анонімним 🕶",
        reply_markup=ReplyKeyboardRemove()
    )

# ТЕКСТ
@dp.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == Form.waiting_for_nickname.state:
        return

    nickname = users.get(message.from_user.id)

    if nickname:
        text_to_send = f"Повідомлення від {nickname}:\n{message.text}"
    else:
        text_to_send = f"Анонімне повідомлення:\n{message.text}"

    await bot.send_message(ADMIN_ID, text_to_send)
    await message.answer("Плітку відправлено 📨")

# ФОТО
@dp.message(F.photo)
async def handle_photo(message: Message):
    nickname = users.get(message.from_user.id)

    if nickname:
        caption = f"Фото від {nickname} 📸"
    else:
        caption = "Анонімне фото 📸"

    await bot.send_photo(
        ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=caption
    )

    await message.answer("Плітку відправлено 📨")

# ВІДЕО
@dp.message(F.video)
async def handle_video(message: Message):
    nickname = users.get(message.from_user.id)

    if nickname:
        caption = f"Відео від {nickname} 🎬"
    else:
        caption = "Анонімне відео 🎬"

    await bot.send_video(
        ADMIN_ID,
        video=message.video.file_id,
        caption=caption
    )

    await message.answer("Плітку відправлено 📨")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
