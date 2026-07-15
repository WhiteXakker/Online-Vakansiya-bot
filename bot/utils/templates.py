from database.models import SubmissionCategory
from bot.utils.hashtags import format_telegram_contact, generate_region_tag, generate_tech_tags

CHANNEL_LINK = "👉 <b>@OnlineVakansiyaUz</b> kanaliga ulanish"


def _footer(technologies: str, region: str, main_tag: str) -> str:
    tech_tags = generate_tech_tags(technologies)
    region_tag = generate_region_tag(region)
    return f"\n\n{main_tag} {tech_tags} {region_tag}\n\n{CHANNEL_LINK}".rstrip()


def render_ustoz_kerak(data: dict) -> str:
    telegram = format_telegram_contact(data["telegram"])
    body = (
        f"<b>Ustoz kerak:</b>\n\n"
        f"🎓 <b>Shogird:</b> {data['full_name']}\n"
        f"🌐 <b>Yosh:</b> {data['age']}\n"
        f"📚 <b>Texnologiya:</b> {data['technologies']}\n"
        f"🇺🇿 <b>Telegram:</b> {telegram}\n"
        f"🌐 <b>Hudud:</b> {data['region']}\n"
        f"🕰 <b>Murojaat qilish vaqti:</b> {data['contact_time']}\n"
        f"🔎 <b>Maqsad:</b> <i>{data['purpose']}</i>"
    )
    return body + _footer(data["technologies"], data["region"], "#shogird")


def render_ish_joyi_kerak(data: dict) -> str:
    telegram = format_telegram_contact(data["telegram"])
    body = (
        f"<b>Ish joyi kerak:</b>\n\n"
        f"👨‍💼 <b>Xodim:</b> {data['full_name']}\n"
        f"🕑 <b>Yosh:</b> {data['age']}\n"
        f"📚 <b>Texnologiya:</b> {data['technologies']}\n"
        f"🇺🇿 <b>Telegram:</b> {telegram}\n"
        f"📞 <b>Aloqa:</b> <code>{data['phone']}</code>\n"
        f"🌐 <b>Hudud:</b> {data['region']}\n"
        f"💰 <b>Narxi:</b> {data['salary']}\n"
        f"👨🏻‍💻 <b>Kasbi:</b> {data['profession']}\n"
        f"🕰 <b>Murojaat qilish vaqti:</b> {data['contact_time']}\n"
        f"🔎 <b>Maqsad:</b> <i>{data['purpose']}</i>"
    )
    return body + _footer(data["technologies"], data["region"], "#xodim")


def render_xodim_kerak(data: dict) -> str:
    telegram = format_telegram_contact(data["telegram"])
    body = (
        f"<b>Xodim kerak:</b>\n\n"
        f"🏢 <b>Idora:</b> {data['company_name']}\n"
        f"📚 <b>Texnologiya:</b> {data['technologies']}\n"
        f"🇺🇿 <b>Telegram:</b> {telegram}\n"
        f"📞 <b>Aloqa:</b> <code>{data['phone']}</code>\n"
        f"🌐 <b>Hudud:</b> {data['region']}\n"
        f"✍️ <b>Mas'ul:</b> {data['responsible_person']}\n"
        f"🕰 <b>Murojaat vaqti:</b> {data['contact_time']}\n"
        f"🕰 <b>Ish vaqti:</b> {data['working_hours']}\n"
        f"💰 <b>Maosh:</b> {data['salary']}\n"
        f"‼️ <b>Qo'shimcha:</b> <i>{data['additional_info']}</i>"
    )
    return body + _footer(data["technologies"], data["region"], "#ishJoyi")


def render_shogird_kerak(data: dict) -> str:
    telegram = format_telegram_contact(data["telegram"])
    body = (
        f"<b>SHogird kerak:</b>\n\n"
        f"🎓 <b>Ustoz:</b> {data['mentor_name']}\n"
        f"🌐 <b>Yosh:</b> {data['age']}\n"
        f"📚 <b>Texnologiya:</b> {data['technologies']}\n"
        f"🇺🇿 <b>Telegram:</b> {telegram}\n"
        f"📞 <b>Aloqa:</b> <code>{data['phone']}</code>\n"
        f"🌐 <b>Hudud:</b> {data['region']}\n"
        f"💰 <b>Narxi:</b> {data['price']}\n"
        f"👨🏻‍💻 <b>Kasbi:</b> {data['profession']}\n"
        f"🕰 <b>Murojaat qilish vaqti:</b> {data['contact_time']}\n"
        f"🔎 <b>Maqsad:</b> <i>{data['purpose']}</i>"
    )
    return body + _footer(data["technologies"], data["region"], "#shogird")


def render_sherik_kerak(data: dict) -> str:
    telegram = format_telegram_contact(data["telegram"])
    body = (
        f"<b>Sherik kerak:</b>\n\n"
        f"🏅 <b>Sherik:</b> {data['partner_name']}\n"
        f"📚 <b>Texnologiya:</b> {data['technologies']}\n"
        f"🇺🇿 <b>Telegram:</b> {telegram}\n"
        f"🌐 <b>Hudud:</b> {data['region']}\n"
        f"💰 <b>Narxi:</b> {data['price']}\n"
        f"👨🏻‍💻 <b>Kasbi:</b> {data['profession']}\n"
        f"🕰 <b>Murojaat qilish vaqti:</b> {data['contact_time']}\n"
        f"🔎 <b>Maqsad:</b> <i>{data['purpose']}</i>"
    )
    return body + _footer(data["technologies"], data["region"], "#sherik")


RENDERERS = {
    SubmissionCategory.USTOZ_KERAK: render_ustoz_kerak,
    SubmissionCategory.ISH_JOYI_KERAK: render_ish_joyi_kerak,
    SubmissionCategory.XODIM_KERAK: render_xodim_kerak,
    SubmissionCategory.SHOGIRD_KERAK: render_shogird_kerak,
    SubmissionCategory.SHERIK_KERAK: render_sherik_kerak,
}


def render_submission(category: str, data: dict) -> str:
    renderer = RENDERERS.get(category)
    if not renderer:
        raise ValueError(f"Unknown category: {category}")
    return renderer(data)