import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from keyboards import start_keyboards, contact_keyboard, shaharlar_kb, oyliklar_kb, ruxsat_uchun
from states import DataState
from config import ADMIN_CHAT_ID, CHANNEL_ID, MY_TOKEN

API_TOKEN = MY_TOKEN 

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, proxy='http://proxy.server:3128')

dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])  
async def salom_ber(message: types.Message):
    await message.answer(text=f"""Assalom alaykum {message.from_user.full_name}
UstozShogird kanalining NOrasmiy botiga xush kelibsiz!

/help yordam buyrugi orqali nimalarga qodir ekanligimni bilib oling!""", reply_markup=start_keyboards)


@dp.message_handler(commands=['help'])
async def yordam_ber(message: types.Message):
    await message.answer(text="""/start - Botni ishga tushirish\n/help - Yordam""")


@dp.message_handler(text="Ish joyi kerak")
async def ish_joyi_kerak(message: types.Message, state: DataState):
    await message.answer(text="""👨‍💻 Ish joyi topish uchun ariza berish

Hozir sizga birnecha savollar beriladi. 
Har biriga javob bering. 
Oxirida agar hammasi to`g`ri bo`lsa, HA tugmasini bosing va arizangiz Adminga yuboriladi.""")
    await state.update_data(status="Ish joyi kerak")
    await message.answer(text="🔖 Ism va Familiyangizni kiriting:")
    await DataState.ism_familiya.set()


@dp.message_handler(state=DataState.ism_familiya)
async def ism_familiya(message: types.Message, state: DataState):
    await state.update_data(ism_familiya=message.text)
    await message.answer(text="🧑 Yoshingizni kiriting:")
    await DataState.yosh.set()


@dp.message_handler(state=DataState.yosh)
async def yosh(message: types.Message, state: DataState):
    await state.update_data(yosh=message.text)
    await message.answer(text="📱 Qaysi texnologiyalardan foydalanishingiz kerak? (Masalan: Python, Java, C++)" )
    await DataState.texnologiya.set()


@dp.message_handler(state=DataState.texnologiya)
async def texnologiya(message: types.Message, state: DataState):
    await state.update_data(texnologiya=message.text)
    await message.answer(text="📞 Telefon raqamni yuboring:", reply_markup=contact_keyboard)
    await DataState.telefon.set()


@dp.message_handler(state=DataState.telefon, content_types=types.ContentType.CONTACT)  # contact
async def telefon(message: types.Message, state: DataState):
    await state.update_data(telefon=message.contact.phone_number)
    await message.answer(text="📍 Hududingizni tanlang:", reply_markup=shaharlar_kb)
    await DataState.hudud.set()


@dp.message_handler(state=DataState.hudud)
async def hudud(message: types.Message, state: DataState):
    await state.update_data(hudud=message.text)
    await message.answer(text="💸 Narx kiriting:", reply_markup=oyliklar_kb)
    await DataState.narx.set() 


@dp.callback_query_handler(state=DataState.narx)
async def narx(call: types.CallbackQuery, state: DataState):
    oylik = call.data
    await state.update_data(narx=oylik)
    await call.message.answer(text="👨‍💼 Kasbingizni kiriting: (Ishlaysizmi yoki o`qiysizmi?)")
    await DataState.kasb.set()


@dp.message_handler(state=DataState.kasb)
async def kasb(message: types.Message, state: DataState):
    await state.update_data(kasb=message.text)
    await message.answer(text="📅 Murojaat vaqtingizni kiriting:")
    await DataState.murojat_vaqti.set()


@dp.message_handler(state=DataState.murojat_vaqti)
async def murojat_vaqti(message: types.Message, state: DataState):
    await state.update_data(murojat_vaqti=message.text)
    await message.answer(text="🎯 Maqsadingizni qisqacha yozib bering:")
    await DataState.maqsad.set()


malumotlar = ''

@dp.message_handler(state=DataState.maqsad)
async def maqsad(message: types.Message, state: DataState):
    await state.update_data(maqsad=message.text)
    await message.answer(text="🤔 Ma'lumotlar to'g'rimi? (Ha / Yo`q)")
    all_data = await state.get_data()
    username = message.from_user.username if message.from_user.username else "Yo'q"
    global malumotlar
    malumotlar = f"""📝 Ma'lumotlar:
👨‍💼 Xodim: {all_data['ism_familiya']}
🕑 Yosh: {all_data['yosh']}
📚 Texnologiya: {all_data['texnologiya']} 
🇺🇿 Telegram: @{username}
📞 Aloqa: {all_data['telefon']} 
🌐 Hudud: {all_data['hudud']}
💰 Narxi: {all_data['narx']}
👨🏻‍💻 Kasbi: {all_data['kasb']}
🕰 Murojaat qilish vaqti: {all_data['murojat_vaqti']} 
🔎 Maqsad: {all_data['maqsad']} 
"""
    await message.answer(text=malumotlar)
    await DataState.ha_yoq.set()


@dp.message_handler(state=DataState.ha_yoq)
async def ha_yoq(message: types.Message, state: DataState):
    if message.text.lower() == "ha":
        all_data = await state.get_data()
        global malumotlar
        await message.answer(text="✅ Arizangiz Adminga yuborildi.")
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=malumotlar, reply_markup=ruxsat_uchun)
    else:
        await message.answer(text="❌ Arizangiz bekor qilindi.")
    await state.finish()


@dp.callback_query_handler()
async def admin_confirm(call: types.CallbackQuery):
    admin = call.data
    global malumotlar
    if admin == 'yoq':
        malumotlar = ''
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text="Ariza o'chirildi")
        # await bot.send_message(chat_id=user_id)
    elif admin == 'ha':
        await bot.send_message(chat_id=CHANNEL_ID, text=malumotlar)  # malumotlarga qo'shib texnologiya heshteglari

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
