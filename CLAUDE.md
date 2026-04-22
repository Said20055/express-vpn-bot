# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram VPN bot that sells subscriptions via YooKassa payments, manages VPN keys through the Marzban panel (Shadowsocks/VLESS/VMess), and stores user/subscription data in PostgreSQL. Written in Python with aiogram 3.x.

## Running the Project

**Production (Docker):**
```bash
cp env.dist .env
cp env.marzban.dist .env.marzban
# Fill in .env and .env.marzban with real values
./refresh.sh  # builds and starts all services
```

**Local development (polling mode):**
```bash
pip install -r requirements.txt
# Set USE_WEBHOOK=False in .env
python3 -m bot
```

The bot runs in two modes controlled by `USE_WEBHOOK` in `.env`:
- `False` → polling mode (port 8081 for YooKassa webhooks)
- `True` → webhook mode via aiohttp on port 8080, behind nginx

**Marzban dashboard:** `https://localhost:8002/dashboard/`

## Environment Setup

Two env files are required:
- `.env` (from `env.dist`) — bot token, DB credentials, YooKassa keys, domain, webhook settings
- `.env.marzban` (from `env.marzban.dist`) — Marzban admin credentials

Key `.env` variables:
- `BOT_TOKEN` — Telegram bot token
- `ADMINS` — comma-separated list of admin Telegram IDs (e.g. `123,456`)
- `SUPPORT_CHAT_ID` — Telegram group ID for support tickets (forum topics)
- `TRANSACTION_LOG_TOPIC_ID` — topic ID within the support group for payment logs
- `USE_WEBHOOK` — `True` for production, `False` for local dev
- `MARZ_HAS_CERTIFICATE` — whether Marzban uses TLS

## Architecture

### Initialization chain
`bot.py` → `loader.py` (creates `bot`, `config`, `logger`, `marzban_client`) → handlers/services

`loader.py` is the central DI module. Everything imports from it rather than constructing their own instances.

### Key layers

**`config.py`** — dataclass-based config loaded from `.env` / `.env.marzban` via `environs`.

**`db.py`** — SQLAlchemy 2.0 ORM models (`User`, `Tariff`, `PromoCode`, `UsedPromoCode`, `Channel`) with `async_session_maker` for all DB access. Tables are created synchronously at startup via `setup_database_sync()`.

**`database/requests.py`** — all DB query functions (no raw SQL). Always import from here rather than using `async_session_maker` directly in handlers.

**`marzban/init_client.py`** — `MarzClientCache` wraps the Marzban REST API with auto-refreshing JWT tokens. Exposes `add_user`, `get_user`, `modify_user` (create-or-extend), `delete_user`, `get_system_stats`, `get_nodes`, etc.

**`marzban/client.py`** — higher-level helpers using `marzban-api-client` SDK: `create_user`, `get_user_links`, `delete_users`. Note: two Marzban access patterns exist — `MarzClientCache` (httpx-based, preferred for new code) and the `marzban-api-client` SDK.

**`tgbot/handlers/`** — aiogram routers organized by:
- `user/` — start, profile, payment, instruction, trial subscription
- `admin/` — broadcast, tariff management, promo codes, channels, user management
- `support.py` — forum-topic based support tickets
- `webhook_handlers.py` — YooKassa payment webhook handler

Router registration order in `tgbot/handlers/__init__.py` matters: `support_router` → `admin_router` → `user_router`.

**`tgbot/services/`**:
- `payment.py` — YooKassa payment creation and webhook parsing
- `subscription.py` — checks if user is subscribed to required Telegram channels
- `scheduler.py` — APScheduler jobs (subscription expiry reminders at 7 days, 3 days, <24 hours)
- `qr_generator.py` — generates QR codes for VPN keys

**`tgbot/middlewares/`** — `ThrottlingMiddleware` (flood protection), `CallbackAnswerMiddleware`, `SupportTimeoutMiddleware`.

**`tgbot/keyboards/callback_data_factory.py`** — aiogram `CallbackData` factories for typed callback routing.

**`utils/broadcaster.py`** — sends messages to multiple users (admin broadcasts).

**`utils/logger.py`** — `APINotificationHandler` sends `ERROR`+ logs to the main admin via Telegram API.

### Payment flow
1. User selects tariff → `create_payment()` returns YooKassa redirect URL
2. User pays → YooKassa POSTs to `/yookassa` endpoint
3. `yookassa_webhook_handler` in `webhook_handlers.py` processes the event
4. On `payment.succeeded`: extends subscription in DB + calls `marzban_client.modify_user()` to update Marzban expiry

### Marzban user naming
Marzban usernames are stored in `User.marzban_username` (set once on first subscription). Usernames are lowercased before all Marzban API calls.

## Docker Services

| Service | Container | Port |
|---------|-----------|------|
| Bot | `free_vpn_bot` | — |
| Marzban | `free_vpn_bot_marzban` | 8002 (internal), 2053, 8443 |
| PostgreSQL | `vpn_bot_postgres` | internal only |
| Nginx | `free_vpn_bot_nginx` | 80, 443 |

All services share the `free_vpn_bot` bridge network. The bot connects to Marzban internally as `https://free_vpn_bot_marzban:8002` in polling mode.
