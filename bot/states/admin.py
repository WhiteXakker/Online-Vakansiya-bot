# bot/states/admin.py

from aiogram.fsm.state import State, StatesGroup


class AdminPanel(StatesGroup):
    waiting_user_search = State()
    waiting_channel_id = State()
    waiting_rejection_reason = State()
    
    # Majburiy obuna statelari
    waiting_mandatory_channel_id = State()
    waiting_mandatory_invite_link = State()
    waiting_channel_name = State()
    waiting_channel_link = State()
    
    # Yangi admin qo'shish statelari (qavslar va dublikat tuzatildi)
    waiting_new_admin_id = State()
    waiting_new_admin_name = State()  # <-- Oxiriga () qo'shildi!


class BroadcastState(StatesGroup):
    waiting_content = State()
    confirm = State()