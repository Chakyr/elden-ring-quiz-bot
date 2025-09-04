import aiosqlite
from config.config import DB_NAME

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state 
                         (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS user_stats 
                         (user_id INTEGER PRIMARY KEY, 
                          username TEXT,
                          total_correct INTEGER DEFAULT 0,
                          total_wrong INTEGER DEFAULT 0,
                          last_score INTEGER DEFAULT 0,
                          last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            results = await cursor.fetchone()
            return results[0] if results else 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', 
                        (user_id, index))
        await db.commit()

async def update_user_stats(user_id, username, is_correct):
    async with aiosqlite.connect(DB_NAME) as db:
        # Обновляем или создаем запись пользователя
        await db.execute('''INSERT OR IGNORE INTO user_stats 
                          (user_id, username, total_correct, total_wrong) 
                          VALUES (?, ?, 0, 0)''', (user_id, username))
        
        if is_correct:
            await db.execute('''UPDATE user_stats SET total_correct = total_correct + 1 
                              WHERE user_id = ?''', (user_id,))
        else:
            await db.execute('''UPDATE user_stats SET total_wrong = total_wrong + 1 
                              WHERE user_id = ?''', (user_id,))
        
        await db.commit()

async def update_last_score(user_id, score):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE user_stats SET last_score = ? WHERE user_id = ?', 
                        (score, user_id))
        await db.commit()

async def get_user_stats(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''SELECT total_correct, total_wrong, last_score, last_played 
                              FROM user_stats WHERE user_id = ?''', (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_leaderboard():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''SELECT username, last_score, total_correct 
                              FROM user_stats 
                              ORDER BY last_score DESC 
                              LIMIT 10''') as cursor:
            return await cursor.fetchall()