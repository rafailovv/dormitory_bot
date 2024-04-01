from aiogram.fsm.state import StatesGroup, State

class RegisterState(StatesGroup):
    """ Состояние регистрации """
    reg_block = State()
    reg_has_car = State()


class AnnounceState(StatesGroup):
    """ Состояние уведомления """
    announce = State()