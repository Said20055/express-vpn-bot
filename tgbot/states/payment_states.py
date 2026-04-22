from aiogram.fsm.state import State, StatesGroup


class ManualPaymentFSM(StatesGroup):
    awaiting_receipt = State()
