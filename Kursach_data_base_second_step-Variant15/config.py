from aiogram.fsm.state import State, StatesGroup

Token = '5597665832:AAEZjocB9_hbyX3CiIHleESxGPv8bGjRYaA'
SQLALCHEMY_URL = "sqlite+aiosqlite:///db.sqlite"
ADMIN_TELEGRAM_ID = 768886416


class EditKassaStates(StatesGroup):
    address_edit = State()
    airline_edit = State()
    
class EditAirlineStates(StatesGroup):
    address_edit = State()
    name_edit = State()
    
class EditKassirStates(StatesGroup):
    full_name_edit = State()
    ticket_office_edit = State()    
    kassir_id = State()
    
class EditClientStates(StatesGroup):
    full_name_edit = State()
    client_id = State()
    
class EditTicketStates(StatesGroup):
    ticket_type = State()
    sale_date = State()
    ticket_office = State()
    cashier = State()
    airline = State()
    client = State()
    ticket_id = State()
    
class EditCouponStates(StatesGroup):
    flight_direction_edit = State()
    fare_edit = State()
    ticket_edit = State()
    coupon_id = State()