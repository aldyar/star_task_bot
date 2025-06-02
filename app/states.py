from aiogram.fsm.state import StatesGroup, State


class CreateTask(StatesGroup):
    waiting_for_link = State()
    waiting_for_reward = State()
    waiting_for_count = State()
    waiting_fot_chat_id = State()
    waiting_for_task_type = State()
    waiting_for_description = State()

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

class Reminder(StatesGroup):
    wait_text = State()
    wait_image = State()
    wait_button_text = State()
    wait_button_url = State()
    
class Event(StatesGroup):
    wait_c1 = State()
    wait_c2 = State()
    wait_c3 = State()
    wait_c4 = State()
    wait_c5 = State()
    wait_c6 = State()
    wait_rule = State()
    wait_text = State()
    wait_image = State()
    end_date = State()
    
class StartChannel(StatesGroup):
    link = State()
    chat_id = State()

class LinkStat(StatesGroup):
    wait_name = State()

class MiniAdds(StatesGroup):
    wait_text = State()
    wait_button_text = State()
    wait_url = State()

    