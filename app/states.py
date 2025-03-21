from aiogram.fsm.state import StatesGroup, State


class CreateTask(StatesGroup):
    waiting_for_link = State()
    waiting_for_reward = State()
    waiting_for_count = State()
    waiting_fot_chat_id = State()


class EditTask(StatesGroup):
    adding_completions = State()
    changing_reward = State()

class EditRef(StatesGroup):
    edit_ref_reward = State()
    edit_ref_text = State()

class EditLimit(StatesGroup):
    edit_withdraw_limit = State()

class EditBonus(StatesGroup):
    edit_bonus = State()

class Date(StatesGroup):
    first_date = State()
    second_date = State()