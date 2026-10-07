import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.skins_storage import get_all_weapons, get_weapon, get_weapon_skins, get_all_skins
from keyboards.weapon_selection_buttons import build_weapons_keyboard, build_weapon_skin_view_keyboard
from keyboards.navigation_buttons import build_main_keyboard

weapon_router = Router()

@weapon_router.callback_query(F.data == "view_weapons")
async def show_weapons(callback: CallbackQuery):
    weapons = await get_all_weapons()
    if weapons:
        await callback.message.edit_text(
            "🔫 Доступна зброя:\n\n"
            "Виберіть зброю, щоб переглянути її скіни:",
            reply_markup=build_weapons_keyboard(weapons)
        )
    else:
        await callback.message.edit_text(
            "Зброю не знайдено.",
            reply_markup=build_main_keyboard()
        )
    await callback.answer()

@weapon_router.callback_query(F.data.startswith("weapon_"))
async def show_weapon_details(callback: CallbackQuery):
    weapon_id = callback.data.split("_")[1]
    weapon = await get_weapon(weapon_id)
    skins = await get_weapon_skins(weapon_id)

    if weapon:
        weapon_info = f"🔫 {weapon['weapon_name']}\n\n"

        if skins:
            weapon_info += "🎨 Доступні скіни:\n\n"
            current_rarity = None
            for skin in skins:
                rarity = skin.get("rarity")
                if rarity != current_rarity:
                    current_rarity = rarity
                    weapon_info += f"\n{current_rarity or 'Без рідкості'}:\n"

                special = []
                if skin.get("stattrak"):
                    special.append("StatTrak™")
                if skin.get("souvenir"):
                    special.append("Souvenir")

                special_text = f" ({', '.join(special)})" if special else ""
                weapon_info += f"• {skin.get('skin_name', '')}{special_text}\n"
        else:
            weapon_info += "Для цієї зброї немає скінів."

        await callback.message.edit_text(
            weapon_info,
            reply_markup=build_weapon_skin_view_keyboard(weapon_id)
        )
    else:
        await callback.message.edit_text(
            "Зброя не знайдена.",
            reply_markup=build_main_keyboard()
        )
    await callback.answer()

@weapon_router.callback_query(F.data == "view_skins")
async def show_all_skins(callback: CallbackQuery):
    skins = await get_all_skins()

    if skins:
        weapons_dict = {}
        for skin in skins:
            weapon_name = skin.get("weapon_name", "Невідома зброя")
            if weapon_name not in weapons_dict:
                weapons_dict[weapon_name] = []

            special = []
            if skin.get("stattrak"):
                special.append("StatTrak™")
            if skin.get("souvenir"):
                special.append("Souvenir")

            special_text = f" ({', '.join(special)})" if special else ""
            weapons_dict[weapon_name].append({
                "name": skin.get("skin_name", ""),
                "rarity": skin.get("rarity", "Невідомо"),
                "special": special_text
            })

        skins_info = "🎨 Усі доступні скіни:\n\n"
        for weapon, weapon_skins in sorted(weapons_dict.items()):
            skins_info += f"\n{weapon}:\n"
            rarity_dict = {}
            for skin in weapon_skins:
                rarity = skin["rarity"] or "Невідомо"
                rarity_dict.setdefault(rarity, []).append(f"• {skin['name']}{skin['special']}")

            for rarity in sorted(rarity_dict.keys()):
                skins_info += f"{rarity}:\n"
                skins_info += "\n".join(rarity_dict[rarity]) + "\n\n"

        if len(skins_info) > 4096:
            chunks = [skins_info[i:i + 4096] for i in range(0, len(skins_info), 4096)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await callback.message.edit_text(chunk, reply_markup=build_main_keyboard())
                else:
                    await callback.message.answer(chunk)
        else:
            await callback.message.edit_text(skins_info, reply_markup=build_main_keyboard())
    else:
        await callback.message.edit_text(
            "У базі даних не знайдено скінів.",
            reply_markup=build_main_keyboard()
        )
    await callback.answer()