# tgbot/handlers/admin/payment_settings.py
# Управление режимом оплаты: ручная / YooKassa.

from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import requests as db
from tgbot.keyboards.inline import admin_payment_settings_keyboard

admin_payment_settings_router = Router()


async def _show_payment_settings(call: CallbackQuery):
    is_enabled = await db.is_manual_payment_enabled()
    status = "🟢 Включена (банковский перевод)" if is_enabled else "🔴 Выключена (работает YooKassa)"
    await call.message.edit_text(
        f"<b>💵 Настройки способа оплаты</b>\n\n"
        f"Текущий режим: {status}\n\n"
        "Когда ручная оплата <b>включена</b> — при выборе тарифа создаётся форум-тема, "
        "пользователь переводит деньги по реквизитам, оператор подтверждает.\n\n"
        "Когда <b>выключена</b> — стандартная оплата через YooKassa.",
        reply_markup=admin_payment_settings_keyboard(is_enabled)
    )


@admin_payment_settings_router.callback_query(F.data == "admin_payment_settings")
async def payment_settings_menu(call: CallbackQuery):
    await call.answer()
    await _show_payment_settings(call)


@admin_payment_settings_router.callback_query(F.data == "admin_mp_enable")
async def enable_manual_payment(call: CallbackQuery):
    await db.set_bot_setting("manual_payment_enabled", "true")
    await call.answer("✅ Ручная оплата включена.", show_alert=True)
    await _show_payment_settings(call)


@admin_payment_settings_router.callback_query(F.data == "admin_mp_disable")
async def disable_manual_payment(call: CallbackQuery):
    await db.set_bot_setting("manual_payment_enabled", "false")
    await call.answer("✅ YooKassa снова активна.", show_alert=True)
    await _show_payment_settings(call)
