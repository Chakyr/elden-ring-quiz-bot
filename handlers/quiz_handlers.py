from aiogram import Router, types, F
from aiogram.filters import Command
import aiosqlite
from data.quiz_data import quiz_data
from utils.keyboards import generate_options_keyboard
from database.db_operations import (
    get_quiz_index, 
    update_quiz_index, 
    update_current_attempt, 
    start_new_attempt, 
    finish_attempt,
    get_current_attempt_stats  # Импортируем новую функцию
)
from config.config import DB_NAME

router = Router()

@router.message(F.text == "🎮 Начать квиз")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer("⚔️ Вперед, Избранный! Проверим твои знания!")
    await new_quiz(message)

async def new_quiz(message):
    user_id = message.from_user.id
    await update_quiz_index(user_id, 0)
    await start_new_attempt(user_id)
    await get_question(message, user_id)

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    
    if current_question_index >= len(quiz_data):
        await finish_quiz(message, user_id)
        return
    
    question_data = quiz_data[current_question_index]
    correct_index = question_data['correct_option']
    opts = question_data['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    
    question_text = f"❓ Вопрос {current_question_index + 1}/{len(quiz_data)}:\n{question_data['question']}"
    await message.answer(question_text, reply_markup=kb)

@router.callback_query(F.data.startswith("right_"))
async def right_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_question_index = await get_quiz_index(user_id)
    selected_index = int(callback.data.split("_")[1])
    
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    selected_option = quiz_data[current_question_index]['options'][selected_index]
    await callback.message.answer(f"✅ Вы выбрали: {selected_option}")
    await callback.message.answer("🎯 Верно!")
    
    await update_current_attempt(user_id, True)
    
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)
    
    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await finish_quiz(callback.message, user_id)

@router.callback_query(F.data.startswith("wrong_"))
async def wrong_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_question_index = await get_quiz_index(user_id)
    selected_index = int(callback.data.split("_")[1])
    
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    selected_option = quiz_data[current_question_index]['options'][selected_index]
    await callback.message.answer(f"❌ Вы выбрали: {selected_option}")
    
    correct_option = quiz_data[current_question_index]['options'][quiz_data[current_question_index]['correct_option']]
    await callback.message.answer(f"📌 Правильный ответ: {correct_option}")
    
    if 'explanation' in quiz_data[current_question_index]:
        await callback.message.answer(f"💡 {quiz_data[current_question_index]['explanation']}")
    
    await update_current_attempt(user_id, False)
    
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)
    
    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await finish_quiz(callback.message, user_id)

async def finish_quiz(message, user_id):
    # Завершаем попытку и получаем статистику ТОЛЬКО этой попытки
    correct, wrong, score = await finish_attempt(user_id, message.from_user.username)
    
    if correct + wrong == len(quiz_data):  # Проверяем, что прошли все вопросы
        result_text = f"""
        🎉 Квиз завершен!
        
        📊 Результат этой попытки:
        ✅ Правильных ответов: {correct}
        ❌ Неправильных ответов: {wrong}
        🎯 Точность: {score}%
        
        {'🏆 Отличный результат! Вы истинный Владыка Элдена!' if score >= 80 else 
          '⚔️ Хороший результат! Продолжайте тренироваться!' if score >= 60 else 
          '🔥 Нужно больше практики! Играйте снова!'}
        
        📊 Посмотреть общую статистику: /stats
        🎮 Начать новую попытку: /quiz
        """
    else:
        result_text = "⚠️ Что-то пошло не так. Попробуйте начать заново: /quiz"
    
    await message.answer(result_text)

@router.message(Command("reset_stats"))
async def cmd_reset_stats(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM user_stats WHERE user_id = ?', (user_id,))
        await db.execute('DELETE FROM current_attempt WHERE user_id = ?', (user_id,))
        await db.execute('DELETE FROM quiz_state WHERE user_id = ?', (user_id,))
        await db.commit()
    
    await message.answer("🔄 Вся статистика сброшена! Начните заново: /quiz")