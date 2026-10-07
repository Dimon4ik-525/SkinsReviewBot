import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_IDS
from keyboards.admin_buttons import (
    build_admin_keyboard,
    build_admin_cases_keyboard,
    build_admin_weapons_keyboard,
    build_admin_skins_keyboard,
    build_admin_caseskins_keyboard,
    build_select_case_keyboard,
    build_select_weapon_keyboard,
    build_select_skin_keyboard,
    build_edit_skin_fields_keyboard,
    build_wear_types_keyboard
)
from keyboards.navigation_buttons import build_main_keyboard, build_confirm_keyboard, build_cancel_keyboard
from database.cases_storage import (
    get_all_cases, get_case, add_case_to_db, update_case, delete_case,
    get_case_skins, add_skin_to_case, remove_skin_from_case
)
from database.skins_storage import (
    get_all_weapons, get_weapon, add_weapon_to_db, update_weapon, delete_weapon,
    get_all_skins, get_skin, add_skin_to_db, update_skin, delete_skin, add_skinwear_to_db
)

admin_router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

class AdminStates(StatesGroup):
    add_case = State()
    edit_case_select = State()
    edit_case_name = State()
    edit_case_image = State()
    delete_case_confirm = State()

    add_weapon = State()
    edit_weapon_select = State()
    edit_weapon_name = State()
    delete_weapon_confirm = State()

    add_skin_weapon = State()
    add_skin_name = State()
    add_skin_rarity = State()
    add_skin_stattrak = State()
    add_skin_souvenir = State()
    add_skin_image = State()
    edit_skin_select = State()
    edit_skin_value = State()
    delete_skin_confirm = State()

    add_skinwear_skin = State()
    add_skinwear_weartype = State()
    add_skinwear_floatmin = State()
    add_skinwear_floatmax = State()

    add_caseskin_case = State()
    add_caseskin_skin = State()
    remove_caseskin = State()
    remove_caseskin_confirm = State()

# --- МЕНЮ АДМІНА ---

@admin_router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    if is_admin(message.from_user.id):
        await message.answer(
            f"Ласкаво просимо до панелі адміністратора, {message.from_user.full_name}!\n\n"
            "Тут ви можете керувати елементами CS2 у базі даних:\n",
            reply_markup=build_admin_keyboard()
        )
    else:
        await message.answer("У вас немає дозволу на доступ до панелі адміністратора.")

@admin_router.callback_query(F.data == "admin_menu")
async def show_admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if is_admin(callback.from_user.id):
        await callback.message.edit_text("Панель адміна\n\nВиберіть варіант:", reply_markup=build_admin_keyboard())
    else:
        await callback.message.edit_text("Немає доступу.", reply_markup=build_main_keyboard())
    await callback.answer()

# --- РОЗДІЛИ УПРАВЛІННЯ ---

@admin_router.callback_query(F.data == "admin_cases")
async def admin_cases(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if is_admin(callback.from_user.id):
        await callback.message.edit_text("📦 Управління кейсами\n\nВиберіть дію:", reply_markup=build_admin_cases_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "admin_weapons")
async def admin_weapons(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if is_admin(callback.from_user.id):
        await callback.message.edit_text("🔫 Управління зброєю\n\nВиберіть дію:", reply_markup=build_admin_weapons_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "admin_skins")
async def admin_skins(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if is_admin(callback.from_user.id):
        await callback.message.edit_text("🎨 Управління скінами\n\nВиберіть дію:", reply_markup=build_admin_skins_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "admin_caseskins")
async def admin_caseskins(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if is_admin(callback.from_user.id):
        await callback.message.edit_text("🔄 Управління зв'язками Case-Skin\n\nВиберіть дію:", reply_markup=build_admin_caseskins_keyboard())
    await callback.answer()

# --- КЕРУВАННЯ КЕЙСАМИ ---

@admin_router.callback_query(F.data == "add_case")
async def add_case_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.add_case)
    await callback.message.edit_text(
        "📦 Додавання нового кейсу\n\nВведіть назву кейсу:",
        reply_markup=build_cancel_keyboard()
    )
    await callback.answer()

@admin_router.message(AdminStates.add_case)
async def process_add_case_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("⚠️ Назва кейсу не може бути пустою. Введіть назву:")
        return
    await add_case_to_db(name)
    await state.clear()
    await message.answer(f"✅ Кейс '{name}' успішно додано!", reply_markup=build_admin_cases_keyboard())

@admin_router.callback_query(F.data == "edit_case")
async def edit_case_list(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    cases = await get_all_cases()
    if cases:
        await state.set_state(AdminStates.edit_case_select)
        await callback.message.edit_text(
            "✏️ Виберіть кейс для редагування:", 
            reply_markup=build_select_case_keyboard(cases, "editcase")
        )
    else:
        await callback.message.edit_text("Кейсів не знайдено.", reply_markup=build_admin_cases_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("editcase_"))
async def select_case_field(callback: CallbackQuery, state: FSMContext):
    case_id = callback.data.split("_")[1]
    case = await get_case(case_id)
    if case:
        await state.update_data(case_id=case_id)
        kb = InlineKeyboardBuilder()
        kb.button(text="Назва", callback_data=f"edit_case_name_{case_id}")
        kb.button(text="Картинка", callback_data=f"edit_case_image_{case_id}")
        kb.button(text="⬅️ Скасувати", callback_data="admin_menu")
        kb.adjust(2, 1)
        await callback.message.edit_text(
            f"✏️ Редагувати кейс: {case['case_name']}\n\nВиберіть поле:", 
            reply_markup=kb.as_markup()
        )
    else:
        await callback.message.edit_text("Кейс не знайдено.", reply_markup=build_admin_cases_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("edit_case_name_"))
async def edit_case_name_prompt(callback: CallbackQuery, state: FSMContext):
    case_id = callback.data.split("_")[3]
    await state.set_state(AdminStates.edit_case_name)
    await state.update_data(case_id=case_id)
    await callback.message.edit_text("✏️ Введіть нову назву для кейсу:", reply_markup=build_cancel_keyboard())
    await callback.answer()

@admin_router.message(AdminStates.edit_case_name)
async def process_edit_case_name(message: Message, state: FSMContext):
    data = await state.get_data()
    new_name = message.text.strip()
    if not new_name:
        await message.answer("⚠️ Назва кейсу не може бути пустою. Введіть назву:")
        return
    await update_case(data["case_id"], "case_name", new_name)
    await state.clear()
    await message.answer(f"✅ Назву оновлено на '{new_name}'!", reply_markup=build_admin_cases_keyboard())

@admin_router.callback_query(F.data.startswith("edit_case_image_"))
async def edit_case_image_prompt(callback: CallbackQuery, state: FSMContext):
    case_id = callback.data.split("_")[3]
    await state.set_state(AdminStates.edit_case_image)
    await state.update_data(case_id=case_id)
    await callback.message.edit_text("✏️ Введіть нову URL-адресу зображення для кейсу:", reply_markup=build_cancel_keyboard())
    await callback.answer()

@admin_router.message(AdminStates.edit_case_image)
async def process_edit_case_image(message: Message, state: FSMContext):
    data = await state.get_data()
    await update_case(data["case_id"], "image_case", message.text.strip())
    await state.clear()
    await message.answer("✅ URL зображення кейсу оновлено!", reply_markup=build_admin_cases_keyboard())

@admin_router.callback_query(F.data == "delete_case")
async def delete_case_list(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    cases = await get_all_cases()
    if cases:
        await callback.message.edit_text("🗑️ Виберіть кейс для видалення:", reply_markup=build_select_case_keyboard(cases, "delcase"))
    else:
        await callback.message.edit_text("Кейсів не знайдено.", reply_markup=build_admin_cases_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("delcase_"))
async def confirm_delete_case(callback: CallbackQuery):
    case_id = callback.data.split("_")[1]
    case = await get_case(case_id)
    if case:
        await callback.message.edit_text(
            f"🗑️ Видалити кейс: {case['case_name']}?\nЦе також видалить його прив'язку до всіх скінів.",
            reply_markup=build_confirm_keyboard("case", case_id)
        )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("confirm_case_"))
async def process_delete_case_action(callback: CallbackQuery):
    case_id = callback.data.split("_")[2]
    await delete_case(case_id)
    await callback.message.edit_text("✅ Кейс успішно видалено!", reply_markup=build_admin_cases_keyboard())
    await callback.answer()

# --- КЕРУВАННЯ ЗБРОЄЮ ---

@admin_router.callback_query(F.data == "add_weapon")
async def add_weapon_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminStates.add_weapon)
    await callback.message.edit_text("🔫 Введіть назву нової зброї:", reply_markup=build_cancel_keyboard())
    await callback.answer()

@admin_router.message(AdminStates.add_weapon)
async def process_add_weapon(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("⚠️ Назва зброї не може бути пустою. Спробуйте ще раз:")
        return
    await add_weapon_to_db(name)
    await state.clear()
    await message.answer(f"✅ Зброю '{name}' успішно додано!", reply_markup=build_admin_weapons_keyboard())

@admin_router.callback_query(F.data == "edit_weapon")
async def edit_weapon_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    weapons = await get_all_weapons()
    if weapons:
        await callback.message.edit_text("✏️ Виберіть зброю для редагування:", reply_markup=build_select_weapon_keyboard(weapons, "editwep"))
    else:
        await callback.message.edit_text("Зброї не знайдено.", reply_markup=build_admin_weapons_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("editwep_"))
async def edit_weapon_prompt(callback: CallbackQuery, state: FSMContext):
    weapon_id = callback.data.split("_")[1]
    weapon = await get_weapon(weapon_id)
    if weapon:
        await state.set_state(AdminStates.edit_weapon_name)
        await state.update_data(weapon_id=weapon_id)
        await callback.message.edit_text(f"✏️ Введіть нову назву для '{weapon['weapon_name']}':", reply_markup=build_cancel_keyboard())
    await callback.answer()

@admin_router.message(AdminStates.edit_weapon_name)
async def process_edit_weapon_name(message: Message, state: FSMContext):
    new_name = message.text.strip()
    if new_name:
        data = await state.get_data()
        await update_weapon(data["weapon_id"], new_name)
        await state.clear()
        await message.answer(f"✅ Назву зброї оновлено на '{new_name}'!", reply_markup=build_admin_weapons_keyboard())

@admin_router.callback_query(F.data == "delete_weapon")
async def delete_weapon_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    weapons = await get_all_weapons()
    if weapons:
        await callback.message.edit_text("🗑️ Виберіть зброю для видалення:", reply_markup=build_select_weapon_keyboard(weapons, "delwep"))
    else:
        await callback.message.edit_text("Зброї не знайдено.", reply_markup=build_admin_weapons_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("delwep_"))
async def confirm_delete_weapon_prompt(callback: CallbackQuery):
    weapon_id = callback.data.split("_")[1]
    weapon = await get_weapon(weapon_id)
    if weapon:
        await callback.message.edit_text(
            f"🗑️️ Видалити зброю: {weapon['weapon_name']}?\nЦе також видалить усі пов'язані з нею скіни!",
            reply_markup=build_confirm_keyboard("weapon", weapon_id)
        )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("confirm_weapon_"))
async def process_delete_weapon_action(callback: CallbackQuery):
    weapon_id = callback.data.split("_")[2]
    await delete_weapon(weapon_id)
    await callback.message.edit_text("✅ Зброю та її скіни видалено!", reply_markup=build_admin_weapons_keyboard())
    await callback.answer()

# --- КЕРУВАННЯ СКІНАМИ ---

@admin_router.callback_query(F.data == "add_skin")
async def add_skin_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    weapons = await get_all_weapons()
    if weapons:
        await state.set_state(AdminStates.add_skin_weapon)
        await callback.message.edit_text("🎨 Виберіть зброю для скіна:", reply_markup=build_select_weapon_keyboard(weapons, "new_skin_wep"))
    else:
        await callback.message.edit_text("Спочатку додайте зброю.", reply_markup=build_admin_skins_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("new_skin_wep_"))
async def add_skin_weapon_selected(callback: CallbackQuery, state: FSMContext):
    weapon_id = callback.data.split("_")[3]
    weapon = await get_weapon(weapon_id)
    if weapon:
        await state.update_data(weapon_id=weapon_id, weapon_name=weapon["weapon_name"])
        await state.set_state(AdminStates.add_skin_name)
        await callback.message.edit_text(f"🎨 Введіть назву скіна для {weapon['weapon_name']}:", reply_markup=build_cancel_keyboard())
    await callback.answer()

@admin_router.message(AdminStates.add_skin_name)
async def process_add_skin_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        return
    await state.update_data(skin_name=name)
    await state.set_state(AdminStates.add_skin_rarity)
    
    kb = InlineKeyboardBuilder()
    rarities = ["Common", "Uncommon", "Mythical", "Ancient", "Covert", "Classified", "Restricted", "Mil-Spec Grade"]
    for r in rarities:
        kb.button(text=r, callback_data=f"skinrarity_{r}")
    kb.button(text="Пропустити", callback_data="skinrarity_skip")
    kb.button(text="⬅️ Скасувати", callback_data="admin_menu")
    kb.adjust(2)
    await message.answer("Оберіть рідкість скіна:", reply_markup=kb.as_markup())

@admin_router.callback_query(F.data.startswith("skinrarity_"))
async def process_skin_rarity_choice(callback: CallbackQuery, state: FSMContext):
    rarity = callback.data.replace("skinrarity_", "")
    await state.update_data(rarity=None if rarity == "skip" else rarity)
    await state.set_state(AdminStates.add_skin_stattrak)

    kb = InlineKeyboardBuilder()
    kb.button(text="Так", callback_data="skinstattrak_true")
    kb.button(text="Ні", callback_data="skinstattrak_false")
    kb.adjust(2)
    await callback.message.edit_text("Чи буває скін з StatTrak™?", reply_markup=kb.as_markup())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("skinstattrak_"))
async def process_skin_stattrak_choice(callback: CallbackQuery, state: FSMContext):
    st = callback.data.replace("skinstattrak_", "") == "true"
    await state.update_data(stattrak=st)
    await state.set_state(AdminStates.add_skin_souvenir)

    kb = InlineKeyboardBuilder()
    kb.button(text="Так", callback_data="skinsouvenir_true")
    kb.button(text="Ні", callback_data="skinsouvenir_false")
    kb.adjust(2)
    await callback.message.edit_text("Чи буває скін як Souvenir?", reply_markup=kb.as_markup())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("skinsouvenir_"))
async def process_skin_souvenir_choice(callback: CallbackQuery, state: FSMContext):
    sv = callback.data.replace("skinsouvenir_", "") == "true"
    await state.update_data(souvenir=sv)
    await state.set_state(AdminStates.add_skin_image)
    await callback.message.edit_text("Введіть URL зображення (або 'skip'):", reply_markup=build_cancel_keyboard())
    await callback.answer()

@admin_router.message(AdminStates.add_skin_image)
async def process_skin_image_finish(message: Message, state: FSMContext):
    url = message.text.strip()
    if url.lower() == "skip":
        url = None
    data = await state.get_data()
    skin_id = await add_skin_to_db(
        skin_name=data["skin_name"],
        weapon_id=data["weapon_id"],
        weapon_name=data["weapon_name"],
        rarity=data.get("rarity"),
        stattrak=data.get("stattrak", False),
        souvenir=data.get("souvenir", False),
        image_skin=url
    )
    await state.clear()

    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Додати зноси (wears)", callback_data=f"add_wear_{skin_id}")
    kb.button(text="В меню скінів", callback_data="admin_skins")
    kb.adjust(1)
    await message.answer(f"✅ Скін '{data['weapon_name']} | {data['skin_name']}' додано!", reply_markup=kb.as_markup())

# --- ДОДАВАННЯ WEAR (ЗНОШЕННЯ) ---

@admin_router.callback_query(F.data == "add_skinwear")
async def add_skinwear_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    skins = await get_all_skins()
    if skins:
        await state.set_state(AdminStates.add_skinwear_skin)
        await callback.message.edit_text("Виберіть скін:", reply_markup=build_select_skin_keyboard(skins, "add_wear"))
    else:
        await callback.message.edit_text("Скінів не знайдено.", reply_markup=build_admin_skins_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("add_wear_"))
async def add_skinwear_type(callback: CallbackQuery, state: FSMContext):
    skin_id = callback.data.split("_")[2]
    skin = await get_skin(skin_id)
    if skin:
        await state.set_state(AdminStates.add_skinwear_weartype)
        await state.update_data(skin_id=skin_id)
        await callback.message.edit_text(f"Виберіть знос для {skin['skin_name']}:", reply_markup=build_wear_types_keyboard(skin_id))
    await callback.answer()

@admin_router.callback_query(F.data.startswith("wear_type_"))
async def add_skinwear_float_min_prompt(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    skin_id, wear = parts[2], "_".join(parts[3:])
    await state.update_data(wear_type=wear)
    await state.set_state(AdminStates.add_skinwear_floatmin)
    await callback.message.edit_text(f"Введіть floatmin для {wear} (наприклад: 0.00):", reply_markup=build_cancel_keyboard())
    await callback.answer()

@admin_router.message(AdminStates.add_skinwear_floatmin)
async def process_skinwear_min(message: Message, state: FSMContext):
    try:
        val = float(message.text.strip())
        await state.update_data(float_min=val)
        await state.set_state(AdminStates.add_skinwear_floatmax)
        await message.answer("Введіть floatmax (наприклад: 0.07):", reply_markup=build_cancel_keyboard())
    except ValueError:
        await message.answer("Введіть число від 0 до 1:")

@admin_router.message(AdminStates.add_skinwear_floatmax)
async def process_skinwear_max(message: Message, state: FSMContext):
    try:
        val = float(message.text.strip())
        data = await state.get_data()
        await add_skinwear_to_db(data["skin_id"], data["wear_type"], data["float_min"], val)
        await state.clear()
        await message.answer("✅ Тип зносу збережено!", reply_markup=build_admin_skins_keyboard())
    except ValueError:
        await message.answer("Введіть число від 0 до 1:")

# --- РЕДАГУВАННЯ ТА ВИДАЛЕННЯ СКІНІВ ---

@admin_router.callback_query(F.data == "edit_skin")
async def edit_skin_list(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    skins = await get_all_skins()
    if skins:
        await state.set_state(AdminStates.edit_skin_select)
        await callback.message.edit_text(
            "✏️ Виберіть скін для редагування:",
            reply_markup=build_select_skin_keyboard(skins, "editskin")
        )
    else:
        await callback.message.edit_text("Скінів не знайдено.", reply_markup=build_admin_skins_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("editskin_"))
async def select_skin_field_menu(callback: CallbackQuery, state: FSMContext):
    skin_id = callback.data.split("_")[1]
    skin = await get_skin(skin_id)
    if skin:
        await state.update_data(skin_id=skin_id)
        await callback.message.edit_text(
            f"✏️ Редагування: {skin.get('weapon_name')} | {skin.get('skin_name')}\n\nОберіть поле:",
            reply_markup=build_edit_skin_fields_keyboard(skin_id)
        )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("edit_skin_field_"))
async def edit_skin_field_prompt(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    skin_id = parts[3]
    field = "_".join(parts[4:])
    
    skin = await get_skin(skin_id)
    if not skin:
        await callback.message.edit_text("Скін не знайдено.", reply_markup=build_admin_skins_keyboard())
        await callback.answer()
        return

    await state.set_state(AdminStates.edit_skin_value)
    await state.update_data(skin_id=skin_id, field=field)

    current_val = skin.get(field, "Не встановлено")
    field_title = field.replace("_", " ").capitalize()

    if field in ("stattrak", "souvenir"):
        kb = InlineKeyboardBuilder()
        kb.button(text="Так", callback_data="set_val_true")
        kb.button(text="Ні", callback_data="set_val_false")
        kb.button(text="⬅️ Скасувати", callback_data="admin_menu")
        kb.adjust(2, 1)
        await callback.message.edit_text(
            f"✏️ {field_title} (Зараз: {current_val})\nОберіть нове значення:",
            reply_markup=kb.as_markup()
        )
    else:
        await callback.message.edit_text(
            f"✏️ {field_title} (Зараз: {current_val})\nВведіть нове значення:",
            reply_markup=build_cancel_keyboard()
        )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("set_val_"), AdminStates.edit_skin_value)
async def process_skin_bool_edit(callback: CallbackQuery, state: FSMContext):
    val = callback.data == "set_val_true"
    data = await state.get_data()
    await update_skin(data["skin_id"], data["field"], val)
    await state.clear()
    await callback.message.edit_text("✅ Значення оновлено!", reply_markup=build_admin_skins_keyboard())
    await callback.answer()

@admin_router.message(AdminStates.edit_skin_value)
async def process_skin_text_edit(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    if not text and data["field"] != "image_skin":
        await message.answer("⚠️ Значення не може бути порожнім. Введіть ще раз:")
        return

    await update_skin(data["skin_id"], data["field"], text)
    await state.clear()
    await message.answer("✅ Поле скіна успішно оновлено!", reply_markup=build_admin_skins_keyboard())

@admin_router.callback_query(F.data == "delete_skin")
async def delete_skin_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    skins = await get_all_skins()
    if skins:
        await callback.message.edit_text("🗑️ Виберіть скін для видалення:", reply_markup=build_select_skin_keyboard(skins, "delskin"))
    else:
        await callback.message.edit_text("Скінів не знайдено.", reply_markup=build_admin_skins_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("delskin_"))
async def confirm_delete_skin_prompt(callback: CallbackQuery):
    skin_id = callback.data.split("_")[1]
    skin = await get_skin(skin_id)
    if skin:
        await callback.message.edit_text(
            f"🗑️ Видалити скін: {skin.get('weapon_name')} | {skin.get('skin_name')}?",
            reply_markup=build_confirm_keyboard("skin", skin_id)
        )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("confirm_skin_"))
async def process_delete_skin_action(callback: CallbackQuery):
    skin_id = callback.data.split("_")[2]
    await delete_skin(skin_id)
    await callback.message.edit_text("✅ Скін успішно видалено!", reply_markup=build_admin_skins_keyboard())
    await callback.answer()

# --- ЗВ'ЯЗОК КЕЙС-СКІН ---

@admin_router.callback_query(F.data == "add_caseskin")
async def add_caseskin_select_case(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    cases = await get_all_cases()
    if cases:
        await state.set_state(AdminStates.add_caseskin_case)
        await callback.message.edit_text("➕ Оберіть кейс:", reply_markup=build_select_case_keyboard(cases, "cskin_c"))
    else:
        await callback.message.edit_text("Немає кейсів.", reply_markup=build_admin_caseskins_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("cskin_c_"))
async def add_caseskin_select_skin(callback: CallbackQuery, state: FSMContext):
    case_id = callback.data.replace("cskin_c_", "", 1) 
    case = await get_case(case_id)
    if not case:
        await callback.message.edit_text("❌ Кейс не знайдено в базі.", reply_markup=build_admin_caseskins_keyboard())
        await callback.answer()
        return
    skins = await get_all_skins()
    available = [s for s in skins if case_id not in s.get("case_ids", s.get("cases", []))]
    if available:
        await state.update_data(case_id=case_id, case_name=case.get("case_name", "Без назви"))
        await state.set_state(AdminStates.add_caseskin_skin)
        await callback.message.edit_text(
            f"Оберіть скін для '{case['case_name']}':", 
            reply_markup=build_select_skin_keyboard(available, "cskin_s")
        )
    else:
        await callback.message.edit_text(
            "Всі доступні скіни вже додано в цей кейс (або скінів ще немає).", 
            reply_markup=build_admin_caseskins_keyboard()
        )
    await callback.answer()

@admin_router.callback_query(F.data.startswith("cskin_s_"))
async def process_add_caseskin(callback: CallbackQuery, state: FSMContext):
    skin_id = callback.data.split("_")[2]
    data = await state.get_data()
    await add_skin_to_case(data["case_id"], skin_id)
    await state.clear()
    await callback.message.edit_text(f"✅ Скін додано до кейса '{data['case_name']}'!", reply_markup=build_admin_caseskins_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "remove_caseskin")
async def remove_caseskin_case(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    cases = await get_all_cases()
    if cases:
        await state.set_state(AdminStates.remove_caseskin)
        await callback.message.edit_text("➖ Оберіть кейс:", reply_markup=build_select_case_keyboard(cases, "rem_cs_c"))
    await callback.answer()

@admin_router.callback_query(F.data.startswith("rem_cs_c_"))
async def remove_caseskin_skin(callback: CallbackQuery, state: FSMContext):
    case_id = callback.data.split("_")[3]
    skins = await get_case_skins(case_id)
    if skins:
        await state.update_data(case_id=case_id)
        await state.set_state(AdminStates.remove_caseskin_confirm)
        await callback.message.edit_text("Виберіть скін для видалення з кейса:", reply_markup=build_select_skin_keyboard(skins, "rem_cs_s"))
    else:
        await callback.message.edit_text("У цьому кейсі немає скінів.", reply_markup=build_admin_caseskins_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("rem_cs_s_"))
async def process_remove_caseskin(callback: CallbackQuery, state: FSMContext):
    skin_id = callback.data.split("_")[3]
    data = await state.get_data()
    await remove_skin_from_case(data["case_id"], skin_id)
    await state.clear()
    await callback.message.edit_text("✅ Скін видалено з кейса!", reply_markup=build_admin_caseskins_keyboard())
    await callback.answer()

# --- ОБРОБНИК СКАСУВАННЯ ---

@admin_router.callback_query(F.data == "cancel_action")
async def cancel_any_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Операцію скасовано.", reply_markup=build_admin_keyboard())
    await callback.answer()