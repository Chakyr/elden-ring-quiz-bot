from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    
    for option in answer_options:
        callback_data = f"right_{answer_options.index(option)}" if option == right_answer else f"wrong_{answer_options.index(option)}"
        builder.add(types.InlineKeyboardButton(text=option, callback_data=callback_data))
    
    builder.adjust(1)
    return builder.as_markup()

def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="🎮 Начать квиз"))
    builder.add(types.KeyboardButton(text="📋 Правила"))
    builder.add(types.KeyboardButton(text="📊 Статистика"))
    builder.add(types.KeyboardButton(text="🏆 Таблица лидеров"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)