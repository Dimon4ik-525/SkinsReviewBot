import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.start_command import start_router
from handlers.case_explorer_flow import case_router
from handlers.weapon_catalog_flow import weapon_router
from handlers.skin_search_flow import search_router
from handlers.admin_flow import admin_router

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    logging.info("Ініціалізація CS2 Items Bot...")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Порядок реєстрації: адмін-панель перша, далі призначені для користувача сценарії
    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(case_router)
    dp.include_router(weapon_router)
    dp.include_router(search_router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Бот успішно запущений і готовий до роботи.")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logging.info("Сесію бота закрито.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот зупинений користувачем.")