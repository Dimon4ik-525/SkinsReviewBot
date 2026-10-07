from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_weapons_keyboard(weapons: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for weapon in weapons:
        kb.button(
            text=f"{weapon['weapon_name']}",
            callback_data=f"weapon_{weapon['weapon_id']}"
        )
    kb.button(text="⬅️ Назад", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()

def build_weapon_skin_view_keyboard(weapon_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️️ Повернутись до зброї", callback_data="view_weapons")
    kb.button(text="🏠 Головне меню", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()

def build_search_weapons_keyboard(weapons: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for weapon in weapons:
        kb.button(
            text=f"{weapon['weapon_name']}",
            callback_data=f"search_weapon_{weapon['weapon_id']}"
        )
    kb.button(text="⬅️ Скасувати", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()