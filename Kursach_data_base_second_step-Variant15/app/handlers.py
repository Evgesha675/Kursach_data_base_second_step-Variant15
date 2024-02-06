from aiogram import F, Router
from aiogram.types import Message
from aiogram import types
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.keyboards as kb
from config import ADMIN_TELEGRAM_ID, EditKassaStates, EditKassirStates, EditClientStates, EditTicketStates, EditCouponStates

from app.database.requests import (
    get_kassa_info_by_id, save_kassa_to_db, get_airlines_for_add_kassa, get_airline_name_by_code, 
    delete_kassa_from_db, update_kassa_address, update_kassa_airline, get_all_airlines_for_edit_kassa, 
    get_airline_info_by_id, get_kassir_info_by_id, get_kassas_for_add_cashier, save_cashier_to_db, get_kassa_address_by_code, 
    delete_kassir_from_db, update_kassir_full_name, update_kassir_ticket_office, get_all_ticket_offices, get_client_info_by_passport, 
    save_client_to_db, delete_client_from_db, update_client_full_name, get_ticket_info_by_id, get_clients, 
    get_airlines, get_cashiers_by_ticket_office, get_ticket_offices, save_ticket_to_db, get_ticket_office_address,
    get_cashier_full_name, get_airline_name, get_client_full_name, delete_ticket_from_db, update_ticket_type, 
    update_ticket_sale_date, update_ticket_ticket_office, update_ticket_cashier, update_ticket_airline, 
    update_ticket_client, get_all_clients, get_all_cashiers, get_all_airlines, get_coupon_info_by_id, 
    save_selected_ticket_to_coupon, delete_coupon_from_db, update_coupon_ticket, get_all_tickets_for_edit_coupon,
    update_coupon_fare, update_coupon_flight_direction)

router_u = Router()

class AddKassaStates(StatesGroup):
    address = State()
    airline = State()

class AddCashierStates(StatesGroup):
    full_name = State()
    kassa = State()

class AddClientStates(StatesGroup):
    full_name = State()
    passport_series = State()
    passport_number = State()

class AddTicketStates(StatesGroup):
    ticket_type = State()
    sale_date = State()
    ticket_office = State()
    cashier = State()
    airline = State()
    client = State()

class AddCouponStates(StatesGroup):
    flight_direction =  State()
    fare = State()
    ticket_id = State()
    

@router_u.message(CommandStart())
async def cmd_start(message: types.Message):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f'Привет 👋🏼,\nЯ - чат-бот АВИАКОМПАНИИ\n\n'
                             f'Я могу показать и взаимодействовать: \n\n'
                             f'• Кассами\n'  
                             f'• Кассирами\n'
                             f'• Клиентами\n'
                             f'• Купонами\n'
                             f'• Билетами\n\n'
                             f'А также предостовить информацию по авиакомпниям')
        await message.answer(f'🔮 Главное меню', reply_markup=await kb.menu())
    else:
        await message.answer(f'Меню администратора\n\n'
                             f'Я могу показать и взаимодействовать\n'
                             f'• Кассами\n'
                             f'• Кассиры\n'
                             f'• Клиентами\n'
                             f'• Купонами\n'
                             f'• Билетами\n'
                             f'Отчёты и взаимойдествия с авиакомпаниями по команде /commands')
        await message.answer(f'🔮 Главное меню', reply_markup=await kb.menu())
        
# Работа с кассами   
@router_u.message(F.text == '💳 Касса')
async def Kassa(message: types.Message):
    await message.answer(f'Выберите кассу, чтобы узнать подробную информацию:', reply_markup=await kb.kassa())

@router_u.callback_query(F.data.startswith("kassa_number:"))
async def Kassa_inf(query: types.CallbackQuery):
    kassa_id = int(query.data.split(":")[1])
    kassa_info = await get_kassa_info_by_id(kassa_id)
    if kassa_info:
        text = (
            f"<b>Информация о кассе {kassa_info['address']}:</b>\n\n"
            f"<i>ID:</i> {kassa_id}\n"
            f"<i>Адрес:</i> {kassa_info['address']}\n"
            f"<i>Авиакомпания:</i> {kassa_info['airline_name']}")
        await query.message.answer(text, reply_markup=await kb.kassa_keyboard_act(kassa_id))
    else:
        await query.message.answer("Касса не найдена.", reply_markup=await kb.return_to_menu())

# Добавление новой кассы
@router_u.callback_query(F.data.startswith("action.kassa.add_"))
async def Kassa_add(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Давайте добавим новую кассу. Введите адрес кассы:")
    await state.set_state(AddKassaStates.address)

@router_u.message(AddKassaStates.address)
async def Process_kassa_adress(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    airlines = await get_airlines_for_add_kassa()
    keyboard = await kb.kassa_add(airlines)
    await message.answer("Выберите существующую авиакомпанию:", reply_markup=keyboard)

@router_u.callback_query(F.data.startswith("airlines_code_kassa"))
async def Process_kassa_airlines(query: types.CallbackQuery, state: FSMContext):
    airline_code = query.data.split(":")[1]
    await state.update_data(airline_code=airline_code)

    data = await state.get_data()
    address = data.get('address', '')
    airline_code = data.get('airline_code', '')
    await save_kassa_to_db({'address': address, 'airline_code': airline_code})

    await query.message.answer("Касса успешно добавлена в базу данных!")
    airline_code = int(airline_code)
    airline_name = await get_airline_name_by_code(airline_code)
    await show_kassa_summary(message=query.message, data={'address': address, 'airline_name': airline_name})
    await state.clear()

async def show_kassa_summary(message: Message, data: dict) -> None:
    address = data.get('address', '')
    airline_name = data.get('airline_name', '')
    text = (f"Добавлена новая касса:\n\n"
           f"Адрес: <b>{address}</b>\n"
           f"Авиакомпания: <b>{airline_name}</b>\n")
    await message.answer(text)
           
# Изменение уже существующей кассы    
@router_u.callback_query(F.data.startswith("action.kassa.edit_"))
async def Kassa_edit(query: types.CallbackQuery, state: FSMContext):
    kassa_id_str = query.data.split("_")[1]
    kassa_id = int(kassa_id_str)
    await query.message.answer("Выберите какой пункт хотите изменить", reply_markup=await kb.kassa_edit_keyboard(kassa_id, state))

@router_u.callback_query(F.data.startswith("action.kassa.address"))
async def Kassa_edit_address(query: types.CallbackQuery, state: FSMContext):
    kassa_id_str = query.data.split("_")[1]
    kassa_id = int(kassa_id_str)
    await query.message.answer("Введите новый адрес для кассы:")
    await state.update_data(kassa_id=kassa_id)
    await state.set_state(EditKassaStates.address_edit)

@router_u.message(EditKassaStates.address_edit)
async def Process_kassa_edit_address(message: Message, state: FSMContext):
    new_address = message.text
    data = await state.get_data()
    kassa_id = data.get('kassa_id')
    await update_kassa_address(kassa_id, new_address)
    await message.answer("Адрес успешно изменен!")
    await state.clear()

@router_u.callback_query(F.data.startswith("action.kassa.airline"))
async def Kassa_edit_airline(query: types.CallbackQuery, state: FSMContext):
    kassa_id_str = query.data.split("_")[1]
    kassa_id = int(kassa_id_str)
    airlines_list = await get_all_airlines_for_edit_kassa()
    keyboard = await kb.kassa_airlines_edit(airlines_list)
    await query.message.answer("Выберите новую авиакомпанию для кассы:", reply_markup=keyboard)
    await state.update_data(kassa_id=kassa_id)
    await state.set_state(EditKassaStates.airline_edit)

@router_u.callback_query(F.data.startswith("airlines.code.kassa.airlines"))
async def Process_kassa_edit_airline(query: types.CallbackQuery, state: FSMContext):
    airline_code = query.data.split(":")[1]
    data = await state.get_data()
    kassa_id = data.get('kassa_id')
    await update_kassa_airline(kassa_id, airline_code)
    await query.message.answer("Авиакомпания успешно изменена!")
    await state.clear()
        
# Удаление кассы
@router_u.callback_query(F.data.startswith("action.kassa.delete_"))
async def Kassa_delete(query: types.CallbackQuery):
    kassa_id_str = query.data.split("_")[1]
    kassa_id = int(kassa_id_str)
    success = await delete_kassa_from_db(kassa_id)
    if success:
        await query.message.answer("Касса успешно удалена из базы данных.")
    else:
        await query.message.answer("Не удалось найти или удалить кассу.")
    await query.message.answer("🔮 Главное меню", reply_markup=await kb.menu())

# Работа с авиакомпаниями
@router_u.message(F.text == '✈️ Авиакомпании')
async def Airline(message: Message):
    await message.answer(f'Выберите авикомпанию, чтобы узнать подробную информацию:', reply_markup=await kb.airlines())  

@router_u.callback_query(F.data.startswith("airlines:"))
async def Airlines_inf(query: types.CallbackQuery):
    airline_id = int(query.data.split(":")[1])
    airline_info = await get_airline_info_by_id(airline_id)
    if airline_info:
        text = (
            f"<b>Информация об авиакомпании {airline_info['name']}:</b>\n\n"
            f"<i>ID:</i> {airline_info['id']}\n"
            f"<i>Имя:</i> {airline_info['name']}\n"
            f"<i>Адрес:</i> {airline_info['address']}")
        await query.message.answer(text, reply_markup=await kb.return_to_menu())
    else:
        await query.message.answer("Авиакомпания не найдена.", reply_markup=await kb.return_to_menu())

# Работа с касссирами
@router_u.message(F.text == '👤 Кассиры')
async def Kassir(message: Message):
    await message.answer(f'Выберите кассира, чтобы узнать подробную информацию:', reply_markup=await kb.cashiers_all())

@router_u.callback_query(F.data.startswith("kassir_number:"))
async def Kassir_inf(query: types.CallbackQuery):
    kassir_id = int(query.data.split(":")[1])
    kassir_info = await get_kassir_info_by_id(kassir_id)
    if kassir_info:
        text = (
            f"<b>Информация о кассире {kassir_info['full_name']}:</b>\n\n"
            f"<i>ID:</i> {kassir_id}\n"
            f"<i>Имя:</i> {kassir_info['full_name']}\n"
            f"<i>Касса:</i> {kassir_info['kassa_address']}")
        await query.message.answer(text, reply_markup=await kb.kassir_keyboard_act(kassir_id))
    else:
        await query.message.answer("Кассир не найден.", reply_markup=await kb.return_to_menu())

# Добавление нового кассира
@router_u.callback_query(F.data.startswith("action.kassir.add_"))
async def Cashier_add(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Давайте добавим нового кассира. Введите полное имя кассира:")
    await state.set_state(AddCashierStates.full_name)

@router_u.message(AddCashierStates.full_name)
async def Process_cashier_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    kassas = await get_kassas_for_add_cashier()
    keyboard = await kb.kassir_add(kassas)
    await message.answer("Выберите существующую кассу:", reply_markup=keyboard)

@router_u.callback_query(F.data.startswith("kassa_code_cashier"))
async def Process_cashier_kassa(query: types.CallbackQuery, state: FSMContext):
    kassa_code = query.data.split(":")[1]
    await state.update_data(kassa_code=kassa_code)

    data = await state.get_data()
    full_name = data.get('full_name', '')
    kassa_code = data.get('kassa_code', '')
    await save_cashier_to_db({'full_name': full_name, 'kassa_code': kassa_code})

    await query.message.answer("Кассир успешно добавлен в базу данных!")
    kassa_code = int(kassa_code)
    kassa_address = await get_kassa_address_by_code(kassa_code)
    await show_cashier_summary(message=query.message, data={'full_name': full_name, 'kassa_address': kassa_address})
    await state.clear()

async def show_cashier_summary(message: Message, data: dict) -> None:
    full_name = data.get('full_name', '')
    kassa_address = data.get('kassa_address', '')
    text = (f"Добавлен новый кассир:\n\n"
           f"Имя: <b>{full_name}</b>\n"
           f"Касса: <b>{kassa_address}</b>\n")
    await message.answer(text)

# Изменение уже имеющегося кассира
@router_u.callback_query(F.data.startswith("action.kassir.edit_"))
async def Kassir_edit(query: types.CallbackQuery, state: FSMContext):
    kassir_id_str = query.data.split("_")[1]
    kassir_id = int(kassir_id_str)
    await query.message.answer("Выберите, какой параметр кассира хотите изменить", reply_markup=await kb.kassir_edit_keyboard(kassir_id))
    
@router_u.callback_query(F.data.startswith("action.kassir.fullname_"))
async def Kassir_edit_full_name(query: types.CallbackQuery, state: FSMContext):
    kassir_id_str = query.data.split("_")[1]
    kassir_id = int(kassir_id_str)
    await query.message.answer("Введите новое ФИО кассира:")
    await state.update_data(kassir_id=kassir_id)
    await state.set_state(EditKassirStates.full_name_edit)

@router_u.message(EditKassirStates.full_name_edit)
async def Process_kassir_edit_full_name(message: Message, state: FSMContext):
    new_full_name = message.text
    data = await state.get_data()
    kassir_id = data.get('kassir_id')
    success = await update_kassir_full_name(kassir_id, new_full_name)
    if success:
        await message.answer("ФИО кассира успешно изменено!")
    else:
        await message.answer("Не удалось изменить ФИО кассира.")
    await state.clear()

@router_u.callback_query(F.data.startswith("action.kassir.ticketoffice_"))
async def Kassir_edit_ticket_office(query: types.CallbackQuery, state: FSMContext):
    kassir_id_str = query.data.split("_")[1]
    kassir_id = int(kassir_id_str)
    ticket_offices = await get_all_ticket_offices()  
    keyboard = await kb.kassir_ticket_office_edit(ticket_offices)
    await query.message.answer("Выберите новое место работы для кассира:", reply_markup=keyboard)
    await state.update_data(kassir_id=kassir_id)
    await state.set_state(EditKassirStates.ticket_office_edit)

@router_u.callback_query(F.data.startswith("ticket_office_code_kassir"))
async def Process_kassir_edit_ticket_office(query: types.CallbackQuery, state: FSMContext):
    ticket_office_id = int(query.data.split(":")[1])
    data = await state.get_data()
    kassir_id = data.get('kassir_id')
    success = await update_kassir_ticket_office(kassir_id, ticket_office_id)
    if success:
        await query.message.answer("Место работы кассира успешно изменено!")
    else:
        await query.message.answer("Не удалось изменить место работы кассира.")
    await state.clear()

# Удаление кассира из базы данных
@router_u.callback_query(F.data.startswith("action.kassir.delete_"))
async def Kassir_delete(query: types.CallbackQuery):
    kassir_id_str = query.data.split("_")[1]
    kassir_id = int(kassir_id_str)
    success = await delete_kassir_from_db(kassir_id)
    if success:
        await query.message.answer("Кассир успешно удален из базы данных.")
    else:
        await query.message.answer("Не удалось найти или удалить кассира.")
    await query.message.answer("🔮 Главное меню", reply_markup=await kb.menu())

# Работа с клиентами
@router_u.message(F.text == '👥 Клиенты')
async def Coupon(message: Message):
    await message.answer(f'Выберите клиента, чтобы узнать подробную информацию:', reply_markup=await kb.clients_all())  
    
@router_u.callback_query(F.data.startswith("action.client.info:"))
async def client_info_callback(query: types.CallbackQuery):
    passport_number = query.data.split(":")[1]
    client_info = await get_client_info_by_passport(passport_number)
    
    if client_info:
        text = (
            f"<b>Информация о клиенте {client_info['full_name']}:</b>\n\n"
            f"<i>Номер паспорта:</i> {client_info['passport_number']}\n"
            f"<i>Серия паспорта:</i> {client_info['passport_series']}")
        await query.message.answer(text, reply_markup=await kb.client_actions(passport_number))
    else:
        await query.message.answer("Клиент не найден.", reply_markup=await kb.return_to_menu())   
        
# Добавление нового клиента
@router_u.callback_query(F.data.startswith("action.client.add_"))
async def Client_add(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Давайте добавим нового клиента. Введите полное имя клиента:")
    await state.set_state(AddClientStates.full_name)

@router_u.message(AddClientStates.full_name)
async def Process_client_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Введите серию паспорта клиента:")
    await state.set_state(AddClientStates.passport_series)

@router_u.message(AddClientStates.passport_series)
async def Process_client_passport_series(message: Message, state: FSMContext):
    await state.update_data(passport_series=message.text)
    await message.answer("Введите номер паспорта клиента:")
    await state.set_state(AddClientStates.passport_number)

@router_u.message(AddClientStates.passport_number)
async def Process_client_passport_number(message: Message, state: FSMContext):
    await state.update_data(passport_number=message.text)

    data = await state.get_data()
    full_name = data.get('full_name', '')
    passport_series = data.get('passport_series', '')
    passport_number = data.get('passport_number', '')

    client_data = {
        'full_name': full_name,
        'passport_series': passport_series,
        'passport_number': passport_number
    }

    success = await save_client_to_db(client_data)

    if success:
        await message.answer("Клиент успешно добавлен в базу данных!")
        await show_client_summary(message=message, data=client_data)
        await state.clear()
    else:
        await message.answer("Не удалось добавить клиента в базу данных. Пожалуйста, попробуйте еще раз.")

async def show_client_summary(message: Message, data: dict) -> None:
    full_name = data.get('full_name', '')
    passport_series = data.get('passport_series', '')
    passport_number = data.get('passport_number', '')
    text = (f"Добавлен новый клиент:\n\n"
           f"Имя: <b>{full_name}</b>\n"
           f"Серия паспорта: <b>{passport_series}</b>\n"
           f"Номер паспорта: <b>{passport_number}</b>\n")
    await message.answer(text)        

# Изменения клиента
@router_u.callback_query(F.data.startswith("action.client.edit_"))
async def Client_edit(query: types.CallbackQuery, state: FSMContext):
    passport_number = query.data.split("_")[1]
    await query.message.answer("Выберите, какой параметр клиента хотите изменить", reply_markup=await kb.client_edit_keyboard(passport_number, state))

@router_u.callback_query(F.data.startswith("action.client.fullname_"))
async def Client_edit_full_name(query: types.CallbackQuery, state: FSMContext):
    passport_number = query.data.split("_")[1]
    await query.message.answer("Введите новое имя клиента:")
    await state.update_data(client_id=passport_number)
    await state.set_state(EditClientStates.full_name_edit)

@router_u.message(EditClientStates.full_name_edit)
async def Process_client_edit_full_name(message: Message, state: FSMContext):
    new_full_name = message.text
    data = await state.get_data()
    client_id = data.get('client_id')
    success = await update_client_full_name(client_id, new_full_name)
    if success:
        await message.answer("Имя клиента успешно изменено!")
    else:
        await message.answer("Не удалось изменить имя клиента.")
    await state.clear()
    
# Удаление клиента из базы данных
@router_u.callback_query(F.data.startswith("action.client.delete_"))
async def Client_delete(query: types.CallbackQuery):
    passport_number = query.data.split("_")[1]
    success = await delete_client_from_db(passport_number)
    if success:
        await query.message.answer("Клиент успешно удален из базы данных.")
    else:
        await query.message.answer("Не удалось найти или удалить клиента.")
    await query.message.answer("🔮 Главное меню", reply_markup=await kb.menu())    

# Работа с билетами
@router_u.message(F.text == '🎫 Билеты')
async def ticket_menu(message: Message):
    await message.answer(f'Выберите билет, чтобы узнать подробную информацию:', reply_markup=await kb.tickets_all()) 

@router_u.callback_query(F.data.startswith("action.ticket.info:"))
async def ticket_info_callback(query: types.CallbackQuery):
    ticket_id = query.data.split(":")[1]
    ticket_info = await get_ticket_info_by_id(ticket_id)
    
    if ticket_info:
        text = (
            f"<b>Информация о билете:</b>\n\n"
            f"<i>Тип билета:</i> {ticket_info['ticket_type']}\n"
            f"<i>Дата продажи:</i> {ticket_info['sale_date']}\n"
            f"<i>Касса:</i> {ticket_info['ticket_office_address']}\n"
            f"<i>Кассир:</i> {ticket_info['cashier_full_name']}\n"
            f"<i>Авиакомпания:</i> {ticket_info['airline_name']}\n"
            f"<i>Клиент:</i> {ticket_info['client_full_name']}\n"
        )
        await query.message.answer(text, reply_markup=await kb.ticket_actions(ticket_id))
    else:
        await query.message.answer("Билет не найден.", reply_markup=await kb.return_to_menu())   

# Добавление нового билета
@router_u.callback_query(F.data.startswith("action.ticket.add_"))
async def ticket_add(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Давайте добавим новый билет. Выберите тип билета:", reply_markup=await kb.ticket_type_keyboard())
    await state.set_state(AddTicketStates.ticket_type)

@router_u.callback_query(F.data.startswith("ticket_type:"))
async def process_ticket_type(query: types.CallbackQuery, state: FSMContext):
    ticket_type = query.data.split(":")[1]
    await state.update_data(ticket_type=ticket_type)
    await query.message.answer("Введите дату продажи билета в формате ДД.ММ.ГГГГ:")
    await state.set_state(AddTicketStates.sale_date)

@router_u.message(AddTicketStates.sale_date)
async def process_sale_date(message: Message, state: FSMContext):
    await state.update_data(sale_date=message.text)
    
    ticket_offices = await get_ticket_offices()
    keyboard_ticket_offices = await kb.ticket_office_keyboard(ticket_offices)

    await message.answer("Выберите кассу, в которой был продан билет:", reply_markup=keyboard_ticket_offices)
    await state.set_state(AddTicketStates.ticket_office)

@router_u.callback_query(F.data.startswith("action.ticket.office:"))
async def process_ticket_office(query: types.CallbackQuery, state: FSMContext):
    ticket_office_id = query.data.split(":")[1]
    await state.update_data(ticket_office_id=ticket_office_id)
    
    cashiers = await get_cashiers_by_ticket_office(ticket_office_id)
    keyboard_cashiers = await kb.cashier_keyboard(cashiers)

    await query.message.answer("Выберите кассира, который продал билет:", reply_markup=keyboard_cashiers)
    await state.set_state(AddTicketStates.cashier)

@router_u.callback_query(F.data.startswith("action.ticket.cashier:"))
async def process_ticket_cashier(query: types.CallbackQuery, state: FSMContext):
    cashier_id = query.data.split(":")[1]
    await state.update_data(cashier_id=cashier_id)
    
    airlines = await get_airlines()
    keyboard_airlines = await kb.airline_keyboard(airlines)

    await query.message.answer("Выберите авиакомпанию, на которую выписан билет:", reply_markup=keyboard_airlines)
    await state.set_state(AddTicketStates.airline)

@router_u.callback_query(F.data.startswith("action.ticket.airline:"))
async def process_ticket_airline(query: types.CallbackQuery, state: FSMContext):
    airline_id = query.data.split(":")[1]
    await state.update_data(airline_id=airline_id)

    clients = await get_clients()
    keyboard_clients = await kb.client_keyboard(clients)

    await query.message.answer("Выберите клиента, на которого выписан билет:", reply_markup=keyboard_clients)
    await state.set_state(AddTicketStates.client)

@router_u.callback_query(F.data.startswith("action.ticket.client:"))
async def process_ticket_client(query: types.CallbackQuery, state: FSMContext):
    client_passport_number = query.data.split(":")[1]
    await state.update_data(client_passport_number=client_passport_number)

    data = await state.get_data()
    ticket_type = data.get('ticket_type', '')
    sale_date = data.get('sale_date', '')
    ticket_office_id = data.get('ticket_office_id', '')
    cashier_id = data.get('cashier_id', '')
    airline_id = data.get('airline_id', '')
    client_passport_number = data.get('client_passport_number', '')

    await save_ticket_to_db({
        'ticket_type': ticket_type,
        'sale_date': sale_date,
        'ticket_office_id': ticket_office_id,
        'cashier_id': cashier_id,
        'airline_id': airline_id,
        'client_passport_number': client_passport_number
    })

    await query.message.answer("Билет успешно добавлен в базу данных!")
    await show_ticket_summary(query.message, data)
    await state.clear()
 
async def show_ticket_summary(message: Message, data: dict) -> None:
    ticket_type = data.get('ticket_type', '')
    sale_date = data.get('sale_date', '')
    ticket_office_id = data.get('ticket_office_id', '')
    cashier_id = data.get('cashier_id', '')
    airline_id = data.get('airline_id', '')
    client_passport_number = data.get('client_passport_number', '')

    ticket_office_address = await get_ticket_office_address(ticket_office_id)
    cashier_full_name = await get_cashier_full_name(cashier_id)
    airline_name = await get_airline_name(airline_id)
    client_full_name = await get_client_full_name(client_passport_number)

    text = (
        f"Добавлен новый билет:\n\n"
        f"Тип билета: <b>{ticket_type}</b>\n"
        f"Дата продажи: <b>{sale_date}</b>\n"
        f"Касса: <b>{ticket_office_address}</b>\n"
        f"Кассир: <b>{cashier_full_name}</b>\n"
        f"Авиакомпания: <b>{airline_name}</b>\n"
        f"Клиент: <b>{client_full_name}</b>\n"
    )
    await message.answer(text)

# Изменение уже имеющегося билета
@router_u.callback_query(F.data.startswith("action.ticket.edit_"))
async def ticket_edit(query: types.CallbackQuery, state: FSMContext):
    ticket_id_str = query.data.split("_")[1]
    ticket_id = int(ticket_id_str)
    await state.set_state(EditTicketStates.ticket_id)
    await state.update_data(ticket_id=ticket_id)
    await state.set_state(EditTicketStates.ticket_id)
    await query.message.answer("Выберите, какой параметр билета хотите изменить", reply_markup=await kb.ticket_edit_keyboard(state))


@router_u.callback_query(F.data.startswith("action.ticket.type_"))
async def ticket_edit_type(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Выберите новый тип билета:", reply_markup=await kb.ticket_edit_type())
    await state.set_state(EditTicketStates.ticket_type)

@router_u.callback_query(F.data.startswith("ticket_type_ticket"))
async def process_ticket_edit_type(query: types.CallbackQuery, state: FSMContext):
    new_ticket_type = query.data.split(":")[-1]
    data = await state.get_data()
    ticket_id = data.get('ticket_id')
    if not ticket_id:
        await query.message.answer("Не удалось получить идентификатор билета.")
        await state.clear()
        return
    try:
        success = await update_ticket_type(ticket_id, new_ticket_type)
        if success:
            await query.message.answer("Тип билета успешно изменен!")
        else:
            await query.message.answer("Не удалось изменить тип билета.")
    except Exception as e:
        await query.message.answer(f"Произошла ошибка при обновлении типа билета: {e}")
    await state.clear()

@router_u.callback_query(F.data.startswith("action.ticket.sale_date_"))
async def ticket_edit_sale_date_callback(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Введите новую дату продажи билета в формате ДД.ММ.ГГГГ:")
    await state.set_state(EditTicketStates.sale_date)

@router_u.message(EditTicketStates.sale_date)
async def process_ticket_edit_sale_date(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        ticket_id_str = data.get('ticket_id')
        print("Debug: ticket_id_str =", ticket_id_str)  
        ticket_id = int(ticket_id_str)

        new_sale_date = message.text
        success = await update_ticket_sale_date(ticket_id, new_sale_date)
        if success:
            await message.answer("Дата продажи билета успешно изменена!")
        else:
            await message.answer("Не удалось изменить дату продажи билета.")
    except ValueError:
        print("Debug: ValueError:") 
        await message.answer("Произошла ошибка при получении идентификатора билета.")
    finally:
        await state.clear()

@router_u.callback_query(F.data.startswith("action.ticket.ticket_office_"))
async def ticket_edit_ticket_office(query: types.CallbackQuery, state: FSMContext):
    ticket_offices = await get_all_ticket_offices()
    keyboard = await kb.ticket_edit_ticket_office(ticket_offices)
    await query.message.answer("Выберите новую кассу для билета:", reply_markup=keyboard)
    await state.set_state(EditTicketStates.ticket_office)

@router_u.callback_query(F.data.startswith("ticket_office_code_ticket"))
async def process_ticket_edit_ticket_office(query: types.CallbackQuery, state: FSMContext):
    ticket_office_id = int(query.data.split(":")[1])
    data = await state.get_data()
    ticket_id_str = data.get('ticket_id')
    ticket_id = int(ticket_id_str)
    success = await update_ticket_ticket_office(ticket_id, ticket_office_id)
    if success:
        await query.message.answer("Касса для билета успешно изменена!")
    else:
        await query.message.answer("Не удалось изменить кассу для билета.")
    await state.clear()

@router_u.callback_query(F.data.startswith("action.ticket.cashier_"))
async def ticket_edit_cashier(query: types.CallbackQuery, state: FSMContext):
    cashiers = await get_all_cashiers()
    keyboard = await kb.ticket_edit_cashier(cashiers)
    await query.message.answer("Выберите нового кассира для билета:", reply_markup=keyboard)
    await state.set_state(EditTicketStates.cashier)

@router_u.callback_query(F.data.startswith("cashier_code_ticket"))
async def process_ticket_edit_cashier(query: types.CallbackQuery, state: FSMContext):
    cashier_id = int(query.data.split(":")[1])
    data = await state.get_data()
    ticket_id_str = data.get('ticket_id')
    ticket_id = int(ticket_id_str)
    success = await update_ticket_cashier(ticket_id, cashier_id)
    if success:
        await query.message.answer("Кассир для билета успешно изменен!")
    else:
        await query.message.answer("Не удалось изменить кассира для билета.")
    await state.clear()

@router_u.callback_query(F.data.startswith("action.ticket.airline_"))
async def ticket_edit_airline(query: types.CallbackQuery, state: FSMContext):
    airlines = await get_all_airlines()
    keyboard = await kb.ticket_edit_airline(airlines)
    await query.message.answer("Выберите новую авиакомпанию для билета:", reply_markup=keyboard)
    await state.set_state(EditTicketStates.airline)

@router_u.callback_query(F.data.startswith("airline_code_ticket"))
async def process_ticket_edit_airline(query: types.CallbackQuery, state: FSMContext):
    airline_id = int(query.data.split(":")[1])
    data = await state.get_data()
    ticket_id = data.get('ticket_id')
    success = await update_ticket_airline(ticket_id, airline_id)
    if success:
        await query.message.answer("Авиакомпания для билета успешно изменена!")
    else:
        await query.message.answer("Не удалось изменить авиакомпанию для билета.")
    await state.clear()

@router_u.callback_query(F.data.startswith("action.ticket.client_"))
async def ticket_edit_client(query: types.CallbackQuery, state: FSMContext):
    ticket_id_str = query.data.split("_")[1]
    ticket_id = int(ticket_id_str)
    clients = await get_all_clients()
    keyboard = await kb.ticket_edit_client(clients)
    await query.message.answer("Выберите нового клиента для билета:", reply_markup=keyboard)
    await state.update_data(ticket_id=ticket_id)
    await state.set_state(EditTicketStates.client)

@router_u.callback_query(F.data.startswith("client_passport_number_ticket"))
async def process_ticket_edit_client(query: types.CallbackQuery, state: FSMContext):
    client_passport_number = int(query.data.split(":")[1])
    data = await state.get_data()
    ticket_id = data.get('ticket_id')
    success = await update_ticket_client(ticket_id, client_passport_number)
    if success:
        await query.message.answer("Клиент для билета успешно изменен!")
    else:
        await query.message.answer("Не удалось изменить клиента для билета.")
    await state.clear()

# Функция удаления билета из базы данных  
@router_u.callback_query(F.data.startswith("action.ticket.delete_"))
async def ticket_delete(query: types.CallbackQuery):
    ticket_id = query.data.split("_")[1]
    success = await delete_ticket_from_db(ticket_id)
    if success:
        await query.message.answer("Билет успешно удален из базы данных.")
    else:
        await query.message.answer("Не удалось найти или удалить билет.")
    await query.message.answer("🔮 Главное меню", reply_markup=await kb.menu())
    
# Работа с купонами  
@router_u.message(F.text == '🎁 Купоны')
async def coupons(message: Message):
    await message.answer(f'Выберите купон, чтобы узнать подробную информацию:', reply_markup=await kb.coupons_all()) 

@router_u.callback_query(F.data.startswith("action.coupon.info:"))
async def coupon_info_callback(query: types.CallbackQuery):
    coupon_id = int(query.data.split(":")[1])
    coupon_info = await get_coupon_info_by_id(coupon_id)
    
    if coupon_info:
        text = (
            f"<b>Информация о купоне {coupon_info.id}:</b>\n\n"
            f"<i>Направление полета:</i> {coupon_info.flight_direction}\n"
            f"<i>Тариф:</i> {coupon_info.fare}")
        await query.message.answer(text, reply_markup=await kb.coupon_actions(coupon_info.id))
    else:
        await query.message.answer("Купон не найден.", reply_markup=await kb.return_to_menu())
        
# Добавление купона в базу данных
@router_u.callback_query(F.data.startswith("action.coupon.add_"))
async def coupon_add(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Давайте добавим новый купон. Выберите билет из списка:", reply_markup=await kb.get_tickets_keyboard())
    await state.set_state(AddCouponStates.ticket_selection)

@router_u.callback_query(F.data.startswith("action.coupon.select_ticket:"))
async def process_coupon_select_ticket(query: types.CallbackQuery, state: FSMContext):
    ticket_id = int(query.data.split(":")[1])
    await state.update_data(ticket_id=ticket_id)
    await query.message.answer("Введите направление полета:")
    await state.set_state(AddCouponStates.flight_direction)

@router_u.message(AddCouponStates.flight_direction)
async def process_coupon_flight_direction(message: Message, state: FSMContext):
    await state.update_data(flight_direction=message.text)
    await message.answer("Введите тариф купона:")
    await state.set_state(AddCouponStates.fare)

@router_u.message(AddCouponStates.fare)
async def process_coupon_fare(message: Message, state: FSMContext):
    try:
        fare = int(message.text)
        await state.update_data(fare=fare)
        data = await state.get_data()
        await save_selected_ticket_to_coupon(data)
        await show_coupon_summary(message, data)
        await state.clear()

    except ValueError:
        await message.answer("Пожалуйста, введите корректный тариф (целое число).")

async def show_coupon_summary(message: Message, data: dict) -> None:
    flight_direction = data.get('flight_direction', '')
    fare = data.get('fare', '')
    text = (
        f"Добавлен новый купон:\n\n"
        f"Направление полета: <b>{flight_direction}</b>\n"
        f"Тариф: <b>{fare}</b>\n"
    )
    await message.answer(text, reply_markup=await kb.return_to_menu() )

# Изменение уже имеющегося купона в базе данных

@router_u.callback_query(F.data.startswith("action.coupon.edit_"))
async def coupon_edit(query: types.CallbackQuery, state: FSMContext):
    coupon_id_str = query.data.split("_")[1]
    coupon_id = int(coupon_id_str)
    await state.update_data(coupon_id=coupon_id)
    await query.message.answer("Выберите, что вы хотите изменить", reply_markup=await kb.coupon_edit_keyboard(coupon_id, state))

@router_u.callback_query(F.data.startswith("action.coupon.flight_direction"))
async def coupon_edit_flight_direction(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Введите новое направление полета для купона:")
    await state.set_state(EditCouponStates.flight_direction_edit)

@router_u.message(EditCouponStates.flight_direction_edit)
async def process_coupon_edit_flight_direction(message: Message, state: FSMContext):
    new_flight_direction = message.text
    data = await state.get_data()
    coupon_id = data.get('coupon_id')
    await update_coupon_flight_direction(coupon_id, new_flight_direction)
    await message.answer("Направление полета успешно изменено!")
    await state.clear()

@router_u.callback_query(F.data.startswith("action.coupon.fare"))
async def coupon_edit_fare(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Введите новый тариф для купона:")
    await state.set_state(EditCouponStates.fare_edit) 
    
@router_u.message(EditCouponStates.fare_edit)
async def process_coupon_edit_fare(message: Message, state: FSMContext):
    try:
        new_fare = int(message.text)
        if new_fare is None:
            await message.answer("Пожалуйста, введите корректный тариф (целое число).")
            await state.clear()
        data = await state.get_data()
        coupon_id = data.get('coupon_id')
        await update_coupon_fare(coupon_id, new_fare)
        await message.answer("Тариф успешно изменен!")
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректный тариф (целое число).")
        
@router_u.callback_query(F.data.startswith("action.coupon.ticket"))
async def coupon_edit_ticket(query: types.CallbackQuery, state: FSMContext):
    tickets_list = await get_all_tickets_for_edit_coupon()
    keyboard = await kb.coupon_tickets_edit(tickets_list)
    await query.message.answer("Выберите новый билет для купона:", reply_markup=keyboard)

@router_u.callback_query(F.data.startswith("action.coupon.selectticket:"))
async def process_coupon_select_ticket(query: types.CallbackQuery, state: FSMContext):
    ticket_id = int(query.data.split(":")[1])
    data = await state.get_data()
    coupon_id = data.get('coupon_id')
    await update_coupon_ticket(coupon_id, ticket_id)
    await query.message.answer("Билет успешно изменен!")
    await state.clear()

# Удаления купона из базы данных
@router_u.callback_query(F.data.startswith("action.coupon.delete_"))
async def coupon_delete(query: types.CallbackQuery):
    coupon_id_str = query.data.split("_")[1]
    coupon_id = int(coupon_id_str)
    success = await delete_coupon_from_db(coupon_id)
    if success:
        await query.message.answer("Купон успешно удален из базы данных.")
    else:
        await query.message.answer("Не удалось найти или удалить купон.")
    await query.message.answer("🔮 Главное меню", reply_markup=await kb.menu())


@router_u.callback_query(F.data.startswith("return_to_menu"))
async def return_to_menu(query: types.CallbackQuery):
    await query.message.answer('🔮 Главное меню', reply_markup=await kb.menu())
