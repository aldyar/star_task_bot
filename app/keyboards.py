from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton
from app.database.requests import get_withdraw_limit
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

withdraw_inline = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '15⭐️',callback_data='15'),
                                                         InlineKeyboardButton(text = '25⭐️',callback_data='25')],
                                                         [InlineKeyboardButton(text = '50⭐️',callback_data='50'),
                                                          InlineKeyboardButton(text = '100⭐️',callback_data='100')],
                                                          [InlineKeyboardButton(text = '150⭐️',callback_data='150'),
                                                           InlineKeyboardButton(text = '350⭐️',callback_data='350')],
                                                           [InlineKeyboardButton(text = '500⭐️',callback_data='500')]])

complete_inline = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✅Выполнил', callback_data='complete_task')]])


"""async def withdraw_inline():
    # Значения по умолчанию
    default_values = [15, 25, 50, 100, 150, 350, 500]

    # Получаем лимиты из базы данных
    limits = await get_withdraw_limit()

    # Если значения в БД есть, используем их, иначе используем значения по умолчанию
    buttons = limits if limits else default_values

    # Формируем клавиатуру
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=str(value), callback_data=f"withdraw_{value}")] for value in buttons
        ]
    )

    return keyboard"""


async def withdraw_keyboard():
    values = await get_withdraw_limit()
    withdraw_inline = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'{values[0]}⭐️', callback_data=f'withdraw_{values[0]}'),
        InlineKeyboardButton(text=f'{values[1]}⭐️', callback_data=f'withdraw_{values[1]}')],
        [InlineKeyboardButton(text=f'{values[2]}⭐️', callback_data=f'withdraw_{values[2]}'),
        InlineKeyboardButton(text=f'{values[3]}⭐️', callback_data=f'withdraw_{values[3]}')],
        [InlineKeyboardButton(text=f'{values[4]}⭐️', callback_data=f'withdraw_{values[4]}'),
        InlineKeyboardButton(text=f'{values[5]}⭐️', callback_data=f'withdraw_{values[5]}')],
        [InlineKeyboardButton(text=f'{values[6]}⭐️', callback_data=f'withdraw_{values[6]}')],
    ])
    return withdraw_inline


#ADMIN KEYBOARDS
main_admin = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = 'Задание'),
                                            KeyboardButton(text = 'Реферальная система')],
                                            [KeyboardButton(text = 'Вывод средств')],
                                            [KeyboardButton(text = 'Бонус'),
                                             KeyboardButton(text = 'Статистика')]], resize_keyboard=True)

tasks_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✅ Создать задание', callback_data='create_task')],
                                                   [InlineKeyboardButton(text = '✏️ Редактировать задание', callback_data='edit_task')]])

referal_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✏️Изменить текст', callback_data='edit_ref_text')],
                                                     [InlineKeyboardButton(text = '⭐️Изменить вознаграждение',callback_data='edit_ref_reward')]])

withdraw_menu_admin = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✏️Изменить значения', callback_data= 'editwithdraw_limit')],
                                                            [InlineKeyboardButton(text = '💸Заявки на вывод', callback_data= 'withdraw_req')]])

async def withdraw_edit_req():
    values = await get_withdraw_limit()
    withdraw_inline = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'{values[0]}⭐️', callback_data=f'editlimit_1'),
        InlineKeyboardButton(text=f'{values[1]}⭐️', callback_data=f'editlimit_2')],
        [InlineKeyboardButton(text=f'{values[2]}⭐️', callback_data=f'editlimit_3'),
        InlineKeyboardButton(text=f'{values[3]}⭐️', callback_data=f'editlimit_4')],
        [InlineKeyboardButton(text=f'{values[4]}⭐️', callback_data=f'editlimit_5'),
        InlineKeyboardButton(text=f'{values[5]}⭐️', callback_data=f'editlimit_6')],
        [InlineKeyboardButton(text=f'{values[6]}⭐️', callback_data=f'editlimit_7')],
    ])
    return withdraw_inline

edit_bonus = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Изменить',callback_data='editbonus')]])

stat_edit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✏️Сортировать по дате',callback_data='num_date')]])

