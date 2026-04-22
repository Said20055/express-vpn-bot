# tgbot/handlers/user/payment.py (Полная, исправленная и оптимизированная версия)

from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from loader import logger, config
from database import requests as db
from marzban.init_client import MarzClientCache
from tgbot.handlers.user.profile import show_profile_logic
from tgbot.keyboards.inline import (
    cancel_fsm_keyboard, tariffs_keyboard, back_to_main_menu_keyboard,
    manual_payment_user_keyboard, operator_manual_payment_keyboard,
)
from tgbot.services import payment
from tgbot.states.payment_states import ManualPaymentFSM
from tgbot.states.support_states import SupportFSM

payment_router = Router()

# --- Состояния FSM ---
class PromoApplyFSM(StatesGroup):
    awaiting_code = State()

# =============================================================================
# --- БЛОК 1: ПОКАЗ ТАРИФОВ ---
# =============================================================================

async def show_tariffs_logic(event: Message | CallbackQuery, state: FSMContext):
    """Универсальная логика для показа списка тарифов."""
    fsm_data = await state.get_data()
    discount = fsm_data.get("discount")
    
    active_tariffs = await db.get_active_tariffs()
    tariffs_list = list(active_tariffs) if active_tariffs else []

    text = "Пожалуйста, выберите тарифный план:"
    if discount:
        text = f"✅ Промокод на <b>{discount}%</b> применен!\n\n" + text

    reply_markup = tariffs_keyboard(tariffs_list, promo_procent=discount or 0)

    if not tariffs_list:
        text = "К сожалению, сейчас нет доступных тарифов для покупки."
        reply_markup = back_to_main_menu_keyboard()
    
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=reply_markup)
    else:
        await event.answer(text, reply_markup=reply_markup)

@payment_router.message(Command("payment"))
async def payment_command_handler(message: Message, state: FSMContext):
    await show_tariffs_logic(message, state)

@payment_router.callback_query(F.data == "buy_subscription")
async def buy_subscription_callback_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await show_tariffs_logic(call, state)

# =============================================================================
# --- БЛОК 2: ПРИМЕНЕНИЕ ПРОМОКОДА ---
# =============================================================================


@payment_router.callback_query(F.data.startswith("apply_promo_"))
async def apply_promo_from_broadcast(call: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку с промокодом из рассылки.
    Применяет скидку и показывает меню тарифов.
    """
    await call.answer() # Сразу отвечаем, чтобы убрать "часики"
    
    try:
        promo_code = call.data.split("_")[2]
    except IndexError:
        await call.answer("Ошибка в данных промокода.", show_alert=True)
        return

    promo = await db.get_promo_code(promo_code)
    user_id = call.from_user.id

    # --- Валидация промокода ---
    
    # Отдельно обрабатываем случай, когда пользователь уже использовал код
    if promo and await db.has_user_used_promo(user_id, promo.id):
        # Отправляем информативное сообщение и сразу показываем тарифы без скидки
        await call.message.edit_text(
            "❗️ <b>Вы уже использовали этот промокод.</b>\n\n"
            "Каждый промокод можно использовать только один раз.\n"
            "Пожалуйста, выберите тариф по стандартной цене:",
            reply_markup=tariffs_keyboard(list(await db.get_active_tariffs()))
        )
        return

    # Остальные проверки
    error_text = None
    if not promo:
        error_text = "Промокод не найден."
    elif promo.discount_percent == 0:
        error_text = "Этот промокод дает бонусные дни, а не скидку. Введите его вручную в разделе «Промокод»."
    elif promo.uses_left <= 0:
        error_text = "К сожалению, этот промокод уже закончился."
    elif promo.expire_date and datetime.now() > promo.expire_date:
        error_text = "Срок действия этого промокода истек."
    
    if error_text:
        await call.answer(error_text, show_alert=True)
        return

    # --- Применение промокода и показ тарифов ---
    try:
        # Отмечаем, что пользователь использовал промокод
        await db.use_promo_code(user_id, promo)
        
        # Сохраняем скидку в FSM для следующего шага
        await state.set_state(None)
        await state.update_data(discount=promo.discount_percent, promo_code=promo_code)
        
        # Вызываем нашу универсальную функцию для показа тарифов со скидкой
        await show_tariffs_logic(call, state)

    except Exception as e:
        logger.error(f"Error applying promo code '{promo_code}' for user {user_id}: {e}", exc_info=True)
        await call.answer("Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.", show_alert=True)

async def _start_promo_input(event: Message | CallbackQuery, state: FSMContext):
    """
    Универсальная функция для начала сценария ввода промокода.
    """
    await state.set_state(PromoApplyFSM.awaiting_code)
    
    text = "Введите ваш промокод:"
    # Кнопка "Отмена" будет возвращать пользователя к списку тарифов
    reply_markup = back_to_main_menu_keyboard()

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=reply_markup)
    else: # если это Message
        await event.answer(text, reply_markup=reply_markup)


@payment_router.message(Command("promo"))
async def promo_command_handler(message: Message, state: FSMContext):
    """Начинает сценарий ввода промокода по команде."""
    # Просто вызываем нашу универсальную функцию
    await _start_promo_input(message, state)


# --- ОБНОВЛЕННЫЙ хендлер для кнопки "Ввести промокод" ---
@payment_router.callback_query(F.data == "enter_promo_code")
async def enter_promo_callback_handler(call: CallbackQuery, state: FSMContext):
    """Начинает сценарий ввода промокода по кнопке."""
    await call.answer()
    # Просто вызываем нашу универсальную функцию
    await _start_promo_input(call, state)
        
@payment_router.message(PromoApplyFSM.awaiting_code)
async def process_promo_code(message: Message, state: FSMContext, bot: Bot, marzban: MarzClientCache):
    """Обрабатывает введенный промокод."""
    code = message.text.upper()
    promo = await db.get_promo_code(code)
    user_id = message.from_user.id

    await message.delete() # Сразу удаляем сообщение с кодом

    error_text = None
    if not promo: error_text = "Промокод не найден."
    elif promo.uses_left <= 0: error_text = "Этот промокод уже закончился."
    elif promo.expire_date and promo.expire_date < datetime.now(): error_text = "Срок действия этого промокода истек."
    elif await db.has_user_used_promo(user_id, promo.id): error_text = "Вы уже использовали этот промокод."

    if error_text:
        await message.answer(error_text)
        return

    await db.use_promo_code(user_id, promo)

    if promo.bonus_days > 0:
        await state.clear()
        user_from_db = await db.get_user(user_id) # Получаем юзера один раз
        marzban_username = (user_from_db.marzban_username or f"user_{user_id}").lower()
        
        try:
            # --- ИСПРАВЛЕНО: Используем наш "умный" метод modify_user ---
            await marzban.modify_user(username=marzban_username, expire_days=promo.bonus_days)
            
            # Обновляем наши локальные данные ТОЛЬКО после успешной операции в Marzban
            await db.extend_user_subscription(user_id, promo.bonus_days)
            if not user_from_db.marzban_username:
                await db.update_user_marzban_username(user_id, marzban_username)
            
            await message.answer(f"✅ Промокод успешно применен! Вам начислено <b>{promo.bonus_days} бонусных дней</b>.")
            # Показываем обновленный профиль
            await show_profile_logic(message, marzban, bot)

        except Exception as e:
            logger.error(f"Failed to apply bonus days for promo code {code} for user {user_id}: {e}", exc_info=True)
            await message.answer("❌ Произошла ошибка при начислении бонусных дней. Обратитесь в поддержку.")
    
    elif promo.discount_percent > 0:
        # Сохраняем скидку в состояние и показываем тарифы
        await state.set_state(None) # Выходим из состояния ввода промокода
        await state.update_data(discount=promo.discount_percent, promo_code=code)
        await show_tariffs_logic(message, state)

# =============================================================================
# --- БЛОК 3: ВЫБОР ТАРИФА И СОЗДАНИЕ ПЛАТЕЖА ---
# =============================================================================

@payment_router.callback_query(F.data.startswith("select_tariff_"))
async def select_tariff_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    """Обрабатывает выбор тарифа: ветвится на ручную оплату или YooKassa."""
    await call.answer()

    tariff_id = int(call.data.split("_")[2])
    tariff = await db.get_tariff_by_id(tariff_id)
    if not tariff:
        await call.message.edit_text("Ошибка! Тариф не найден.", reply_markup=back_to_main_menu_keyboard())
        return

    fsm_data = await state.get_data()
    discount_percent = fsm_data.get("discount")
    promo_code = fsm_data.get("promo_code")
    final_price = round(tariff.price * (1 - discount_percent / 100), 2) if discount_percent else tariff.price

    if await db.is_manual_payment_enabled():
        await _start_manual_payment_flow(call, state, bot, tariff, final_price, discount_percent, promo_code)
    else:
        await _start_yookassa_flow(call, state, bot, tariff, final_price, discount_percent, promo_code)


async def _start_yookassa_flow(
    call: CallbackQuery, state: FSMContext, bot: Bot,
    tariff, final_price: float, discount_percent, promo_code
):
    """Создаёт платёж YooKassa и показывает ссылку на оплату."""
    if discount_percent:
        price_text = (
            f"<s>{tariff.price} RUB</s>\n"
            f"Скидка {discount_percent}% ({promo_code}): <b>{final_price} RUB</b>"
        )
    else:
        price_text = f"<b>{tariff.price} RUB</b>"

    payment_url, _ = payment.create_payment(
        user_id=call.from_user.id,
        amount=final_price,
        description=f"Оплата тарифа '{tariff.name}'" + (f" (скидка {discount_percent}%)" if discount_percent else ""),
        bot_username=(await bot.get_me()).username,
        metadata={'user_id': str(call.from_user.id), 'tariff_id': tariff.id}
    )

    payment_kb = InlineKeyboardBuilder()
    payment_kb.button(text="💳 Перейти к оплате", url=payment_url)
    payment_kb.button(text="⬅️ Назад к выбору тарифа", callback_data="buy_subscription")
    payment_kb.adjust(1)

    sent_message = await call.message.edit_text(
        f"Вы выбрали тариф: <b>{tariff.name}</b>\n"
        f"Срок: <b>{tariff.duration_days} дней</b>\n\n"
        f"Сумма к оплате: {price_text}\n\n"
        "Нажмите на кнопку ниже, чтобы перейти к оплате.",
        reply_markup=payment_kb.as_markup()
    )
    await state.update_data(payment_message_id=sent_message.message_id)


async def _start_manual_payment_flow(
    call: CallbackQuery, state: FSMContext, bot: Bot,
    tariff, final_price: float, discount_percent, promo_code
):
    """Создаёт заявку на ручную оплату и форум-тему для оператора."""
    # Защита: пользователь открыл диалог поддержки
    current_state = await state.get_state()
    if current_state == SupportFSM.in_chat.state:
        await call.answer(
            "Сначала закройте диалог с поддержкой (кнопка «Завершить диалог» или /close).",
            show_alert=True
        )
        return

    user_id = call.from_user.id

    # Защита: уже есть активная заявка
    existing = await db.get_pending_manual_payment_by_user(user_id)
    if existing:
        await state.set_state(ManualPaymentFSM.awaiting_receipt)
        await state.update_data(manual_payment_id=existing.id)
        await call.message.edit_text(
            "⚠️ У вас уже есть незавершённая заявка на ручную оплату.\n"
            "Ожидайте подтверждения оператором или отмените её.",
            reply_markup=manual_payment_user_keyboard()
        )
        return

    username = call.from_user.username or f"id{user_id}"

    # Создаём форум-тему в группе поддержки
    try:
        topic = await bot.create_forum_topic(
            chat_id=config.tg_bot.support_chat_id,
            name=f"💳 Оплата #{user_id} | @{username}"
        )
    except Exception as e:
        logger.error(f"Failed to create manual payment topic for {user_id}: {e}", exc_info=True)
        await call.answer("Не удалось создать заявку. Попробуйте позже.", show_alert=True)
        return

    # Сохраняем заявку в БД
    mp = await db.create_manual_payment(user_id, tariff.id, topic.message_thread_id, final_price)

    # Сообщение оператору с кнопками
    user = await db.get_user(user_id)
    price_text = (
        f"<s>{tariff.price} RUB</s> → <b>{final_price} RUB</b> (скидка {discount_percent}%, промо: {promo_code})"
        if discount_percent else f"<b>{final_price} RUB</b>"
    )
    try:
        op_msg = await bot.send_message(
            chat_id=config.tg_bot.support_chat_id,
            message_thread_id=topic.message_thread_id,
            text=(
                f"💳 <b>Заявка на ручную оплату</b>\n\n"
                f"👤 <a href='tg://user?id={user_id}'>{user.full_name}</a> "
                f"(ID: <code>{user_id}</code>)\n"
                f"Username: @{username}\n\n"
                f"📦 Тариф: «{tariff.name}» ({tariff.duration_days} дн.)\n"
                f"💰 Сумма: {price_text}"
            ),
            reply_markup=operator_manual_payment_keyboard(mp.id)
        )
        try:
            await bot.pin_chat_message(
                chat_id=config.tg_bot.support_chat_id,
                message_id=op_msg.message_id,
                disable_notification=True
            )
        except Exception:
            pass  # нефатально — нет прав на закрепление
        await db.set_manual_payment_operator_msg(mp.id, op_msg.message_id)
    except Exception as e:
        logger.error(f"Failed to send operator message for payment {mp.id}: {e}", exc_info=True)

    # Устанавливаем FSM пользователя
    await state.set_state(ManualPaymentFSM.awaiting_receipt)
    await state.update_data(manual_payment_id=mp.id)

    # Показываем пользователю реквизиты
    await call.message.edit_text(
        f"✅ <b>Заявка создана!</b>\n\n"
        f"Переведите <b>{final_price} RUB</b> по реквизитам:\n\n"
        f"<code>{config.tg_bot.manual_payment_bank_details}</code>\n\n"
        "После перевода отправьте сюда скриншот или фото квитанции. "
        "Оператор подтвердит платёж в течение рабочего времени.",
        reply_markup=manual_payment_user_keyboard()
    )