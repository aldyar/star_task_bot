from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.states import Promocode
from function.promocode_req import PromocodeFunction

admin = Router()



@admin.callback_query(F.data == 'Promocode')
async def admin_promocode(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "*Управление промокодами*\n\n"
        "Выбери, что хочешь сделать:\n"
        "• Создать новый промокод\n"
        "• Удалить существующий\n"
        "• Посмотреть список всех\n\n"
        "_Нажми кнопку ниже:_",
        reply_markup=kb.promocode_menu_inline,
        parse_mode="Markdown"
    )


@admin.callback_query(F.data == 'PromoList')
async def show_promocodes(callback: CallbackQuery,state:FSMContext):
    await callback.answer()
    await state.clear()
    promocodes = await PromocodeFunction.get_promocode()

    active = []
    inactive = []

    for promo in promocodes:
        if promo.use_count < promo.total_count:
            active.append(promo)
        else:
            inactive.append(promo)

    # Активные промокоды — по одному сообщению
    if active:
        for promo in active:
            await callback.message.answer(
                f"*Название:* {promo.name}\n"
                f"*Промокод:* `{promo.code}`\n"
                f"*Использовано:* {promo.use_count} / {promo.total_count}\n"
                f"*Награда:* {promo.reward}",
                parse_mode='Markdown'
            )
    else:
        await callback.message.answer("*Нет активных промокодов.*", parse_mode='Markdown')

    # Неактивные — списком
    if inactive:
        text = "*Неактивные промокоды:*\n\n"
        for promo in inactive:
            text += f"🔒 *{promo.name}* (`{promo.code}`) — {promo.use_count}/{promo.total_count}\n"
        await callback.message.answer(text, parse_mode='Markdown')
    else:
        await callback.message.answer("*Нет неактивных промокодов.*", parse_mode='Markdown')



@admin.callback_query(F.data == 'CreatePromocode')
async def create_promocode(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    await callback.message.answer(
        "*Введите данные промокода в следующем формате:*\n\n"
        "*Название\nПромокод\nКол-во использований\nНаграда*\n\n"
        "*Пример:*\n_Летний бонус\nSUMMER2025\n10\n50_",
        parse_mode='Markdown'
    )
    await state.set_state(Promocode.create_promo)


@admin.message(Promocode.create_promo)
async def create_promocode_handler(message: Message, state: FSMContext):
    lines = message.text.strip().split("\n")

    if len(lines) != 4:
        await message.answer(
            "❌ *Неверный формат. Пожалуйста, введите ровно 4 строки*:\n"
            "*Название\nПромокод\nКол-во\nНаграда*\n\n"
            "*Пример:*\n_Летний бонус\nSUMMER2025\n10\n50_",
            parse_mode='Markdown'
        )
        return

    name, promocode, count_str, reward_str = lines

    # Валидация чисел
    try:
        count = int(count_str)
        reward = int(reward_str)
    except ValueError:
        await message.answer(
            "❌ *Ошибка: Кол-во и награда должны быть числами*.\n"
            "*Попробуй снова по шаблону:*\n\n"
            "*Пример:*\n_Летний бонус\nSUMMER2025\n10\n50_",
            parse_mode='Markdown'
        )
        return

    # Сохраняем
    await PromocodeFunction.create_promocode(name=name, promocode=promocode, count=count, reward=reward)

    await message.answer("✅ Промокод успешно сохранён!")
    await state.clear()


@admin.callback_query(F.data =='DeletePromocode')
async def delete_promocode(callback:CallbackQuery,state:FSMContext):
    await callback.answer()
    await callback.message.answer("*Введите промокод, который хотите удалить:*",parse_mode='Markdown')
    await state.set_state(Promocode.delete_promo)


@admin.message(Promocode.delete_promo)
async def process_delete_promocode(message: Message, state: FSMContext):
    promo_code_text = message.text.strip()

    promocode = await PromocodeFunction.delete_promocode(promo_code_text)

    if promocode:
        await message.answer(f"*Промокод* `{promo_code_text}` *успешно удалён* ✅",parse_mode='Markdown')
    else:
        await message.answer(f"*Промокод* `{promo_code_text}` *не найден* ❌",parse_mode='Markdown')

    await state.clear()