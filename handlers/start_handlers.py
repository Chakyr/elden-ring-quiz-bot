from aiogram import Router, types, F
from aiogram.filters import Command
from utils.keyboards import main_menu_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = """
    🔥 Добро пожаловать в квиз по Elden Ring!
    
    Проверь свои знания о Землях Междумирья!
    Выбери действие из меню ниже:
    """
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())

@router.message(F.text == "📋 Правила")
async def cmd_rules(message: types.Message):
    rules_text = """
    📋 Правила квиза:
    
    • Отвечай на вопросы о мире Elden Ring
    • Выбирай один из вариантов ответа
    • Всего 10 вопросов
    • После ответа кнопки исчезают, а текст ответа сохраняется
    • Результат сохраняется в статистике
    
    🎮 Готов проверить свои знания?
    """
    await message.answer(rules_text)