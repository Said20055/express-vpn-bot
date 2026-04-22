# tgbot/handlers/operator_payment.py
# Обработчики кнопок «Подтвердить» / «Отклонить» в форум-теме поддержки.
# Зарегистрирован на верхнем уровне (не внутри user_router или admin_router),
# так как колбэки приходят из групповой форум-темы, а не из приватного чата.

from aiogram import Router, F, Bot
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, StorageKey
from aiogram.types import CallbackQuery

from loader import config, logger
from database import requests as db
from tgbot.services.payment_processing import (
    handle_user_payment,
    handle_referral_bonus,
    log_transaction,
    notify_user_payment_success,
)
from tgbot.keyboards.inline import main_menu_keyboard

operator_payment_router = Router()


class IsAdmin(Filter):
    """Разрешает действие только администраторам из списка в конфиге."""
    async def __call__(self, call: CallbackQuery) -> bool:
        return call.from_user.id in config.tg_bot.admin_ids


@operator_payment_router.callback_query(F.data.startswith("mp_confirm_"), IsAdmin())
async def operator_confirm_payment(
    call: CallbackQuery, bot: Bot, marzban, fsm_storage: BaseStorage
):
    """Оператор подтверждает оплату — активирует подписку пользователя."""
    await call.answer("Обрабатываю подтверждение...")

    payment_id = int(call.data.split("_")[2])

    # Атомарное подтверждение: только один оператор может подтвердить
    confirmed = await db.confirm_manual_payment_atomic(payment_id)
    if not confirmed:
        await call.answer("Эта заявка уже обработана другим оператором.", show_alert=True)
        try:
            await call.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        return

    mp = await db.get_manual_payment_by_id(payment_id)
    if not mp:
        logger.error(f"Manual payment {payment_id} not found after atomic confirm.")
        return

    tariff = await db.get_tariff_by_id(mp.tariff_id)
    if not tariff:
        logger.error(f"Tariff {mp.tariff_id} not found for manual payment {payment_id}.")
        await call.answer("Тариф не найден — данные повреждены.", show_alert=True)
        return

    user_from_db = await db.get_user(mp.user_id)
    is_first_payment = not user_from_db.is_first_payment_made

    # Запускаем тот же pipeline, что и при YooKassa-оплате
    try:
        is_new = await handle_user_payment(mp.user_id, tariff, marzban)
        await handle_referral_bonus(mp.user_id, marzban, bot)
        await log_transaction(
            bot=bot,
            user_id=mp.user_id,
            tariff_name=tariff.name,
            tariff_price=mp.final_price,
            is_new_user=is_new
        )
        if is_first_payment:
            await db.set_first_payment_done(mp.user_id)
        await notify_user_payment_success(mp.user_id, tariff, marzban, bot)
    except Exception as e:
        logger.error(f"Error processing confirmed manual payment {payment_id}: {e}", exc_info=True)
        await call.answer("Подписка подтверждена, но возникла ошибка при активации. Проверьте логи.",
                          show_alert=True)

    # Явно очищаем FSM пользователя (он мог ждать в awaiting_receipt)
    try:
        user_state = FSMContext(
            storage=fsm_storage,
            key=StorageKey(bot_id=bot.id, chat_id=mp.user_id, user_id=mp.user_id)
        )
        await user_state.clear()
    except Exception as e:
        logger.warning(f"Could not clear FSM for user {mp.user_id} after manual payment confirm: {e}")

    # Редактируем сообщение оператора: убираем кнопки, добавляем пометку
    operator_name = call.from_user.username or str(call.from_user.id)
    try:
        await call.message.edit_text(
            call.message.text + f"\n\n✅ <b>ПОДТВЕРЖДЕНО</b> @{operator_name}",
            reply_markup=None
        )
    except Exception as e:
        logger.warning(f"Could not edit operator confirmation message: {e}")

    await call.answer("✅ Подписка успешно активирована!", show_alert=True)


@operator_payment_router.callback_query(F.data.startswith("mp_cancel_"), IsAdmin())
async def operator_cancel_payment(
    call: CallbackQuery, bot: Bot, fsm_storage: BaseStorage
):
    """Оператор отклоняет заявку на ручную оплату."""
    await call.answer("Отклоняю заявку...")

    payment_id = int(call.data.split("_")[2])
    mp = await db.get_manual_payment_by_id(payment_id)

    if not mp:
        await call.answer("Заявка не найдена.", show_alert=True)
        return

    if mp.status != 'pending':
        await call.answer(f"Заявка уже обработана (статус: {mp.status}).", show_alert=True)
        try:
            await call.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        return

    await db.update_manual_payment_status(payment_id, 'cancelled')

    # Уведомляем пользователя
    try:
        await bot.send_message(
            mp.user_id,
            "❌ <b>Ваш платёж был отклонён оператором.</b>\n\n"
            "Если вы считаете это ошибкой — обратитесь в поддержку.",
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        logger.warning(f"Could not send cancellation notice to user {mp.user_id}: {e}")

    # Очищаем FSM пользователя
    try:
        user_state = FSMContext(
            storage=fsm_storage,
            key=StorageKey(bot_id=bot.id, chat_id=mp.user_id, user_id=mp.user_id)
        )
        await user_state.clear()
    except Exception as e:
        logger.warning(f"Could not clear FSM for user {mp.user_id} after manual payment cancel: {e}")

    # Редактируем сообщение оператора
    operator_name = call.from_user.username or str(call.from_user.id)
    try:
        await call.message.edit_text(
            call.message.text + f"\n\n❌ <b>ОТКЛОНЕНО</b> @{operator_name}",
            reply_markup=None
        )
    except Exception as e:
        logger.warning(f"Could not edit operator cancellation message: {e}")

    await call.answer("❌ Платёж отклонён.", show_alert=True)
