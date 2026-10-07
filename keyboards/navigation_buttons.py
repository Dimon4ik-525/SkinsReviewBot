from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_main_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Кейси", callback_data="view_cases")
    kb.button(text="Зброя", callback_data="view_weapons")
    kb.button(text="Всі скіни", callback_data="view_skins")
    kb.button(text="Пошук скіна", callback_data="search_skin")
    kb.adjust(2)
    return kb.as_markup()

def build_cancel_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Скасувати", callback_data="admin_menu")
    kb.adjust(1)
    return kb.as_markup()

def build_confirm_keyboard(action: str, item_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Так", callback_data=f"confirm_{action}_{item_id}")
    kb.button(text="❌ Ні", callback_data="admin_menu")
    kb.adjust(2)
    return kb.as_markup()