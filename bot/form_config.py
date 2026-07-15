from collections.abc import Callable
from dataclasses import dataclass

from database.models import SubmissionCategory
from bot.states.forms import (
    IshJoyiKerakForm,
    SherikKerakForm,
    ShogirdKerakForm,
    UstozKerakForm,
    XodimKerakForm,
)
from bot.utils.validators import validate_age, validate_non_empty, validate_phone, validate_telegram


@dataclass(frozen=True)
class FormStep:
    field: str
    prompt: str
    validator: Callable[[str], tuple[bool, str]] | None = None


FORM_FLOWS: dict[str, dict] = {
    SubmissionCategory.USTOZ_KERAK: {
        "title": "Ustoz kerak",
        "state_group": UstozKerakForm,
        "states": [
            UstozKerakForm.full_name,
            UstozKerakForm.age,
            UstozKerakForm.technologies,
            UstozKerakForm.telegram,
            UstozKerakForm.region,
            UstozKerakForm.contact_time,
            UstozKerakForm.purpose,
        ],
        "steps": [
            FormStep("full_name", "👤 To'liq ismingizni kiriting:", validate_non_empty),
            FormStep("age", "🌐 Yoshingizni kiriting:", validate_age),
            FormStep("technologies", "📚 Biladigan texnologiyalaringizni kiriting (vergul bilan):", validate_non_empty),
            FormStep("telegram", "🇺🇿 Telegram username yoki aloqa raqamingizni kiriting:", validate_telegram),
            FormStep("region", "🌐 Hududingizni kiriting:", validate_non_empty),
            FormStep("contact_time", "🕰 Murojaat qilish vaqtini kiriting:", validate_non_empty),
            FormStep("purpose", "🔎 Maqsadingizni kiriting:", validate_non_empty),
        ],
    },
    SubmissionCategory.ISH_JOYI_KERAK: {
        "title": "Ish joyi kerak",
        "state_group": IshJoyiKerakForm,
        "states": [
            IshJoyiKerakForm.full_name,
            IshJoyiKerakForm.age,
            IshJoyiKerakForm.technologies,
            IshJoyiKerakForm.telegram,
            IshJoyiKerakForm.phone,
            IshJoyiKerakForm.region,
            IshJoyiKerakForm.salary,
            IshJoyiKerakForm.profession,
            IshJoyiKerakForm.contact_time,
            IshJoyiKerakForm.purpose,
        ],
        "steps": [
            FormStep("full_name", "👤 To'liq ismingizni kiriting:", validate_non_empty),
            FormStep("age", "🕑 Yoshingizni kiriting:", validate_age),
            FormStep("technologies", "📚 Biladigan texnologiyalaringizni kiriting:", validate_non_empty),
            FormStep("telegram", "🇺🇿 Telegram username kiriting:", validate_telegram),
            FormStep("phone", "📞 Aloqa raqamingizni kiriting:", validate_phone),
            FormStep("region", "🌐 Hududingizni kiriting:", validate_non_empty),
            FormStep("salary", "💰 Maosh/kutilayotgan narxni kiriting:", validate_non_empty),
            FormStep("profession", "👨🏻‍💻 Kasbingizni kiriting:", validate_non_empty),
            FormStep("contact_time", "🕰 Murojaat qilish vaqtini kiriting:", validate_non_empty),
            FormStep("purpose", "🔎 O'zingiz haqingizda / maqsadingizni kiriting:", validate_non_empty),
        ],
    },
    SubmissionCategory.XODIM_KERAK: {
        "title": "Xodim kerak",
        "state_group": XodimKerakForm,
        "states": [
            XodimKerakForm.company_name,
            XodimKerakForm.technologies,
            XodimKerakForm.telegram,
            XodimKerakForm.phone,
            XodimKerakForm.region,
            XodimKerakForm.responsible_person,
            XodimKerakForm.contact_time,
            XodimKerakForm.working_hours,
            XodimKerakForm.salary,
            XodimKerakForm.additional_info,
        ],
        "steps": [
            FormStep("company_name", "🏢 Idora/kompaniya nomini kiriting:", validate_non_empty),
            FormStep("technologies", "📚 Kerakli texnologiyalarni kiriting:", validate_non_empty),
            FormStep("telegram", "🇺🇿 Telegram username kiriting:", validate_telegram),
            FormStep("phone", "📞 Aloqa raqamini kiriting:", validate_phone),
            FormStep("region", "🌐 Hududni kiriting:", validate_non_empty),
            FormStep("responsible_person", "✍️ Mas'ul shaxs ismini kiriting:", validate_non_empty),
            FormStep("contact_time", "🕰 Murojaat vaqtini kiriting:", validate_non_empty),
            FormStep("working_hours", "🕰 Ish vaqtini kiriting:", validate_non_empty),
            FormStep("salary", "💰 Maosh miqdorini kiriting:", validate_non_empty),
            FormStep("additional_info", "‼️ Qo'shimcha ma'lumot kiriting:", validate_non_empty),
        ],
    },
    SubmissionCategory.SHOGIRD_KERAK: {
        "title": "Shogird kerak",
        "state_group": ShogirdKerakForm,
        "states": [
            ShogirdKerakForm.mentor_name,
            ShogirdKerakForm.age,
            ShogirdKerakForm.technologies,
            ShogirdKerakForm.telegram,
            ShogirdKerakForm.phone,
            ShogirdKerakForm.region,
            ShogirdKerakForm.price,
            ShogirdKerakForm.profession,
            ShogirdKerakForm.contact_time,
            ShogirdKerakForm.purpose,
        ],
        "steps": [
            FormStep("mentor_name", "🎓 Ustoz (mentor) ismini kiriting:", validate_non_empty),
            FormStep("age", "🌐 Yoshingizni kiriting:", validate_age),
            FormStep("technologies", "📚 O'rgatadigan texnologiyalarni kiriting:", validate_non_empty),
            FormStep("telegram", "🇺🇿 Telegram username kiriting:", validate_telegram),
            FormStep("phone", "📞 Aloqa raqamini kiriting:", validate_phone),
            FormStep("region", "🌐 Hududni kiriting:", validate_non_empty),
            FormStep("price", "💰 Narxi/to'lov miqdorini kiriting:", validate_non_empty),
            FormStep("profession", "👨🏻‍💻 Kasbingizni kiriting:", validate_non_empty),
            FormStep("contact_time", "🕰 Murojaat qilish vaqtini kiriting:", validate_non_empty),
            FormStep("purpose", "🔎 Maqsad/mo'ljalni kiriting:", validate_non_empty),
        ],
    },
    SubmissionCategory.SHERIK_KERAK: {
        "title": "Sherik kerak",
        "state_group": SherikKerakForm,
        "states": [
            SherikKerakForm.partner_name,
            SherikKerakForm.technologies,
            SherikKerakForm.telegram,
            SherikKerakForm.region,
            SherikKerakForm.price,
            SherikKerakForm.profession,
            SherikKerakForm.contact_time,
            SherikKerakForm.purpose,
        ],
        "steps": [
            FormStep("partner_name", "🏅 Sherik nomi/ismini kiriting:", validate_non_empty),
            FormStep("technologies", "📚 Texnologiyalarni kiriting:", validate_non_empty),
            FormStep("telegram", "🇺🇿 Telegram username kiriting:", validate_telegram),
            FormStep("region", "🌐 Hududni kiriting:", validate_non_empty),
            FormStep("price", "💰 Narx/ulush miqdorini kiriting:", validate_non_empty),
            FormStep("profession", "👨🏻‍💻 Kasbingizni kiriting:", validate_non_empty),
            FormStep("contact_time", "🕰 Murojaat qilish vaqtini kiriting:", validate_non_empty),
            FormStep("purpose", "🔎 Maqsad/mo'ljalni kiriting:", validate_non_empty),
        ],
    },
}

MENU_TO_CATEGORY = {
    "Ustoz kerak": SubmissionCategory.USTOZ_KERAK,
    "Ish joyi kerak": SubmissionCategory.ISH_JOYI_KERAK,
    "Xodim kerak": SubmissionCategory.XODIM_KERAK,
    "Shogird kerak": SubmissionCategory.SHOGIRD_KERAK,
    "Sherik kerak": SubmissionCategory.SHERIK_KERAK,
}
