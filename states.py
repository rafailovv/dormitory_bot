from aiogram.fsm.state import StatesGroup, State

class RegisterState(StatesGroup):
    """ Состояние регистрации """
    reg_block = State()


class AnnounceState(StatesGroup):
    """ Состояние уведомления """
    announce = State()