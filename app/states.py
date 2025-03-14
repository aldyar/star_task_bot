from aiogram.fsm.state import StatesGroup, State


class CreateTask(StatesGroup):
    waiting_for_link = State()
    waiting_for_reward = State()
    waiting_for_count = State()


class EditTask(StatesGroup):
    adding_completions = State()
    changing_reward = State()

class EditRef(StatesGroup):
    edit_ref_reward = State()
    edit_ref_text = State()
    