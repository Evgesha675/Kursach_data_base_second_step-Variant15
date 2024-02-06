from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import EditKassaStates, EditAirlineStates, EditKassirStates, EditClientStates, EditTicketStates, EditCouponStates

from app.database.requests import get_kassa, get_airlines_for_add_kassa, get_cashiers, get_all_clients, get_tickets, get_all_coupon

# Клавиатура - Меню
async def menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💳 Касса"), KeyboardButton(text="👤 Кассиры")],
            [KeyboardButton(text="🎁 Купоны"), KeyboardButton(text="🎫 Билеты")],
            [KeyboardButton(text="👥 Клиенты"), KeyboardButton(text="✈️ Авиакомпании")]], resize_keyboard=True, input_field_placeholder="Выберите пункт ниже")

# Клавиатура для выбора кассы для взаимодействия
async def kassa():
    kassas = await get_kassa()
    keyboard = [[InlineKeyboardButton(text=kassa.address, callback_data=f'kassa_number:{kassa.id}')] for kassa in kassas]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для действий с кассой
async def kassa_keyboard_act(kassa_id):
    buttons = [
        InlineKeyboardButton(text="Добавить", callback_data=f"action.kassa.add_{kassa_id}"),
        InlineKeyboardButton(text="Изменить", callback_data=f"action.kassa.edit_{kassa_id}"),
        InlineKeyboardButton(text="Удалить", callback_data=f"action.kassa.delete_{kassa_id}")]
    return InlineKeyboardMarkup(inline_keyboard=[buttons, [InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]])

# Клавиатура для добавления новой кассы - выбор авиакомпании
async def kassa_add(airlines):
    keyboard = [[InlineKeyboardButton(text=airline.name, callback_data=f'airlines_code_kassa:{airline.id}')] for airline in airlines]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для изменения кассы - выбор пункта для изменения
async def kassa_edit_keyboard(kassa_id, state: FSMContext):
    bottons = [
        [InlineKeyboardButton(text="Изменить адрес", callback_data=f"action.kassa.address_{kassa_id}")],
        [InlineKeyboardButton(text="Изменить авиакомпанию", callback_data=f"action.kassa.airline_{kassa_id}")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=bottons)
        
    current_state = await state.get_state()
    if current_state == EditKassaStates.address_edit:
        return None
    elif current_state == EditKassaStates.airline_edit:
        return None
    return keyboard

# Клавиатура для выбора авиакомпании для изменения кассы
async def kassa_airlines_edit(airlines):
    keyboard = [[InlineKeyboardButton(text=airline.name, callback_data=f'airlines.code.kassa.airlines:{airline.id}')] for airline in airlines]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для выбора авиакомпании
async def airlines():
    airlines = await get_airlines_for_add_kassa()
    keyboard = [[InlineKeyboardButton(text=airline.name, callback_data=f'airlines:{airline.id}')] for airline in airlines]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для действий с авикомпаниями - администратор
async def airlines_keyboard_act(airline_id):
    buttons = [
        InlineKeyboardButton(text="Добавить", callback_data=f"action.airlines.add_{airline_id}"),
        InlineKeyboardButton(text="Изменить", callback_data=f"action.airlines.edit_{airline_id}"),
        InlineKeyboardButton(text="Удалить", callback_data=f"action.airlines.delete_{airline_id}")]
    return InlineKeyboardMarkup(inline_keyboard=[buttons, [InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]])

# Клавиатура для выбора авиакомпании - администратор
async def airlines_adm():
    airlines = await get_airlines_for_add_kassa()
    keyboard = [[InlineKeyboardButton(text=airline.name, callback_data=f'airlines_adm:{airline.id}')] for airline in airlines]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для изменения авиакомпании - выбор пункта для изменения
async def airline_edit_keyboard(airline_id, state: FSMContext):
    buttons = [
        [InlineKeyboardButton(text="Изменить адрес", callback_data=f"action.airline.address_{airline_id}")],
        [InlineKeyboardButton(text="Изменить название", callback_data=f"action.airline.name_{airline_id}")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
    current_state = await state.get_state()
    if current_state == EditAirlineStates.address_edit:
        return None
    elif current_state == EditAirlineStates.name_edit:
        return None
    return keyboard

# Клавиатура для выбора кассира для взаимодействия
async def cashiers_all():
    cashiers = await get_cashiers()
    keyboard = [[InlineKeyboardButton(text=kassir.full_name, callback_data=f'kassir_number:{kassir.id}')] for kassir in cashiers]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для действий с кассиром
async def kassir_keyboard_act(kassir_id):
    buttons = [
        InlineKeyboardButton(text="Добавить", callback_data=f"action.kassir.add_{kassir_id}"),
        InlineKeyboardButton(text="Изменить", callback_data=f"action.kassir.edit_{kassir_id}"),
        InlineKeyboardButton(text="Удалить", callback_data=f"action.kassir.delete_{kassir_id}")]
    return InlineKeyboardMarkup(inline_keyboard=[buttons, [InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]])

# Клавиатура для выбора кассы при добавлении кассира
async def kassir_add(kassas):
    keyboard = [[InlineKeyboardButton(text=kassa.address, callback_data=f'kassa_code_cashier:{kassa.id}')] for kassa in kassas]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для выбора действий при изменении кассира
async def kassir_edit_keyboard(kassir_id):
    buttons = [
        [InlineKeyboardButton(text="Изменить ФИО", callback_data=f"action.kassir.fullname_{kassir_id}")],
        [InlineKeyboardButton(text="Изменить место работы", callback_data=f"action.kassir.ticketoffice_{kassir_id}")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# Клавиатура для выбора места работы кассира
async def kassir_ticket_office_edit(ticket_offices):
    buttons = [[InlineKeyboardButton(text=office.address, callback_data=f"ticket_office_code_kassir:{office.id}")] for office in ticket_offices]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для вывода клиентов
async def clients_all():
    clients = await get_all_clients()
    buttons = [[InlineKeyboardButton(text=client.full_name, callback_data=f"action.client.info:{client.passport_number}")] for client in clients]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# Клавиатура для действий с клиентом 
async def client_actions(passport_number):
    buttons = [
        InlineKeyboardButton(text="Добавить", callback_data=f"action.client.add_{passport_number}"),
        InlineKeyboardButton(text="Изменить", callback_data=f"action.client.edit_{passport_number}"),
        InlineKeyboardButton(text="Удалить", callback_data=f"action.client.delete_{passport_number}")]
    return InlineKeyboardMarkup(inline_keyboard=[buttons, [InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]])

# Клавиатура для выбора действий при изменении клиента
async def client_edit_keyboard(passport_number, state: FSMContext):
    buttons = [[InlineKeyboardButton(text="Изменить имя", callback_data=f"action.client.fullname_{passport_number}")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    current_state = await state.get_state()
    if current_state == EditClientStates.full_name_edit.state:
        return None
    return keyboard

# Клавиатура для выбора билета для взаимодействия
async def tickets_all():
    tickets = await get_tickets()
    keyboard = [[InlineKeyboardButton(text=f'Билет #{ticket.id}', callback_data=f'action.ticket.info:{ticket.id}')] for ticket in tickets]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для действий с клиентом 
async def ticket_actions(ticket_id):
    buttons = [
        InlineKeyboardButton(text="Добавить", callback_data=f"action.ticket.add_{ticket_id}"),
        InlineKeyboardButton(text="Изменить", callback_data=f"action.ticket.edit_{ticket_id}"),
        InlineKeyboardButton(text="Удалить", callback_data=f"action.ticket.delete_{ticket_id}")]
    return InlineKeyboardMarkup(inline_keyboard=[buttons, [InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]])

# Клавиатуры для добавления нового билета 
# Создаем клавиатуру для выбора типа билета
async def ticket_type_keyboard():
    buttons = [
        InlineKeyboardButton(text="Эконом", callback_data="ticket_type:economy"),
        InlineKeyboardButton(text="Бизнес", callback_data="ticket_type:business"),
        InlineKeyboardButton(text="Первый класс", callback_data="ticket_type:first_class"),]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# Клавиатура для выбора кассира
async def cashier_keyboard(cashiers):
    buttons = [InlineKeyboardButton(text=f"{cashier.full_name}", callback_data=f"action.ticket.cashier:{cashier.id}") for cashier in cashiers]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# Клавиатура для выбора кассы
async def ticket_office_keyboard(ticket_offices):
    buttons = [[InlineKeyboardButton(text=f"{office.address}", callback_data=f"action.ticket.office:{office.id}")] for office in ticket_offices]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для выбора авиакомпании
async def airline_keyboard(airlines):
    buttons = [InlineKeyboardButton(text=f"{airline.name}", callback_data=f"action.ticket.airline:{airline.id}") for airline in airlines]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# Клавиатура для выбора клиента
async def client_keyboard(clients):
    buttons = [InlineKeyboardButton(text=f"{client.full_name}", callback_data=f"action.ticket.client:{client.passport_number}") for client in clients]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# Клавиатуры для изменении билета 
async def ticket_edit_keyboard(states: EditTicketStates):
    data = await states.get_data()
    ticket_id = data.get('ticket_id')
    buttons = [
        [InlineKeyboardButton(text="Тип билета", callback_data=f"action.ticket.type_{ticket_id}"),
         InlineKeyboardButton(text="Дата продажи", callback_data=f"action.ticket.sale_date_{ticket_id}"),
         InlineKeyboardButton(text="Касса", callback_data=f"action.ticket.ticket_office_{ticket_id}")],
        [InlineKeyboardButton(text="Кассир", callback_data=f"action.ticket.cashier_{ticket_id}"),
         InlineKeyboardButton(text="Авиакомпания", callback_data=f"action.ticket.airline_{ticket_id}"),
         InlineKeyboardButton(text="Клиент", callback_data=f"action.ticket.client_{ticket_id}")],
        [InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для выбора кассы при редактировании билета
async def ticket_edit_ticket_office(ticket_offices):
    keyboard = [[InlineKeyboardButton(text=kassa.address, callback_data=f'ticket_office_code_ticket:{kassa.id}')] for kassa in ticket_offices]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для выбора кассира при редактировании билета
async def ticket_edit_cashier(cashiers):
    keyboard = [[InlineKeyboardButton(text=kassir.full_name, callback_data=f'cashier_code_ticket:{kassir.id}')] for kassir in cashiers]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для выбора авиакомпании при редактировании билета
async def ticket_edit_airline(airlines):
    keyboard = [[InlineKeyboardButton(text=airline.name, callback_data=f'airline_code_ticket:{airline.id}')] for airline in airlines]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для выбора клиента при редактировании билета
async def ticket_edit_client(clients):
    keyboard = [[InlineKeyboardButton(text=f"{client.full_name} ({client.passport_number})", callback_data=f'client_passport_number_ticket:{client.passport_number}')] for client in clients]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Создаем клавиатуру для выбора типа билета
async def ticket_edit_type():
    buttons = [
        [InlineKeyboardButton(text="Эконом", callback_data="ticket_type_ticket:econom"),
         InlineKeyboardButton(text="Бизнес", callback_data="ticket_type_ticket:business"),
         InlineKeyboardButton(text="Первый класс", callback_data="ticket_type_ticket:first_class")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для вывода всех купонов
async def coupons_all():
    coupons = await get_all_coupon()
    keyboard = [[InlineKeyboardButton(text=f"Купон #{coupon.id} - {coupon.flight_direction}", callback_data = f"action.coupon.info:{coupon.id}")] for coupon in coupons]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для действий с купоном
async def coupon_actions(coupon_id):
    buttons = [
        InlineKeyboardButton(text="Добавить", callback_data=f"action.coupon.add_{coupon_id}"),
        InlineKeyboardButton(text="Изменить", callback_data=f"action.coupon.edit_{coupon_id}"),
        InlineKeyboardButton(text="Удалить", callback_data=f"action.coupon.delete_{coupon_id}")]
    return InlineKeyboardMarkup(inline_keyboard=[buttons, [InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]])

# Клавиатура для выбора билета для купона
async def get_tickets_keyboard():
    tickets = await get_tickets()
    buttons = [InlineKeyboardButton(text=f"Билет {ticket.id}", callback_data=f"action.coupon.select_ticket:{ticket.id}") for ticket in tickets]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# Клавиатура для выбора поля купона для редактирования
async def coupon_edit_keyboard(coupon_id, state):
    buttons = [
        [InlineKeyboardButton(text="Изменить билет", callback_data=f"action.coupon.ticket_{coupon_id}"),],
        [InlineKeyboardButton(text="Изменить направление полета", callback_data=f"action.coupon.flight_direction_{coupon_id}"),],
        [InlineKeyboardButton(text="Изменить тариф", callback_data=f"action.coupon.fare_{coupon_id}")],
        [InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура для выбора билета при редактировании купона
async def coupon_tickets_edit(tickets_list):
    buttons = [InlineKeyboardButton(text=f"Билет {ticket.id}", callback_data=f"action.coupon.selectticket:{ticket.id}") for ticket in tickets_list]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# Клавиатура для выбора авиакомпании - администратор - Билеты, проданные за указанный месяц указанной авиакомпании
async def airlines_otchet():
    airlines = await get_airlines_for_add_kassa()
    keyboard = [[InlineKeyboardButton(text=airline.name, callback_data=f'airlines_otchet:{airline.id}')] for airline in airlines]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для выбора месяца - администратор - Билеты, проданные за указанный месяц у авиакомпании
async def airlines_month():
    buttons = [
        [InlineKeyboardButton(text="Январь", callback_data=f"airlines.month_01"), InlineKeyboardButton(text="Февраль", callback_data=f"airlines.month_02")],
        [InlineKeyboardButton(text="Март", callback_data=f"airlines.month_03"), InlineKeyboardButton(text="Апрель", callback_data=f"airlines.month_04")],
        [InlineKeyboardButton(text="Май", callback_data=f"airlines.month_05"), InlineKeyboardButton(text="Июнь", callback_data=f"airlines.month_06")],
        [InlineKeyboardButton(text="Июль", callback_data=f"airlines.month_07"), InlineKeyboardButton(text="Август", callback_data=f"airlines.month_08")],
        [InlineKeyboardButton(text="Сентябрь", callback_data=f"airlines.month_09"), InlineKeyboardButton(text="Октябрь", callback_data=f"airlines.month_10")],
        [InlineKeyboardButton(text="Ноябрь", callback_data=f"airlines.month_11"), InlineKeyboardButton(text="Декабрь", callback_data=f"airlines.month_12")],
        [InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def airlines_data():
    airlines = await get_airlines_for_add_kassa() 
    keyboard = [[InlineKeyboardButton(text=airline.name, callback_data=f'airlines_data:{airline.id}')] for airline in airlines]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def summ_by_airlines():
    airlines = await get_airlines_for_add_kassa()
    keyboard = [[InlineKeyboardButton(text=airline.name, callback_data=f'summ_by_airlines:{airline.id}')] for airline in airlines]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Клавиатура для прикрепляемой кнопки - вернуться в меню
async def return_to_menu():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🏡 Вернуться в меню", callback_data="return_to_menu")]])
