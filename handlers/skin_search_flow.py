import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database.skins_storage import get_all_weapons, get_weapon, get_weapon_skins
from database.cases_storage import get_case
from keyboards.weapon_selection_buttons import build_search_weapons_keyboard
from keyboards.navigation_buttons import build_main_keyboard

search_router = Router()

class UserStates(StatesGroup):
    search_skin_weapon = State()
    search_skin = State()

@search_router.callback_query(F.data == "search_skin")
async def start_skin_search(callback: CallbackQuery, state: FSMContext):
    weapons = await get_all_weapons()
    if weapons:
        await callback.message.edit_text(
            "🎨 Пошук скіна\n\n"
            "Спочатку виберіть зброю:",
            reply_markup=build_search_weapons_keyboard(weapons)
        )
        await state.set_state(UserStates.search_skin_weapon)
    else:
        await callback.message.edit_text(
            "⚠️ У базі даних немає зброї.",
            reply_markup=build_main_keyboard()
        )
        await state.clear()
    await callback.answer()

@search_router.callback_query(F.data.startswith("search_weapon_"))
async def select_weapon_for_search(callback: CallbackQuery, state: FSMContext):
    weapon_id = callback.data.split("_")[2]
    weapon = await get_weapon(weapon_id)
    if weapon:
        await state.update_data(weapon_id=weapon_id, weapon_name=weapon["weapon_name"])
        await callback.message.edit_text(
            f"🎨 Пошук скіна для {weapon['weapon_name']}\n\n"
            "Введіть назву скіна для пошуку (наприклад: 'Dragon Lore'):"
        )
        await state.set_state(UserStates.search_skin)
    else:
        await callback.message.edit_text(
            "⚠️ Зброю не знайдено.",
            reply_markup=build_main_keyboard()
        )
        await state.clear()
    await callback.answer()

@search_router.message(UserStates.search_skin)
async def process_skin_search(message: Message, state: FSMContext):
    search_term = message.text.strip().lower()
    if not search_term:
        await message.answer("⚠️ Будь ласка, введіть коректну назву скіна.")
        return

    data = await state.get_data()
    weapon_id = data.get("weapon_id")
    weapon_name = data.get("weapon_name")

    skins = await get_weapon_skins(weapon_id)
    matched_skins = [s for s in skins if search_term in s.get("skin_name", "").lower()]

    if not matched_skins:
        await message.answer(
            f"⚠️ Скінів за запитом '{search_term}' для {weapon_name} не знайдено.",
            reply_markup=build_main_keyboard()
        )
        await state.clear()
        return

    result = []
    for skin in matched_skins:
        stattrak = "StatTrak™ " if skin.get("stattrak") else ""
        souvenir = "Souvenir " if skin.get("souvenir") else ""
        skin_info = [
            f"🎨 Скін: {stattrak}{souvenir}{weapon_name} | {skin.get('skin_name')}",
            f"Рідкість: {skin.get('rarity') or 'Невідомо'}"
        ]

        wears = skin.get("wears", [])
        if wears:
            skin_info.append("\nТипи зносу:")
            for wear in wears:
                skin_info.append(f"• {wear.get('weartype')} (Float: {wear.get('floatmin')} - {wear.get('floatmax')})")

        case_ids = skin.get("cases", [])
        if case_ids:
            skin_info.append("\nМожна знайти в кейсах:")
            for cid in case_ids:
                c_data = await get_case(cid)
                if c_data:
                    skin_info.append(f"• {c_data.get('case_name')}")

        result.append("\n".join(skin_info))

    final_message = "\n\n".join(result)
    if len(final_message) > 4096:
        chunks = [final_message[i:i + 4096] for i in range(0, len(final_message), 4096)]
        for i, chunk in enumerate(chunks):
            if i == 0:
                await message.answer(chunk, reply_markup=build_main_keyboard())
            else:
                await message.answer(chunk)
    else:
        await message.answer(final_message, reply_markup=build_main_keyboard())

    await state.clear()