from aiogram import Router, types, F
from aiogram.filters import Command
import aiosqlite
from data.quiz_data import quiz_data
from utils.keyboards import generate_options_keyboard
from database.db_operations import get_quiz_index, update_quiz_index, update_user_stats, update_last_score
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
    
    # Удаляем кнопки
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    # Показываем выбранный ответ
    selected_option = quiz_data[current_question_index]['options'][selected_index]
    await callback.message.answer(f"✅ Вы выбрали: {selected_option}")
    await callback.message.answer("🎯 Верно!")
    
    # Обновляем статистику
    await update_user_stats(user_id, callback.from_user.username, True)
    
    # Переходим к следующему вопросу
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
    
    # Удаляем кнопки
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    # Показываем выбранный ответ
    selected_option = quiz_data[current_question_index]['options'][selected_index]
    await callback.message.answer(f"❌ Вы выбрали: {selected_option}")
    
    correct_option = quiz_data[current_question_index]['options'][quiz_data[current_question_index]['correct_option']]
    await callback.message.answer(f"📌 Правильный ответ: {correct_option}")
    
    if 'explanation' in quiz_data[current_question_index]:
        await callback.message.answer(f"💡 {quiz_data[current_question_index]['explanation']}")
    
    # Обновляем статистику
    await update_user_stats(user_id, callback.from_user.username, False)
    
    # Переходим к следующему вопросу
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)
    
    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        await finish_quiz(callback.message, user_id)

async def finish_quiz(message, user_id):
    # Получаем статистику
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''SELECT total_correct, total_wrong FROM user_stats 
                              WHERE user_id = ?''', (user_id,)) as cursor:
            stats = await cursor.fetchone()
    
    if stats:
        correct, wrong = stats
        total = correct + wrong
        score = int((correct / total) * 100) if total > 0 else 0
        
        await update_last_score(user_id, score)
        
        result_text = f"""
        🎉 Квиз завершен!
        
        📊 Ваш результат:
        ✅ Правильных ответов: {correct}
        ❌ Неправильных ответов: {wrong}
        🎯 Точность: {score}%
        
        {'🏆 Отличный результат! Вы истинный Владыка Элдена!' if score >= 80 else 
          '⚔️ Хороший результат! Продолжайте тренироваться!' if score >= 60 else 
          '🔥 Нужно больше практики! Играйте снова!'}
        
        🎮 Хотите попробовать еще раз? /quiz
        """
    else:
        result_text = "🎉 Квиз завершен! 🎮 Начните заново: /quiz"
    
    await message.answer(result_text)