from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton
from database.requests import get_withdraw_limit,get_task_about_taskid
main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = '⭐️Заработать звёзды'),
                                      KeyboardButton(text = '🏆Топ')],
                                     [KeyboardButton(text = '🎁Вывести звёзды'),
                                      KeyboardButton(text = '👤Профиль')],
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

complete_inline = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Выполнить',url = ''),
                                                        InlineKeyboardButton(text = '✅Выполнил', callback_data='complete_task')],
                                                        [InlineKeyboardButton(text = '⏩Пропустить', callback_data= 'skip')]])


async def complete_task_inline(link):
    complete_inline = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Выполнить',url = f'{link}'),
                                                        InlineKeyboardButton(text = '✅Выполнил', callback_data='complete_task')],
                                                        [InlineKeyboardButton(text = '⏩Пропустить', callback_data= 'skip')]])

    return complete_inline


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
                                            [KeyboardButton(text = 'Вывод средств'),
                                             KeyboardButton(text = 'Конкурс')],
                                            [KeyboardButton(text = 'Приветствие'),
                                            KeyboardButton(text = 'Напоминание')],
                                            [KeyboardButton(text = 'Бонус'),
                                             KeyboardButton(text = 'Статистика')]], resize_keyboard=True)

tasks_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✅ Создать задание', callback_data='create_task')],
                                                   [InlineKeyboardButton(text = '✏️ Редактировать задание', callback_data='edit_task')],
                                                   [InlineKeyboardButton(text = '🗄 Архив заданий', callback_data= 'TaskArchive')]])

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

stat_edit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✏️Сортировать по дате(Регистрация)',callback_data='NumDate_reg')],
                                                  [InlineKeyboardButton(text = '✏️Сортировать по дате(Количество привлеченных)',callback_data='NumDate_ref')],
                                                  [InlineKeyboardButton(text = '🔗 Ссылки',callback_data='LinkStat')],
                                                  [InlineKeyboardButton(text = '🧾 Промокод',callback_data='Promocode')]])

inline_task_type = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Подписка',callback_data= 'subscribe')],
                                                         [InlineKeyboardButton(text = 'Заявка', callback_data = 'entry')],
                                                         [InlineKeyboardButton(text = 'Переход в бота',callback_data='BotEntry')]])

describe_inline = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '❌Без текстат', callback_data= 'describe_none')]])


async def entry_type_inline(link):
    entry_type_inline =  InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Выполнить',url = f'{link}')],
                                                        [InlineKeyboardButton(text = '⏩Пропустить', callback_data= 'skip')]])
    return entry_type_inline

next_task_inline = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '🎯Следующее задание',callback_data='task')]])

inline_admin_reminder = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Изменить текст', callback_data='ResetTextReminder')],
                                                              [InlineKeyboardButton(text = 'Изменить картинку', callback_data= 'ResetImageReminder')],
                                                              [InlineKeyboardButton(text = 'Изменить кнопку',callback_data='ResetButton')],
                                                              [InlineKeyboardButton(text = 'Опубликовать',callback_data='SendReminder')]])


inline_user_profile = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '🧾 Промокод', callback_data='UsePromocode')],
                                                             [InlineKeyboardButton(text = '⬅️В главное меню',callback_data='BackMenu')]])
                                                              

inline_user_top = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '📅 Топ за неделю',callback_data='TopWeek')],
                                                        [InlineKeyboardButton(text = '📅 Топ за месяц',callback_data='TopMonth')]])


inline_admin_event = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Создать конкурс',callback_data='CreateEvent')],
                                                           [InlineKeyboardButton(text = 'Активный конкрус',callback_data='ActiveEvent')]])

inline_type_event = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Конкурса N1',callback_data='Event_1')],
                                                          [InlineKeyboardButton(text = 'Конкурса N2',callback_data='Event_2')],
                                                          [InlineKeyboardButton(text = 'Конкурса N3',callback_data='Event_3')],
                                                          [InlineKeyboardButton(text = 'Конкурса N4',callback_data='Event_4')]])

inline_save_or_delete_event = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Сохранить',callback_data='EventSave')],
                                                                    [InlineKeyboardButton(text = 'Не сохранять',callback_data='EventDontSave')]])

async def inline_join_event(event_id):
    inline_join_event = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Участвовать',callback_data=f'eventjoin_{event_id}')]])
    return inline_join_event

inline_admin_start_channel = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Добавить канал',callback_data='AddStartChannel')],
                                                                   [InlineKeyboardButton(text = 'Удалить канал',callback_data='DeleteStartChannel')]])

async def inline_subgram(link):
    inline_subgram = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Выполнить',url = f'{link}'),
                                                        InlineKeyboardButton(text = '✅Выполнил', callback_data=f'SubComplete_{link}')],
                                                        [InlineKeyboardButton(text = '⏩Пропустить', callback_data= 'SkipSubgram')]])
    return inline_subgram

inline_choose_gender = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '🙎🏼‍♂️ Мужской',callback_data='gender_male'),
                                                              InlineKeyboardButton(text = '🙍🏼‍♀️ Женский', callback_data='gender_female')]])


inline_link_stat = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Создать ссылку',callback_data='CreateLink')],
                                                         [InlineKeyboardButton(text = 'Список ссылок', callback_data='LinkList')]])

inline_reminder_edit_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Изменить кнопку', callback_data='ReminderTextButton')],
                                                                    [InlineKeyboardButton(text = 'Удалить кнопку',callback_data='ReminderDeleteButton')]])

async def inline_remider_button(text,url):
    inline_remider_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = text,url = url)]])
    return inline_remider_button

async def check_flyer(mark):
    check_flyer = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✅Проверить', callback_data=f'CheckFlyer_{mark}')]])
    return check_flyer

remider_choose = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Напоминание',callback_data='Reminder')],
                                                       [InlineKeyboardButton(text = 'Мини рекламы',callback_data='MiniAdds')]])

mini_adds_choose = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Старт',callback_data='choose_start')],
                                                         [InlineKeyboardButton(text = 'Базовая',callback_data='choose_base')]])


async def mini_adds_menu(type):
    mini_adds_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Список реклам',callback_data=f'Mini_{type}')],
                                                       [InlineKeyboardButton(text = 'Создать новую рекламу',callback_data=f'CreateMiniAdds_{type}')]])
    return mini_adds_menu


async def mini_adds_set(type):
    mini_adds_set = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Удалить',callback_data=f'DeleteMini_{type}')]])
    return mini_adds_set

async def add_mini_adds(type):
    add_mini_adds = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Создать рекламу',callback_data=f'CreateMiniAdds_{type}')],])
    return add_mini_adds

async def mini_add(text,url):
    mini_add = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = f'{text}',url=f'{url}')]])
    return mini_add

promocode_menu_inline = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text ='Список промокодов',callback_data='PromoList')],
                                                              [InlineKeyboardButton(text = 'Создать промокод',callback_data='CreatePromocode')],
                                                              [InlineKeyboardButton(text = 'Удалить промокод', callback_data='DeletePromocode')]])

new_withdraw_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='15 ⭐️ (🧸)', callback_data='gift_15_🧸'),
                                                           InlineKeyboardButton(text='15 ⭐️ (💖)', callback_data='gift_15_💖')],
                                                          [InlineKeyboardButton(text='25 ⭐️ (🌹)', callback_data='gift_25_🌹'),
                                                           InlineKeyboardButton(text='25 ⭐️ (🎁)', callback_data='gift_25_🎁')],
                                                          [InlineKeyboardButton(text='50 ⭐️ (🍾)', callback_data='gift_50_🍾'),
                                                           InlineKeyboardButton(text='50 ⭐️ (🚀)', callback_data='gift_50_🚀')],
                                                          [InlineKeyboardButton(text='50 ⭐️ (💐)', callback_data='gift_50_💐'),
                                                           InlineKeyboardButton(text='50 ⭐️ (🎂)', callback_data='gift_50_🎂')],
                                                          [InlineKeyboardButton(text='100 ⭐️ (🏆)', callback_data='gift_100_🏆'),
                                                          InlineKeyboardButton(text='100 ⭐️ (💍)', callback_data='gift_100_💍')],
                                                          [InlineKeyboardButton(text='100 ⭐️ (💎)', callback_data='gift_100_💎')]])
                                                          #[InlineKeyboardButton(text='Telegram Premium 6мес. (1700 ⭐️)', callback_data='gift_1700_💎')]])


add_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '🧸',url = 'https://t.me/freestarsss_tgrobot?start=Stars'),
                                                      InlineKeyboardButton(text = '🚀',url = 'https://t.me/freestarsss_tgrobot?start=Stars'),
                                                      InlineKeyboardButton(text = '💍',url = 'https://t.me/freestarsss_tgrobot?start=Stars')],
                                                     [InlineKeyboardButton(text = '🌹',url = 'https://t.me/freestarsss_tgrobot?start=Stars'),
                                                      InlineKeyboardButton(text = '🍭',url = 'https://t.me/freestarsss_tgrobot?start=Stars'),
                                                      InlineKeyboardButton(text = '🏆',url = 'https://t.me/freestarsss_tgrobot?start=Stars')],
                                                      [InlineKeyboardButton(text = '--Другой подарок', url = 'https://t.me/freestarsss_tgrobot?start=Stars')]])                                                        