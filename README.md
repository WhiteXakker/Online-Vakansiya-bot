# Ustoz-Shogird Telegram Bot

Production-ready Telegram bot for the Ustoz-Shogird IT community platform. Connects mentors, students, job seekers, employers, and partners through structured FSM forms, admin moderation, and channel publishing.

## Features

- **5 FSM form flows**: Ustoz kerak, Ish joyi kerak, Xodim kerak, Shogird kerak, Sherik kerak
- **Input validation** for age, phone, Telegram username, and required fields
- **Preview & confirmation** before submission
- **Admin moderation** with approve/reject workflow
- **Auto hashtag generation** from technologies and region
- **Admin panel** (`/admin`):
  - Real-time statistics
  - Smart broadcast with progress bar and throttling
  - User search, ban/unban
  - Channel ID configuration

## Tech Stack

- Python 3.10+
- [aiogram 3.x](https://docs.aiogram.dev/)
- SQLAlchemy 2.x (SQLite dev / PostgreSQL prod)
- Redis FSM storage (optional, for production)
- pydantic-settings for `.env` config

## Project Structure

```
ustoz-shogird-bot/
├── main.py                 # Entry point
├── config/settings.py      # Environment configuration
├── database/
│   ├── models.py           # SQLAlchemy models
│   ├── queries.py          # Database operations
│   └── base.py             # Engine & session
├── bot/
│   ├── factory.py          # Bot & dispatcher setup
│   ├── form_config.py      # Form step definitions
│   ├── states/             # FSM state groups
│   ├── keyboards/          # Reply & inline keyboards
│   ├── handlers/           # Message & callback handlers
│   ├── middlewares/        # DB session & ban check
│   └── utils/              # Templates, validators, hashtags
├── requirements.txt
└── .env.example
```

## Quick Start

### 1. Clone & install

```bash
cd Projects/ustoz-shogird-bot
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
copy .env.example .env
```

Edit `.env`:

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Token from [@BotFather](https://t.me/BotFather) |
| `ADMIN_IDS` | Comma-separated Telegram user IDs |
| `CHANNEL_ID` | Target channel (`@username` or numeric ID) |
| `MODERATION_CHAT_ID` | Optional group/chat for moderation queue |
| `DATABASE_URL` | SQLite or PostgreSQL connection string |
| `FSM_STORAGE` | `memory` (dev) or `redis` (prod) |

### 3. Bot permissions

1. Add the bot as **admin** to your target channel (with post permission).
2. Add the bot to your moderation group (if using `MODERATION_CHAT_ID`).
3. Get your Telegram user ID via [@userinfobot](https://t.me/userinfobot).

### 4. Run

```bash
python main.py
```

## Production Notes

**PostgreSQL:**

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ustoz_shogird
```

**Redis FSM:**

```env
FSM_STORAGE=redis
REDIS_URL=redis://localhost:6379/0
```

**Broadcast throttling** — adjust `BROADCAST_DELAY` (default `0.05` seconds) to stay under Telegram rate limits.

## User Flow

1. `/start` → main menu (5 options)
2. Step-by-step form with validation
3. Preview → ✅ Tasdiqlash / ❌ Rad etish
4. Admin receives post with 🟢 Qabul qilish / 🔴 Rad etish
5. On approval → published to channel + user notified

## Admin Commands

| Command | Description |
|---------|-------------|
| `/admin` | Open admin panel (admins only) |
| `/skip` | Skip rejection reason (during moderation) |
| `/cancel` | Cancel broadcast or user search |

## License

MIT
