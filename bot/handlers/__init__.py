# bot/handlers/__init__.py

from aiogram import Router

# Barcha ichki modullarni faqat bir marta, nisbiy (relative) import orqali yuklaymiz
from . import start
from . import forms
from . import confirmation
from . import moderation
from . import subscription
from .admin import panel, broadcast, users

router = Router(name="main")

# Routerlarni dispatcher ko'radigan tartibda ulaymiz
router.include_router(start.router)
router.include_router(forms.router)
router.include_router(confirmation.router)
router.include_router(moderation.router)
router.include_router(subscription.router) # Obuna routerini shu yerda ulaymiz

# Admin routerlari
router.include_router(panel.router)
router.include_router(broadcast.router)
router.include_router(users.router)