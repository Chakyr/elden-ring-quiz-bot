import asyncio
import logging
from aiogram import Bot, Dispatcher
from config.config import API_TOKEN
from database.db_operations import create_tables
from handlers.start_handlers import router as start_router
from handlers.quiz_handlers import router as quiz_router
from handlers.stats_handlers import router as stats_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Создаем бота и диспетчер
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    
    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(quiz_router)
    dp.include_router(stats_router)
    
    # Создаем таблицы в базе данных
    await create_tables()
    logger.info("Таблицы базы данных созданы")
    
    # Запускаем бота
    logger.info("Бот Elden Ring Quiz запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())