# tgbot/handlers/webhook_handlers.py

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiohttp import web
from aiogram import Bot, Dispatcher

from tgbot.services import payment
from tgbot.services.payment_processing import (
    handle_user_payment,
    handle_referral_bonus,
    log_transaction,
    notify_user_payment_success,
)
from database import requests as db
from loader import logger


# --- ГЛАВНЫЙ ХЕНДЛЕР ВЕБХУКА ---
async def yookassa_webhook_handler(request: web.Request):
    """Принимает вебхуки от YooKassa и обрабатывает успешные платежи."""
    try:
        request_body = await request.json()
        notification = payment.parse_webhook_notification(request_body)

        if notification is None or notification.event != 'payment.succeeded':
            return web.Response(status=400)

        metadata = notification.object.metadata
        user_id = int(metadata['user_id'])
        tariff_id = int(metadata['tariff_id'])
        tariff = await db.get_tariff_by_id(tariff_id)
        user_from_db = await db.get_user(user_id)
        is_first_payment = not user_from_db.is_first_payment_made

        if not tariff:
            logger.error(f"Webhook for non-existent tariff_id: {tariff_id}")
            return web.Response(status=400)

        logger.info(f"Webhook: processing successful payment for user {user_id}, tariff '{tariff.name}'.")

        bot: Bot = request.app['bot']
        marzban = request.app['marzban']

        is_new = await handle_user_payment(user_id, tariff, marzban)
        await handle_referral_bonus(user_id, marzban, bot)
        await log_transaction(bot=bot, user_id=user_id, tariff_name=tariff.name,
                              tariff_price=tariff.price, is_new_user=is_new)

        # Очистить FSM и старое сообщение с платёжной ссылкой
        try:
            dp: Dispatcher = request.app['dp']
            storage_key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
            state = FSMContext(storage=dp.storage, key=storage_key)
            fsm_data = await state.get_data()
            payment_message_id = fsm_data.get("payment_message_id")
            if payment_message_id:
                await bot.edit_message_text(
                    chat_id=user_id,
                    message_id=payment_message_id,
                    text="✅ <i>Этот счет был успешно оплачен.</i>",
                    reply_markup=None
                )
            await state.clear()
        except Exception as e:
            logger.error(f"Could not clear state or edit payment message for user {user_id}: {e}")

        await notify_user_payment_success(user_id, tariff, marzban, bot)

        if is_first_payment:
            await db.set_first_payment_done(user_id)
            logger.info(f"Marked first payment for user {user_id}.")

        return web.Response(status=200)

    except Exception as e:
        logger.error(f"FATAL: Unhandled error in yookassa_webhook_handler: {e}", exc_info=True)
        return web.Response(status=500)
