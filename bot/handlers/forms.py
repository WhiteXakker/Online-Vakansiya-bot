from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.form_config import FORM_FLOWS, MENU_TO_CATEGORY
from bot.keyboards.inline import confirmation_keyboard
from bot.keyboards.reply import CANCEL_BUTTON, cancel_keyboard, main_menu_keyboard
from bot.utils.templates import render_submission
from database import queries

router = Router(name="forms")


async def _start_form(message: Message, state: FSMContext, category: str) -> None:
    flow = FORM_FLOWS[category]
    first_step = flow["steps"][0]
    first_state = flow["states"][0]

    await state.update_data(category=category, form_data={}, step_index=0)
    await state.set_state(first_state)
    await message.answer(
        f"📝 <b>{flow['title']}</b>\n\n{first_step.prompt}",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text.in_(MENU_TO_CATEGORY.keys()))
async def select_category(message: Message, state: FSMContext) -> None:
    category = MENU_TO_CATEGORY[message.text]
    await _start_form(message, state, category)


@router.message(F.text == CANCEL_BUTTON)
async def cancel_form(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "❌ Jarayon bekor qilindi.\nAsosiy menyuga qaytdingiz.",
        reply_markup=main_menu_keyboard(),
    )


def _register_step_handlers(router: Router, category: str) -> None:
    flow = FORM_FLOWS[category]
    states = flow["states"]

    for index, (step, fsm_state) in enumerate(zip(flow["steps"], states)):
        async def step_handler(
            message: Message,
            state: FSMContext,
            *,
            step_index: int = index,
            cat: str = category,
        ) -> None:
            current_flow = FORM_FLOWS[cat]
            current_step = current_flow["steps"][step_index]
            value = message.text.strip()

            if current_step.validator:
                valid, error = current_step.validator(value)
                if not valid:
                    await message.answer(error)
                    return

            data = await state.get_data()
            form_data = data.get("form_data", {})
            form_data[current_step.field] = value
            await state.update_data(form_data=form_data)

            next_index = step_index + 1
            if next_index < len(current_flow["steps"]):
                next_step = current_flow["steps"][next_index]
                next_state = states[next_index]
                await state.update_data(step_index=next_index)
                await state.set_state(next_state)
                await message.answer(next_step.prompt)
                return

            formatted = render_submission(cat, form_data)
            await state.update_data(formatted_text=formatted)
            await state.set_state(None)
            await message.answer(
                "📋 <b>Post ko'rinishi:</b>\n\n"
                f"{formatted}\n\n"
                "Ma'lumotlarni tasdiqlaysizmi?",
                reply_markup=confirmation_keyboard(),
                parse_mode="HTML",
            )

        router.message.register(step_handler, fsm_state)


for category_key in FORM_FLOWS:
    _register_step_handlers(router, category_key)
