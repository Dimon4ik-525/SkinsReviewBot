import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.cases_storage import get_all_cases, get_case, get_case_skins
from keyboards.case_selection_buttons import build_cases_keyboard, build_case_skin_view_keyboard
from keyboards.navigation_buttons import build_main_keyboard

case_router = Router()

@case_router.callback_query(F.data == "view_cases")
async def show_cases(callback: CallbackQuery):
    cases = await get_all_cases()
    if cases:
        await callback.message.edit_text(
            "📦 Доступні кейси:\n\n"
            "Виберіть кейс, щоб переглянути його скіни:",
            reply_markup=build_cases_keyboard(cases)
        )
    else:
        await callback.message.edit_text(
            "Кейсів не знайдено.",
            reply_markup=build_main_keyboard()
        )
    await callback.answer()

@case_router.callback_query(F.data.startswith("case_"))
async def show_case_details(callback: CallbackQuery):
    case_id = callback.data.split("_")[1]
    case = await get_case(case_id)
    skins = await get_case_skins(case_id)

    if case:
        case_info = f"📦 {case['case_name']}\n\n"

        if skins:
            case_info += "🎨 Скіни в цьому кейсі:\n\n"
            current_rarity = None
            for skin in skins:
                rarity = skin.get("rarity")
                if rarity != current_rarity:
                    current_rarity = rarity
                    case_info += f"\n{current_rarity or 'Без рідкості'}:\n"

                special = []
                if skin.get("stattrak"):
                    special.append("StatTrak™")
                if skin.get("souvenir"):
                    special.append("Souvenir")

                special_text = f" ({', '.join(special)})" if special else ""
                case_info += f"• {skin.get('weapon_name', '')} | {skin.get('skin_name', '')}{special_text}\n"
        else:
            case_info += "В цьому кейсі немає скінів."

        await callback.message.edit_text(
            case_info,
            reply_markup=build_case_skin_view_keyboard(case_id)
        )
    else:
        await callback.message.edit_text(
            "Кейс не знайдено.",
            reply_markup=build_main_keyboard()
        )
    await callback.answer()