from aiogram.fsm.state import State, StatesGroup


class UstozKerakForm(StatesGroup):
    full_name = State()
    age = State()
    technologies = State()
    telegram = State()
    region = State()
    contact_time = State()
    purpose = State()


class IshJoyiKerakForm(StatesGroup):
    full_name = State()
    age = State()
    technologies = State()
    telegram = State()
    phone = State()
    region = State()
    salary = State()
    profession = State()
    contact_time = State()
    purpose = State()


class XodimKerakForm(StatesGroup):
    company_name = State()
    technologies = State()
    telegram = State()
    phone = State()
    region = State()
    responsible_person = State()
    contact_time = State()
    working_hours = State()
    salary = State()
    additional_info = State()


class ShogirdKerakForm(StatesGroup):
    mentor_name = State()
    age = State()
    technologies = State()
    telegram = State()
    phone = State()
    region = State()
    price = State()
    profession = State()
    contact_time = State()
    purpose = State()


class SherikKerakForm(StatesGroup):
    partner_name = State()
    technologies = State()
    telegram = State()
    region = State()
    price = State()
    profession = State()
    contact_time = State()
    purpose = State()
