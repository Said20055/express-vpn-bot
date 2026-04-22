# tgbot/handlers/user/manual_payment.py
# Обработчики пользовательской стороны ручной оплаты:
# - пересылка чека оператору
# - отмена заявки пользователем

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from loader import config, logger
from database import requests as db
from tgbot.states.payment_states import ManualPaymentFSM
from tgbot.keyboards.inline import main_menu_keyboard, manual_payment_user_keyboard

manual_payment_router = Router()


@manual_payment_router.message(ManualPaymentFSM.awaiting_receipt)
async def forward_receipt_to_topic(message: Message, state: FSMContext, bot: Bot):
    """Пересылает сообщения пользователя в форум-тему оператора."""
    # Если пользователь вводит команду — выходим из состояния, но заявка остаётся
    if message.text and message.text.startswith('/'):
        await state.clear()
        await message.answer(
            "Вы вышли из режима ожидания подтверждения оплаты.\n\n"
            "Ваша заявка всё ещё активна — оператор рассмотрит её. "
            "Чтобы вернуться к заявке, напишите что-нибудь боту.",
            reply_markup=main_menu_keyboard()
        )
        return

    fsm_data = await state.get_data()
    payment_id = fsm_data.get("manual_payment_id")
    if not payment_id:
        await state.clear()
        await message.answer("Ошибка состояния. Пожалуйста, начните снова.", reply_markup=main_menu_keyboard())
        return

    mp = await db.get_manual_payment_by_id(payment_id)
    if not mp or mp.status != 'pending':
        await state.clear()
        await message.answer(
            "Ваша заявка уже обработана или не найдена.",
            reply_markup=main_menu_keyboard()
        )
        return

    try:
        await message.forward(
            chat_id=config.tg_bot.support_chat_id,
            message_thread_id=mp.topic_id
        )
        await message.answer("✅ Квитанция отправлена оператору. Ожидайте подтверждения.")
    except Exception as e:
        logger.error(f"Failed to forward receipt for payment {payment_id} to topic: {e}")
        await message.answer("Не удалось переслать сообщение оператору. Попробуйте ещё раз.")


@manual_payment_router.callback_query(
    F.data == "manual_payment_cancel_by_user",
    ManualPaymentFSM.awaiting_receipt
)
async def user_cancel_manual_payment(call: CallbackQuery, state: FSMContext, bot: Bot):
    """Пользователь отменяет свою заявку на ручную оплату."""
    fsm_data = await state.get_data()
    payment_id = fsm_data.get("manual_payment_id")
    await state.clear()

    if payment_id:
        mp = await db.get_manual_payment_by_id(payment_id)
        if mp and mp.status == 'pending':
            await db.update_manual_payment_status(payment_id, 'cancelled')
            try:
                await bot.send_message(
                    chat_id=config.tg_bot.support_chat_id,
                    message_thread_id=mp.topic_id,
                    text="ℹ️ Пользователь самостоятельно отменил заявку на ручную оплату."
                )
                if mp.operator_message_id:
                    await bot.edit_message_reply_markup(
                        chat_id=config.tg_bot.support_chat_id,
                        message_id=mp.operator_message_id,
                        reply_markup=None
                    )
            except Exception as e:
                logger.warning(f"Could not notify operator of user-cancelled payment {payment_id}: {e}")

    await call.message.edit_text(
        "❌ Заявка на ручную оплату отменена.\n\nВы можете создать новую заявку, выбрав тариф.",
        reply_markup=main_menu_keyboard()
    )
