# tgbot/services/payment_processing.py
# Общие функции обработки платежей, используемые как webhook_handlers, так и operator_payment.

import logging
from datetime import datetime

from aiogram import Bot
from aiogram.types import User as TgUser, Chat, Message

from loader import config, logger
from database import requests as db
from marzban.init_client import MarzClientCache

log = logging.getLogger(__name__)


async def handle_user_payment(user_id: int, tariff, marzban: MarzClientCache) -> bool:
    """Продлевает подписку в БД и создаёт/модифицирует пользователя в Marzban.
    Возвращает True, если пользователь новый для Marzban."""
    await db.extend_user_subscription(user_id, days=tariff.duration_days)
    log.info(f"Subscription for user {user_id} extended by {tariff.duration_days} days.")

    user_from_db = await db.get_user(user_id)
    marzban_username = (user_from_db.marzban_username or f"user_{user_id}").lower()
    is_new_user = False
    try:
        if await marzban.get_user(marzban_username):
            await marzban.modify_user(username=marzban_username, expire_days=tariff.duration_days)
        else:
            await marzban.add_user(username=marzban_username, expire_days=tariff.duration_days)
            is_new_user = True
        if not user_from_db.marzban_username:
            await db.update_user_marzban_username(user_id, marzban_username)
    except Exception as e:
        log.error(f"CRITICAL: Failed to create/modify Marzban user {marzban_username}: {e}", exc_info=True)
    return is_new_user


async def handle_referral_bonus(user_who_paid_id: int, marzban: MarzClientCache, bot: Bot):
    """Проверяет и начисляет бонус рефереру (30 дней за первую оплату реферала)."""
    user_who_paid = await db.get_user(user_who_paid_id)
    if not (user_who_paid and user_who_paid.referrer_id and not user_who_paid.is_first_payment_made):
        return

    bonus_days = 30
    referrer = await db.get_user(user_who_paid.referrer_id)
    if not referrer:
        return

    if referrer.marzban_username:
        try:
            await marzban.modify_user(username=referrer.marzban_username, expire_days=bonus_days)
            await db.extend_user_subscription(referrer.user_id, days=bonus_days)
            await db.add_bonus_days(referrer.user_id, days=bonus_days)
            log.info(f"Referral bonus: extended subscription for referrer {referrer.user_id} by {bonus_days} days.")
            await bot.send_message(
                referrer.user_id,
                f"🎉 Ваш реферал совершил первую оплату! Вам начислено <b>{bonus_days} бонусных дней</b> подписки."
            )
        except Exception as e:
            log.error(f"Failed to apply referral bonus to user {referrer.user_id}: {e}")
            await db.add_bonus_days(referrer.user_id, days=bonus_days)
            try:
                await bot.send_message(referrer.user_id,
                    "Не удалось продлить вашу подписку, бонусные дни зачислены на ваш баланс.")
            except Exception:
                pass
    else:
        await db.add_bonus_days(referrer.user_id, days=bonus_days)
        log.info(f"Referral bonus: added {bonus_days} virtual bonus days to user {referrer.user_id}.")
        try:
            await bot.send_message(referrer.user_id,
                f"🎉 Ваш реферал совершил первую оплату! Вам начислено <b>{bonus_days} бонусных дней</b>.")
        except Exception:
            pass


async def log_transaction(
    bot: Bot, user_id: int, tariff_name: str, tariff_price: float, is_new_user: bool
):
    """Отправляет лог транзакции в тему для журнала платежей."""
    user = await db.get_user(user_id)
    if not user:
        return

    action_type = "💎 Новая подписка" if is_new_user else "🔄 Продление подписки"
    text = (
        f"{action_type}\n\n"
        f"👤 <b>Пользователь:</b> <a href='tg://user?id={user.user_id}'>{user.full_name}</a>\n"
        f"<b>ID:</b> <code>{user.user_id}</code>\n"
        f"<b>Username:</b> @{user.username or 'Отсутствует'}\n\n"
        f"💳 <b>Тариф:</b> «{tariff_name}»\n"
        f"💰 <b>Сумма:</b> {tariff_price} RUB"
    )
    try:
        await bot.send_message(
            chat_id=config.tg_bot.support_chat_id,
            message_thread_id=config.tg_bot.transaction_log_topic_id,
            text=text
        )
    except Exception as e:
        log.error(f"Failed to send transaction log for user {user_id}: {e}")


async def notify_user_payment_success(
    user_id: int, tariff, marzban: MarzClientCache, bot: Bot
):
    """Уведомляет пользователя об успешной активации и показывает профиль."""
    from tgbot.handlers.user.profile import show_profile_logic

    try:
        await bot.send_message(
            user_id,
            f"✅ Оплата прошла успешно! Ваш тариф «<b>{tariff.name}</b>» "
            f"активирован на <b>{tariff.duration_days} дней</b>."
        )
        fake_user = TgUser(id=user_id, is_bot=False, first_name="N/A")
        fake_chat = Chat(id=user_id, type="private")
        fake_message = Message(message_id=0, date=datetime.now(), chat=fake_chat, from_user=fake_user)
        await show_profile_logic(fake_message, marzban, bot)
    except Exception as e:
        log.error(f"Could not send payment success notification to user {user_id}: {e}")
