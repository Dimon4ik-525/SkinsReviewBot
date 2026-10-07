from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_cases_keyboard(cases: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for case in cases:
        kb.button(
            text=f"{case['case_name']}",
            callback_data=f"case_{case['case_id']}"
        )
    kb.button(text="⬅️ Назад", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()

def build_case_skin_view_keyboard(case_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️️ Повернутись до кейсів", callback_data="view_cases")
    kb.button(text="🏠 Головне меню", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()