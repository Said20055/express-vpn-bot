# tgbot/keyboards/inline.py

from typing import List
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from urllib.parse import quote_plus

# Импортируем модели только для аннотации типов, чтобы избежать циклических импортов
from db import Tariff, PromoCode, Channel


# =============================================================================
# === 1. КЛАВИАТУРЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ (ОСНОВНОЕ МЕНЮ) ===
# =============================================================================

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главная клавиатура, которая будет показываться пользователю в основном меню."""
    builder = InlineKeyboardBuilder()
    builder.button(text='💎 Продлить / Оплатить', callback_data='buy_subscription')
    builder.button(text='👤 Мой профиль', callback_data='my_profile')
    builder.button(text='🔑 Мои ключи', callback_data='my_keys')
    builder.button(text='🤝 Реферальная программа', callback_data='referral_program')
    builder.button(text="📲 Инструкция по подключению", callback_data="instruction_info")
    builder.button(text="🎁 Промокод", callback_data="enter_promo_code")
    builder.button(text="💬 Поддержка", callback_data="support_chat_start")
    builder.button(text="🌟 Бесплатная подписка", callback_data="start_trial_process")
    builder.adjust(1, 1, 2, 2, 1) # Немного изменил расположение для симметрии
    return builder.as_markup()


def profile_keyboard(subscription_url: str) -> InlineKeyboardMarkup:
    """Клавиатура для раздела "Мой профиль"."""
    REDIRECT_PAGE_URL = "https://vac-service.ru:8443/import"
    encoded_url = quote_plus(subscription_url)
    deep_link = f"v2raytun://import/{encoded_url}"
    final_redirect_url = f"{REDIRECT_PAGE_URL}?deeplink={quote_plus(deep_link)}"

    builder = InlineKeyboardBuilder()
    builder.button(text="📲 Импортировать в V2RayTun", url=final_redirect_url)
    builder.button(text="🔄 Обновить", callback_data="my_profile")
    builder.button(text="⬅️ Назад в меню", callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()


def tariffs_keyboard(tariffs: list[Tariff], promo_procent: int = 0) -> InlineKeyboardMarkup:
    """Создает клавиатуру со списком тарифов для покупки."""
    builder = InlineKeyboardBuilder()
    if promo_procent > 0:
        for tariff in tariffs:
            discounted_price = int(tariff.price * (1-promo_procent / 100))
            builder.button(
                text=f"{tariff.name} - {discounted_price} RUB (скидка {promo_procent}%)",
                callback_data=f"select_tariff_{tariff.id}"
            )
    else:
        for tariff in tariffs:
            builder.button(
            text=f"{tariff.name} - {tariff.price} RUB",
            callback_data=f"select_tariff_{tariff.id}"
        )
        builder.button(text="⬅️ Назад в главное меню", callback_data="back_to_main_menu")
    
    builder.adjust(1)
    return builder.as_markup()


def channels_subscribe_keyboard(channels: List[Channel]) -> InlineKeyboardMarkup:
    """Создает клавиатуру со ссылками на каналы и кнопкой проверки."""
    builder = InlineKeyboardBuilder()
    for i, channel in enumerate(channels):
        builder.button(text=f"Канал {i+1}: {channel.title}", url=channel.invite_link)
    builder.button(text="✅ Я подписался, проверить", callback_data="check_subscription")
    builder.button(text="⬅️ Назад в главное меню", callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()

def close_support_chat_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для закрытия чата с поддержкой."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Завершить диалог", callback_data="support_chat_close")
    return builder.as_markup()


def single_key_view_keyboard():
    """Клавиатура для возврата к списку ключей."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад к списку ключей", callback_data="my_keys")
    return builder.as_markup()
# =============================================================================
# === 2. КЛАВИАТУРЫ ДЛЯ АДМИН-ПАНЕЛИ ===
# =============================================================================

def admin_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню админ-панели."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📈 Статистика", callback_data="admin_stats")
    builder.button(text="👤 Управление пользователями", callback_data="admin_users_menu")
    builder.button(text="📢 Управление каналами", callback_data="admin_channels_menu")
    builder.button(text="💳 Управление тарифами", callback_data="admin_tariffs_menu")
    builder.button(text="🎁 Промокоды", callback_data="admin_promo_codes")
    builder.button(text="📤 Рассылка", callback_data="admin_broadcast")
    builder.button(text="💵 Настройки оплаты", callback_data="admin_payment_settings")
    builder.button(text="⬅️ Выйти из админ-панели", callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()

# --- 2.1. Управление пользователями ---

def user_manage_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для управления конкретным пользователем."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Добавить дни", callback_data=f"admin_add_days_{user_id}")
    builder.button(text="🔄 Сбросить ключ", callback_data=f"admin_reset_user_{user_id}")
    builder.button(text="🗑 Удалить пользователя", callback_data=f"admin_delete_user_{user_id}")
    builder.button(text="⬅️ Назад к поиску", callback_data="admin_users_menu")
    builder.adjust(1)
    return builder.as_markup()


def confirm_delete_keyboard(user_id_to_delete: int) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения удаления пользователя."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, удалить", callback_data=f"admin_confirm_delete_user_{user_id_to_delete}")
    builder.button(text="❌ Отмена", callback_data=f"admin_show_user_{user_id_to_delete}")
    builder.adjust(1)
    return builder.as_markup()

# --- 2.2. Управление каналами (НОВОЕ) ---

def manage_channels_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для добавления/удаления каналов."""
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить канал", callback_data="admin_add_channel")
    builder.button(text="➖ Удалить канал", callback_data="admin_delete_channel")
    builder.button(text="⬅️ Назад в админ-меню", callback_data="admin_main_menu")
    builder.adjust(2, 1)
    return builder.as_markup()

# --- 2.3. Управление тарифами ---

def tariffs_list_keyboard(tariffs: list[Tariff]) -> InlineKeyboardMarkup:
    """Показывает список всех тарифов с кнопкой "Добавить новый"."""
    builder = InlineKeyboardBuilder()
    for tariff in tariffs:
        status_icon = "✅" if tariff.is_active else "❌"
        builder.button(
            text=f"{status_icon} {tariff.name} - {tariff.price} RUB",
            callback_data=f"admin_manage_tariff_{tariff.id}"
        )
    builder.button(text="➕ Добавить новый тариф", callback_data="admin_add_tariff")
    builder.button(text="⬅️ Назад в админ-меню", callback_data="admin_main_menu")
    builder.adjust(1)
    return builder.as_markup()


def single_tariff_manage_keyboard(tariff_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Клавиатура для управления одним тарифом."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить название", callback_data=f"admin_edit_tariff_name_{tariff_id}")
    builder.button(text="💰 Изменить цену", callback_data=f"admin_edit_tariff_price_{tariff_id}")
    builder.button(text="⏳ Изменить срок (дни)", callback_data=f"admin_edit_tariff_duration_{tariff_id}")
    
    action_text, action_cb = ("❌ Отключить", "admin_toggle_tariff_") if is_active else ("✅ Включить", "admin_toggle_tariff_")
    builder.button(text=action_text, callback_data=f"{action_cb}{tariff_id}")
        
    builder.button(text="🗑️ Удалить тариф", callback_data=f"admin_delete_tariff_{tariff_id}")
    builder.button(text="⬅️ Назад к списку тарифов", callback_data="admin_tariffs_menu")
    builder.adjust(1)
    return builder.as_markup()

def confirm_delete_tariff_keyboard(tariff_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения удаления тарифа."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, удалить", callback_data=f"admin_confirm_delete_tariff_{tariff_id}")
    builder.button(text="❌ Нет, отмена", callback_data=f"admin_manage_tariff_{tariff_id}")
    builder.adjust(1)
    return builder.as_markup()

# --- 2.4. Управление промокодами ---

def promo_codes_list_keyboard(promo_codes: list[PromoCode]) -> InlineKeyboardMarkup:
    """Показывает список всех промокодов с кнопкой 'Удалить' и 'Добавить'."""
    builder = InlineKeyboardBuilder()
    if promo_codes:
        for code in promo_codes:
            info = []
            if code.bonus_days > 0: info.append(f"{code.bonus_days} дн.")
            if code.discount_percent > 0: info.append(f"{code.discount_percent}%")
            info.append(f"{code.uses_left}/{code.max_uses} исп.")
            builder.button(text=f"🗑️ {code.code} ({', '.join(info)})", callback_data=f"admin_delete_promo_{code.id}")
    
    builder.button(text="➕ Добавить новый промокод", callback_data="admin_add_promo")
    builder.button(text="⬅️ Назад в админ-меню", callback_data="admin_main_menu")
    builder.adjust(1)
    return builder.as_markup()


def promo_type_keyboard() -> InlineKeyboardMarkup:
    """Предлагает выбрать тип создаваемого промокода."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🎁 Бонусные дни", callback_data="promo_type_days")
    builder.button(text="💰 Скидка (%)", callback_data="promo_type_discount")
    builder.adjust(1)
    return builder.as_markup()

# --- 2.5. Рассылка ---


# tgbot/keyboards/inline.py (или admin_keyboards.py)

def broadcast_audience_keyboard():
    """Клавиатура для выбора аудитории рассылки."""
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Всем пользователям", callback_data="broadcast_audience_all")
    builder.button(text="⏳ Тем, кто не покупал", callback_data="broadcast_audience_never")
    builder.button(text="❌ Отмена", callback_data="admin_main_menu")
    builder.adjust(1)
    return builder.as_markup()

def broadcast_promo_keyboard():
    """Клавиатура для добавления промокода к рассылке."""
    builder = InlineKeyboardBuilder()
    # Эта кнопка будет вести в FSM для ввода промокода
    builder.button(text="🎁 Прикрепить промокод", callback_data="broadcast_attach_promo")
    # Эта кнопка пропустит шаг с промокодом
    builder.button(text="➡️ Продолжить без промокода", callback_data="broadcast_skip_promo")
    builder.button(text="❌ Отмена", callback_data="admin_main_menu")
    builder.adjust(1)
    return builder.as_markup()


def confirm_broadcast_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения рассылки."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Начать рассылку", callback_data="broadcast_start")
    builder.button(text="❌ Отмена", callback_data="admin_panel") # Изменено для единообразия
    builder.adjust(1)
    return builder.as_markup()



# =============================================================================
# === 3. УНИВЕРСАЛЬНЫЕ И СЛУЖЕБНЫЕ КЛАВИАТУРЫ ===
# =============================================================================

def back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Простая клавиатура с одной кнопкой "Назад в главное меню"."""
    builder = InlineKeyboardBuilder()
    builder.button(text='⬅️ Назад в главное меню', callback_data='back_to_main_menu')
    return builder.as_markup()


def back_to_admin_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой "Назад в админ-меню"."""
    builder = InlineKeyboardBuilder()
    builder.button(text='⬅️ Назад в админ-меню', callback_data='admin_main_menu')
    return builder.as_markup()


def cancel_fsm_keyboard(back_callback_data: str) -> InlineKeyboardMarkup:
    """Универсальная клавиатура для отмены любого состояния FSM."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data=back_callback_data)
    return builder.as_markup()

def back_to_promo_list_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для возврата к списку промокодов."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ К списку промокодов", callback_data="admin_promo_codes")
    return builder.as_markup()


# =============================================================================
# === 4. КЛАВИАТУРЫ ДЛЯ РУЧНОЙ ОПЛАТЫ ===
# =============================================================================

def manual_payment_user_keyboard() -> InlineKeyboardMarkup:
    """Показывается пользователю после создания заявки на ручную оплату."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить заявку", callback_data="manual_payment_cancel_by_user")
    builder.adjust(1)
    return builder.as_markup()


def operator_manual_payment_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """Закреплённое сообщение в форум-теме для оператора."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить оплату", callback_data=f"mp_confirm_{payment_id}")
    builder.button(text="❌ Отклонить", callback_data=f"mp_cancel_{payment_id}")
    builder.adjust(2)
    return builder.as_markup()


def admin_payment_settings_keyboard(is_enabled: bool) -> InlineKeyboardMarkup:
    """Меню настроек способа оплаты в админ-панели."""
    builder = InlineKeyboardBuilder()
    if is_enabled:
        builder.button(text="🔴 Выключить ручную оплату (вернуть YooKassa)", callback_data="admin_mp_disable")
    else:
        builder.button(text="🟢 Включить ручную оплату (банковский перевод)", callback_data="admin_mp_enable")
    builder.button(text="⬅️ Назад в админ-меню", callback_data="admin_main_menu")
    builder.adjust(1)
    return builder.as_markup()