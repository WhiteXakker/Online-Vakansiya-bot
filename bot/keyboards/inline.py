from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm:submit"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data="confirm:cancel"),
    )
    return builder.as_markup()


def moderation_keyboard(submission_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🟢 Qabul qilish",
            callback_data=f"mod:approve:{submission_id}",
        ),
        InlineKeyboardButton(
            text="🔴 Rad etish",
            callback_data=f"mod:reject:{submission_id}",
        ),
    )
    return builder.as_markup()


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats"))
    builder.row(InlineKeyboardButton(text="📢 Broadcast", callback_data="admin:broadcast"))
    builder.row(InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin:users"))
    builder.row(InlineKeyboardButton(text="👑 Adminlar", callback_data="admin:admins"))
    builder.row(InlineKeyboardButton(text="📌 Majburiy obuna", callback_data="admin:mandatory"))
    builder.row(InlineKeyboardButton(text="⚙️ Kanal sozlamalari", callback_data="admin:channel"))
    builder.row(InlineKeyboardButton(text="❌ Yopish", callback_data="admin:close"))
    return builder.as_markup()


def mandatory_channels_keyboard(channels: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for channel in channels:
        builder.row(
            InlineKeyboardButton(
                text=f"🗑 {channel.channel_name}",
                callback_data=f"admin:mandatory:del:{channel.id}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="admin:mandatory:add")
    )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin:back"))
    return builder.as_markup()


def admins_list_keyboard(admins: list, env_admin_ids: set[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for admin in admins:
        is_super = admin.telegram_id in env_admin_ids
        label = f"{'🔒' if is_super else '👤'} {admin.full_name or admin.username or admin.telegram_id}"
        if not is_super:
            builder.row(
                InlineKeyboardButton(
                    text=f"❌ {label}",
                    callback_data=f"admin:admins:revoke:{admin.telegram_id}",
                )
            )
        else:
            builder.row(
                InlineKeyboardButton(
                    text=label,
                    callback_data="admin:admins:noop",
                )
            )
    builder.row(InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="admin:admins:add"))
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin:back"))
    return builder.as_markup()


def user_management_keyboard(
    telegram_id: int,
    is_banned: bool,
    *,
    is_admin: bool = False,
    is_super_admin: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_banned:
        builder.row(
            InlineKeyboardButton(
                text="✅ Ban olib tashlash",
                callback_data=f"admin:unban:{telegram_id}",
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🚫 Ban qilish",
                callback_data=f"admin:ban:{telegram_id}",
            )
        )
    if not is_admin:
        builder.row(
            InlineKeyboardButton(
                text="👑 Admin qilish",
                callback_data=f"admin:admins:promote:{telegram_id}",
            )
        )
    elif not is_super_admin:
        builder.row(
            InlineKeyboardButton(
                text="❌ Adminlikni olib tashlash",
                callback_data=f"admin:admins:revoke:{telegram_id}",
            )
        )
    builder.row(InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin:users"))
    return builder.as_markup()


def broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Yuborish", callback_data="admin:broadcast:send"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:broadcast:cancel"),
    )
    return builder.as_markup()
