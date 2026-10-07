import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from keyboards.navigation_buttons import build_main_keyboard

start_router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@start_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Ласкаво просимо до CS2 Items Management Bot, {message.from_user.full_name}!\n\n"
        f"Цей бот дозволяє вам переглядати предмети CS2, включаючи кейси, зброю та скіни.\n\n"
        f"Виберіть варіант:",
        reply_markup=build_main_keyboard()
    )

@start_router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "CS2 Items Management Bot\n\n"
        "Виберіть варіант:",
        reply_markup=build_main_keyboard()
    )
    await callback.answer()