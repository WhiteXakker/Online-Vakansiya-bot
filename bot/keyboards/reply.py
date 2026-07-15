from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

MAIN_MENU_BUTTONS = [
    "Ustoz kerak",
    "Ish joyi kerak",
    "Xodim kerak",
    "Shogird kerak",
    "Sherik kerak",
]

CANCEL_BUTTON = "❌ Bekor qilish"


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MAIN_MENU_BUTTONS[0]), KeyboardButton(text=MAIN_MENU_BUTTONS[1])],
            [KeyboardButton(text=MAIN_MENU_BUTTONS[2]), KeyboardButton(text=MAIN_MENU_BUTTONS[3])],
            [KeyboardButton(text=MAIN_MENU_BUTTONS[4])],
        ],
        resize_keyboard=True,
        input_field_placeholder="Kerakli bo'limni tanlang...",
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=CANCEL_BUTTON)]],
        resize_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
