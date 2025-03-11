from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = '⭐️Заработать звёзды')],
                                     [KeyboardButton(text = '🎁Вывести звёзды')],
                                     [KeyboardButton(text = '🎯Задания'),
                                      KeyboardButton(text = '💎Бонус')]],
                                      resize_keyboard=True)

captcha_1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '🥦',callback_data='void'),
                                                   InlineKeyboardButton(text = '🥑',callback_data='void'),
                                                   InlineKeyboardButton(text = '🍆',callback_data='void')],
                                                  [InlineKeyboardButton(text = '🌽',callback_data='void'),
                                                   InlineKeyboardButton(text = '🥕',callback_data='void'),
                                                   InlineKeyboardButton(text = '🍄',callback_data='void')],
                                                  [InlineKeyboardButton(text = '🍔',callback_data='void'),
                                                   InlineKeyboardButton(text = '🥝',callback_data='void'),
                                                   InlineKeyboardButton(text = '🍍',callback_data='accsess')]])
captcha_2 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '🥦',callback_data='void'),
                                                   InlineKeyboardButton(text = '🥑',callback_data='accsess'),
                                                   InlineKeyboardButton(text = '🍆',callback_data='void')],
                                                  [InlineKeyboardButton(text = '🌽',callback_data='void'),
                                                   InlineKeyboardButton(text = '🥕',callback_data='void'),
                                                   InlineKeyboardButton(text = '🍄',callback_data='void')],
                                                  [InlineKeyboardButton(text = '🍔',callback_data='void'),
                                                   InlineKeyboardButton(text = '🥝',callback_data='void'),
                                                   InlineKeyboardButton(text = '🍍',callback_data='void')]])

captchas = [
    ("🍍", captcha_1),  # Укажи правильный эмодзи из капчи 1
    ("🥑", captcha_2)   # Укажи правильный эмодзи из капчи 2
]

task_inline = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '🎯Показать задания', callback_data='task')]])