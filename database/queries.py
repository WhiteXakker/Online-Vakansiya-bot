import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from database.models import BotSetting, MandatoryChannel, Submission, SubmissionStatus, User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    full_name: str | None,
) -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user:
        user.username = username
        user.full_name = full_name
        user.last_active = datetime.now(timezone.utc)
        await session.commit()
        return user

    user = User(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def is_user_banned(session: AsyncSession, telegram_id: int) -> bool:
    result = await session.execute(
        select(User.is_banned).where(User.telegram_id == telegram_id)
    )
    value = result.scalar_one_or_none()
    return bool(value)


async def set_user_ban(session: AsyncSession, telegram_id: int, banned: bool) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    user.is_banned = banned
    await session.commit()
    return user


async def find_user(session: AsyncSession, query: str) -> User | None:
    if query.isdigit():
        result = await session.execute(select(User).where(User.telegram_id == int(query)))
        user = result.scalar_one_or_none()
        if user:
            return user

    username = query.lstrip("@")
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_submission(
    session: AsyncSession,
    user_id: int,
    category: str,
    form_data: dict,
    formatted_text: str,
) -> Submission:
    submission = Submission(
        user_id=user_id,
        category=category,
        form_data=json.dumps(form_data, ensure_ascii=False),
        formatted_text=formatted_text,
        status=SubmissionStatus.PENDING,
    )
    session.add(submission)
    await session.commit()
    await session.refresh(submission)
    return submission


async def get_submission(session: AsyncSession, submission_id: int) -> Submission | None:
    result = await session.execute(select(Submission).where(Submission.id == submission_id))
    return result.scalar_one_or_none()


async def update_submission_status(
    session: AsyncSession,
    submission_id: int,
    status: str,
    *,
    rejection_reason: str | None = None,
    channel_message_id: int | None = None,
    moderation_message_id: int | None = None,
) -> Submission | None:
    submission = await get_submission(session, submission_id)
    if not submission:
        return None

    submission.status = status
    if rejection_reason is not None:
        submission.rejection_reason = rejection_reason
    if channel_message_id is not None:
        submission.channel_message_id = channel_message_id
    if moderation_message_id is not None:
        submission.moderation_message_id = moderation_message_id
    if status == SubmissionStatus.APPROVED:
        submission.posted_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(submission)
    return submission


async def get_stats(session: AsyncSession) -> dict:
    now = datetime.now(timezone.utc)
    active_since = now - timedelta(days=7)

    total_users = await session.scalar(select(func.count()).select_from(User))
    active_users = await session.scalar(
        select(func.count()).select_from(User).where(User.last_active >= active_since)
    )
    banned_users = await session.scalar(
        select(func.count()).select_from(User).where(User.is_banned.is_(True))
    )
    total_submissions = await session.scalar(select(func.count()).select_from(Submission))
    pending_posts = await session.scalar(
        select(func.count())
        .select_from(Submission)
        .where(Submission.status == SubmissionStatus.PENDING)
    )
    total_posted = await session.scalar(
        select(func.count())
        .select_from(Submission)
        .where(Submission.status == SubmissionStatus.APPROVED)
    )

    return {
        "total_users": total_users or 0,
        "active_users": active_users or 0,
        "banned_users": banned_users or 0,
        "total_submissions": total_submissions or 0,
        "pending_posts": pending_posts or 0,
        "total_posted": total_posted or 0,
    }


async def get_all_user_telegram_ids(session: AsyncSession) -> list[int]:
    result = await session.execute(
        select(User.telegram_id).where(User.is_banned.is_(False)).order_by(User.id)
    )
    return list(result.scalars().all())


async def get_setting(session: AsyncSession, key: str) -> str | None:
    result = await session.execute(select(BotSetting.value).where(BotSetting.key == key))
    return result.scalar_one_or_none()


async def set_setting(session: AsyncSession, key: str, value: str) -> None:
    result = await session.execute(select(BotSetting).where(BotSetting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = value
    else:
        session.add(BotSetting(key=key, value=value))
    await session.commit()


async def get_channel_id(session: AsyncSession) -> str:
    stored = await get_setting(session, "channel_id")
    return stored or settings.channel_id


async def set_channel_id(session: AsyncSession, channel_id: str) -> None:
    await set_setting(session, "channel_id", channel_id)


async def touch_user_activity(session: AsyncSession, telegram_id: int) -> None:
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(last_active=datetime.now(timezone.utc))
    )
    await session.commit()


# ── Admin management ──────────────────────────────────────────────────────────


async def user_has_admin_flag(session: AsyncSession, telegram_id: int) -> bool:
    result = await session.execute(
        select(User.is_admin).where(User.telegram_id == telegram_id)
    )
    value = result.scalar_one_or_none()
    return bool(value)


async def get_all_admins(session: AsyncSession) -> list[User]:
    result = await session.execute(
        select(User).where(User.is_admin.is_(True)).order_by(User.id)
    )
    return list(result.scalars().all())


async def set_user_admin(session: AsyncSession, telegram_id: int, is_admin: bool) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    user.is_admin = is_admin
    await session.commit()
    await session.refresh(user)
    return user


async def promote_user_to_admin(
    session: AsyncSession,
    telegram_id: int,
    username: str | None = None,
    full_name: str | None = None,
) -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user:
        user.is_admin = True
        if username:
            user.username = username
        if full_name:
            user.full_name = full_name
    else:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            is_admin=True,
        )
        session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def seed_env_admins(session: AsyncSession) -> None:
    for admin_id in settings.admin_ids:
        await promote_user_to_admin(session, admin_id)


async def count_admins(session: AsyncSession) -> int:
    value = await session.scalar(
        select(func.count()).select_from(User).where(User.is_admin.is_(True))
    )
    return value or 0


# ── Mandatory channels ────────────────────────────────────────────────────────


async def get_mandatory_channels(session: AsyncSession) -> list[MandatoryChannel]:
    result = await session.execute(
        select(MandatoryChannel).order_by(MandatoryChannel.id)
    )
    return list(result.scalars().all())


async def get_mandatory_channel(session: AsyncSession, channel_db_id: int) -> MandatoryChannel | None:
    result = await session.execute(
        select(MandatoryChannel).where(MandatoryChannel.id == channel_db_id)
    )
    return result.scalar_one_or_none()


async def add_mandatory_channel(
    session: AsyncSession,
    channel_id: str,
    channel_name: str,
    invite_link: str,
) -> MandatoryChannel:
    channel = MandatoryChannel(
        channel_id=channel_id,
        channel_name=channel_name,
        invite_link=invite_link,
    )
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return channel


async def delete_mandatory_channel(session: AsyncSession, channel_db_id: int) -> bool:
    channel = await get_mandatory_channel(session, channel_db_id)
    if not channel:
        return False
    await session.delete(channel)
    await session.commit()
    return True


async def mandatory_channel_exists(session: AsyncSession, channel_id: str) -> bool:
    result = await session.execute(
        select(MandatoryChannel.id).where(MandatoryChannel.channel_id == channel_id)
    )
    return result.scalar_one_or_none() is not None


async def count_mandatory_channels(session: AsyncSession) -> int:
    value = await session.scalar(select(func.count()).select_from(MandatoryChannel))
    return value or 0


# database/queries.py ichiga qo'shiladi

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import MandatoryChannel, AdminUser

# --- MAJBURIY OBUNA KANALLARI UCHUN ---
async def add_mandatory_channel(session: AsyncSession, channel_id: str, name: str, invite_link: str) -> MandatoryChannel:
    channel = MandatoryChannel(channel_id=str(channel_id), channel_name=name, invite_link=invite_link)
    session.add(channel)
    await session.commit()
    return channel

async def get_all_channels(session: AsyncSession):
    result = await session.execute(select(MandatoryChannel))
    return result.scalars().all()

async def delete_mandatory_channel(session: AsyncSession, channel_db_id: int) -> bool:
    result = await session.execute(select(MandatoryChannel).where(MandatoryChannel.id == channel_db_id))
    channel = result.scalar_one_or_none()
    if channel:
        await session.delete(channel)
        await session.commit()
        return True
    return False

# --- DINAMIK ADMINLAR UCHUN ---
async def add_admin_user(session: AsyncSession, telegram_id: int, full_name: str, username: str = None) -> AdminUser:
    admin = AdminUser(telegram_id=telegram_id, full_name=full_name, username=username)
    session.add(admin)
    await session.commit()
    return admin

async def get_all_admins(session: AsyncSession):
    result = await session.execute(select(AdminUser))
    return result.scalars().all()

async def delete_admin_user(session: AsyncSession, admin_db_id: int) -> bool:
    result = await session.execute(select(AdminUser).where(AdminUser.id == admin_db_id))
    admin = result.scalar_one_or_none()
    if admin:
        await session.delete(admin)
        await session.commit()
        return True
    return False

async def is_user_admin(session: AsyncSession, telegram_id: int) -> bool:
    # .env dagi asosiy admin har doim superadmin bo'lib qoladi
    from config.settings import settings
    if telegram_id in settings.admin_ids:
        return True
    
    result = await session.execute(select(AdminUser).where(AdminUser.telegram_id == telegram_id))
    return result.scalar_one_or_none() is not None