from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_admin_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Керування кейсами", callback_data="admin_cases")
    kb.button(text="Керування зброєю", callback_data="admin_weapons")
    kb.button(text="Керування скінами", callback_data="admin_skins")
    kb.button(text="Кейс-Скін зв'язок", callback_data="admin_caseskins")
    kb.button(text="⬅️ Повернутись в меню", callback_data="main_menu")
    kb.adjust(2, 2, 1)
    return kb.as_markup()

def build_admin_cases_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Додати кейс", callback_data="add_case")
    kb.button(text="✏️ Редагувати кейс", callback_data="edit_case")
    kb.button(text="🗑️ Видалити кейс", callback_data="delete_case")
    kb.button(text="⬅️ Назад", callback_data="admin_menu")
    kb.adjust(2, 2)
    return kb.as_markup()

def build_admin_weapons_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Додати зброю", callback_data="add_weapon")
    kb.button(text="✏️ Редагувати зброю", callback_data="edit_weapon")
    kb.button(text="🗑️ Видалити зброю", callback_data="delete_weapon")
    kb.button(text="⬅️ Назад", callback_data="admin_menu")
    kb.adjust(2, 2)
    return kb.as_markup()

def build_admin_skins_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Додати скін", callback_data="add_skin")
    kb.button(text="✏️ Редагувати скін", callback_data="edit_skin")
    kb.button(text="🗑️ Видалити скін", callback_data="delete_skin")
    kb.button(text="➕ Додати Skin Wear", callback_data="add_skinwear")
    kb.button(text="⬅️ Назад", callback_data="admin_menu")
    kb.adjust(2, 2)
    return kb.as_markup()

def build_admin_caseskins_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Додати скін до кейса", callback_data="add_caseskin")
    kb.button(text="➖ Видалити скін з кейса", callback_data="remove_caseskin")
    kb.button(text="⬅️ Назад", callback_data="admin_menu")
    kb.adjust(1)
    return kb.as_markup()

def build_select_case_keyboard(cases: List[Dict[str, Any]], action_prefix: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for case in cases:
        kb.button(text=f"{case['case_name']}", callback_data=f"{action_prefix}_{case['case_id']}")
    kb.button(text="⬅️ Скасувати", callback_data="admin_menu")
    kb.adjust(1)
    return kb.as_markup()

def build_select_weapon_keyboard(weapons: List[Dict[str, Any]], action_prefix: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for weapon in weapons:
        kb.button(text=f"{weapon['weapon_name']}", callback_data=f"{action_prefix}_{weapon['weapon_id']}")
    kb.button(text="⬅️ Скасувати", callback_data="admin_menu")
    kb.adjust(1)
    return kb.as_markup()

def build_select_skin_keyboard(skins: List[Dict[str, Any]], action_prefix: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for skin in skins:
        kb.button(
            text=f"{skin.get('weapon_name', '')} | {skin.get('skin_name', '')}",
            callback_data=f"{action_prefix}_{skin['skin_id']}"
        )
    kb.button(text="⬅️ Скасувати", callback_data="admin_menu")
    kb.adjust(1)
    return kb.as_markup()

def build_edit_skin_fields_keyboard(skin_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Назва", callback_data=f"edit_skin_field_{skin_id}_skin_name")
    kb.button(text="Rarity", callback_data=f"edit_skin_field_{skin_id}_rarity")
    kb.button(text="StatTrak", callback_data=f"edit_skin_field_{skin_id}_stattrak")
    kb.button(text="Souvenir", callback_data=f"edit_skin_field_{skin_id}_souvenir")
    kb.button(text="Image URL", callback_data=f"edit_skin_field_{skin_id}_image_skin")
    kb.button(text="⬅️ Скасувати", callback_data="admin_menu")
    kb.adjust(2, 2, 1, 1)
    return kb.as_markup()

def build_wear_types_keyboard(skin_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    wear_types = ["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]
    for wear in wear_types:
        kb.button(text=wear, callback_data=f"wear_type_{skin_id}_{wear}")
    kb.button(text="⬅️ Скасувати", callback_data="admin_menu")
    kb.adjust(1)
    return kb.as_markup()