from aiogram import Router, types, F
from aiogram.filters import Command
from database.db_operations import get_user_stats, get_leaderboard

router = Router()

@router.message(F.text == "📊 Статистика")
@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)
    
    if stats:
        correct, wrong, last_score, last_played = stats
        total = correct + wrong
        accuracy = int((correct / total) * 100) if total > 0 else 0
        
        stats_text = f"""
        📊 Ваша статистика:
        
        🎯 Последний результат: {last_score}%
        ✅ Всего правильных: {correct}
        ❌ Всего неправильных: {wrong}
        📈 Общая точность: {accuracy}%
        ⏰ Последняя игра: {last_played.split()[0]}
        """
    else:
        stats_text = "📊 У вас еще нет статистики. 🎮 Начните квиз: /quiz"
    
    await message.answer(stats_text)

@router.message(F.text == "🏆 Таблица лидеров")
@router.message(Command("leaderboard"))
async def cmd_leaderboard(message: types.Message):
    leaderboard = await get_leaderboard()
    
    if leaderboard:
        leaderboard_text = "🏆 Топ-10 игроков:\n\n"
        for i, (username, last_score, total_correct) in enumerate(leaderboard, 1):
            leaderboard_text += f"{i}. {username}: {last_score}% ({total_correct} ✅)\n"
    else:
        leaderboard_text = "🏆 Таблица лидеров пуста. 🎮 Станьте первым!"
    
    await message.answer(leaderboard_text)