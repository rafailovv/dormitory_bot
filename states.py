from aiogram.fsm.state import StatesGroup, State


class RegisterState(StatesGroup):
    """ Состояние регистрации """
    reg_block = State()
    reg_has_car = State()
    reg_car_data = State()


class AnnounceState(StatesGroup):
    """ Состояние уведомления """
    announce = State()
    announce_cars = State()