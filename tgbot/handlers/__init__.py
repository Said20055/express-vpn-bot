# tgbot/handlers/__init__.py (ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ)

# --- 1. Импортируем все "конечные" роутеры из их файлов ---
from .admin import admin_router

# --- 2. Импортируем "собранный" пользовательский роутер ---
from .user import user_router

# --- 3. Импортируем роутер поддержки ---
from .support import support_router

# --- 4. Импортируем роутер оператора ручных платежей (верхний уровень) ---
from .operator_payment import operator_payment_router

# --- 5. Собираем список в правильном порядке ---
routers_list = [
    # Форум-тема поддержки (самые специфичные по chat_id)
    support_router,

    # Колбэки Подтвердить/Отклонить из форум-темы (приходят из группы)
    operator_payment_router,

    # Админские FSM и команды
    admin_router,

    # Общий пользовательский роутер
    user_router
]

# --- 5. Экспортируем список ---
__all__ = [
    "routers_list",
]