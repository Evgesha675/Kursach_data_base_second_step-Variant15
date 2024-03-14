import pandas as pd
import io
from openpyxl.utils.dataframe import dataframe_to_rows
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.fsm.state import State, StatesGroup

import app.keyboards as kb
from config import ADMIN_TELEGRAM_ID, EditAirlineStates

from app.database.requests import get_airline_info_by_id
from app.database.requests_a import save_airline_to_db, delete_airline_from_db, update_airline_name, update_airline_address, get_tickets_info_by_month_and_airline, get_tickets_info_by_date_and_airline, get_tickets_info_by_airline


router_a = Router()

class AddAirlineStates(StatesGroup):
    name = State()
    address = State()
    airline_id = State()

class OtchetAirlineStates(StatesGroup):
    airlines_id = State()

class DataAirlineStates(StatesGroup):
    airlines_id = State()
    time_start = State()
    time_finish = State()
    

@router_a.message(Command("commands"))
async def start_add_movie(message: Message, state: FSMContext) -> None:
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f"Список всех доступных команд\n\n"
                             f"/airlines - Возможоность Добавить/Изменить/Удалить авиакомпанию\n\n"
                             f"/tickets_rented_by_month - Отчёт: Билеты, проданные за указанный месяц указанной авиакомпании \n\n"
                             f"/summ_by_ailines - Отчёт: Общая сумма от продаж билетов каждой авиакомпании \n\n"
                             f"/airlines_by_date - Отчёт: Список клиентов авиакомпаний на заданную дату \n\n")                       
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")
        
# Работа с авиакомпаниями
@router_a.message(Command("airlines"))
async def Airlines(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f'Выберите авикомпанию, чтобы узнать подробную информацию:', reply_markup=await kb.airlines_adm())  
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")
        
@router_a.callback_query(F.data.startswith("airlines_adm:"))
async def Airlines_inf(query: types.CallbackQuery, state: FSMContext):
    airline_id = int(query.data.split(":")[1])
    airline_info = await get_airline_info_by_id(airline_id)
    if airline_info:
        text = (
            f"<b>Информация об авиакомпании {airline_info['name']}:</b>\n\n"
            f"<i>ID:</i> {airline_info['id']}\n"
            f"<i>Имя:</i> {airline_info['name']}\n"
            f"<i>Адрес:</i> {airline_info['address']}")
        await query.message.answer(text, reply_markup=await kb.airlines_keyboard_act(airline_id))
    else:
        await query.message.answer("Авиакомпания не найдена.", reply_markup=await kb.return_to_menu())
        
# Добавление новой авиакомпании
@router_a.callback_query(F.data.startswith("action.airlines.add_"))
async def Airline_ad(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer(f"Давайте добавим новую авиакомпанию.\n\nВведите название:")
    await state.set_state(AddAirlineStates.name) 

@router_a.message(AddAirlineStates.name)
async def Process_airline_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите адрес авиакомпании:")
    await state.set_state(AddAirlineStates.address) 

@router_a.message(AddAirlineStates.address)
async def Process_airline_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    name = data.get('name', '')
    address = data.get('address', '')

    # Попробуем сохранить данные и проверим, успешно ли это прошло
    success = await save_airline_to_db({'name': name, 'address': address})

    if success:
        await message.answer("Авиакомпания успешно добавлена в базу данных!")
        text = (f"Добавлена новая авиакомпания:\n\n"
                f"Название: <b>{name}</b>\n"
                f"Адрес: <b>{address}</b>\n")
        await message.answer(text,reply_markup=await kb.menu())
        await state.clear()
    else:
        await message.answer("Произошла ошибка при сохранении данных. Пожалуйста, попробуйте снова.")

# Изменение уже существующей авиакомпании
@router_a.callback_query(F.data.startswith("action.airlines.edit_"))
async def Airline_edit(query: types.CallbackQuery, state: FSMContext):
    airline_id_str = query.data.split("_")[1]
    airline_id = int(airline_id_str)
    await query.message.answer("Выберите, какой параметр хотите изменить:", reply_markup=await kb.airline_edit_keyboard(airline_id, state))

@router_a.callback_query(F.data.startswith("action.airline.address"))
async def Airline_edit_address(query: types.CallbackQuery, state: FSMContext):
    airline_id_str = query.data.split("_")[1]
    airline_id = int(airline_id_str)
    await query.message.answer("Введите новый адрес для авиакомпании:")
    await state.update_data(airline_id=airline_id)
    await state.set_state(EditAirlineStates.address_edit)

@router_a.message(EditAirlineStates.address_edit)
async def Process_airline_edit_address(message: Message, state: FSMContext):
    new_address = message.text
    data = await state.get_data()
    airline_id = data.get('airline_id')
    success = await update_airline_address(airline_id, new_address)

    if success:
        await message.answer("Адрес успешно изменен!")
    else:
        await message.answer("Не удалось изменить адрес. Пожалуйста, попробуйте снова.")
    
    await state.clear()

@router_a.callback_query(F.data.startswith("action.airline.name"))
async def Airline_edit_name(query: types.CallbackQuery, state: FSMContext):
    airline_id_str = query.data.split("_")[1]
    airline_id = int(airline_id_str)
    await query.message.answer("Введите новое название для авиакомпании:")
    await state.update_data(airline_id=airline_id)
    await state.set_state(EditAirlineStates.name_edit)

@router_a.message(EditAirlineStates.name_edit)
async def Process_airline_edit_name(message: Message, state: FSMContext):
    new_name = message.text
    data = await state.get_data()
    airline_id = data.get('airline_id')
    success = await update_airline_name(airline_id, new_name)

    if success:
        await message.answer("Название успешно изменено!")
    else:
        await message.answer("Не удалось изменить название. Пожалуйста, попробуйте снова.")
    
    await state.clear()

# Удаление авиакомпании из бд
@router_a.callback_query(F.data.startswith("action.airlines.delete_"))
async def Airline_delete(query: types.CallbackQuery):
    airline_id_str = query.data.split("_")[1]
    airline_id = int(airline_id_str)
    success = await delete_airline_from_db(airline_id)
    if success:
        await query.message.answer("Авиакомпания успешно удалена из базы данных.")
    else:
        await query.message.answer("Не удалось найти или удалить авиакомпанию.")
    await query.message.answer("🔮 Главное меню", reply_markup=await kb.menu())
        
# Отчёт: Билеты, проданные за указанный месяц указанной авиакомпании 
@router_a.message(Command("tickets_rented_by_month"))
async def tickets_rented_by_month(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f'Выберите авикомпанию, чтобы узнать подробную информацию:', reply_markup=await kb.airlines_otchet())  
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@router_a.callback_query(F.data.startswith("airlines_otchet:"))
async def tickets_rented_by_month_start(query: types.CallbackQuery, state: FSMContext):
    airlines_id_str = query.data.split(":")[1]
    airlines_id = int(airlines_id_str)
    await state.update_data(airlines_id=airlines_id)
    await query.message.answer(f'Выберите месяц, чтобы получить отчёт:', reply_markup=await kb.airlines_month())  

@router_a.callback_query(F.data.startswith("airlines.month_"))
async def tickets_rented_by_month_month(query: types.CallbackQuery, state: FSMContext):
    try:
        month_str = query.data[-2:]  
        month = int(month_str)
        data = await state.get_data()
        airline_id = data.get('airlines_id')

        # Получаем билеты за указанный месяц и авиакомпанию
        tickets = await get_tickets_info_by_month_and_airline(airline_id, month)

        if tickets:
            # Создаем DataFrame и отправляем Excel-файл 
            df = pd.DataFrame([
                {
                    "ID билета": ticket.id,
                    "Тип билета": ticket.ticket_type,
                    "Дата продажи": ticket.sale_date,
                    "Серия и номер паспорта клиента": f"{str(ticket.client.passport_series)} {str(ticket.client.passport_number)}",
                    "Имя авиакомпании": ticket.airline.name,
                    "Адрес офиса продаж": ticket.ticket_office.address,
                    "ФИО кассира": ticket.cashier.full_name,
                } for ticket in tickets
            ], columns=["ID билета", "Тип билета", "Дата продажи", "Серия и номер паспорта клиента", "Имя авиакомпании", "Адрес офиса продаж", "ФИО кассира"])

            # Создаем Excel-файл
            excel_content = io.BytesIO()
            with pd.ExcelWriter(excel_content, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Sheet1", index=False)
                worksheet = writer.sheets["Sheet1"]
                # Расширяем столбцы по ширине данных
                for i, col in enumerate(df.columns):
                    max_len = df[col].astype(str).apply(len).max()
                    worksheet.set_column(i, i, max_len + 2)

            # Отправляем Excel-файл
            input_file = BufferedInputFile(excel_content.getvalue(), filename=f"report_airline_{airline_id}_month_{month}.xlsx")
            await query.message.answer_document(input_file, caption=f"Отчет по билетам за месяц {month} для авиакомпании ")
            await state.clear()
        else:
            await query.message.answer(f"Данные о билетах за месяц {month} для авиакомпании не найдены.")
            await state.clear()
    except ValueError as e:
        print("ValueError:", e)
        await query.message.answer("Произошла ошибка при обработке запроса.")
        await state.clear()

        
# Отчёт: Общая сумма от продаж билетов каждой авиакомпании
@router_a.message(Command("summ_by_ailines"))
async def summ_by_ailines(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f'Выберите авикомпанию, чтобы узнать подробную информацию:', reply_markup=await kb.summ_by_airlines())
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@router_a.callback_query(F.data.startswith("summ_by_airlines:"))
async def summ_by_ailines_start(query: types.CallbackQuery, state: FSMContext):
    airline_id = int(query.data.split(":")[1])
    tickets = await get_tickets_info_by_airline(airline_id)
    total_sales_by_airline = calculate_total_sales_by_airline(tickets)
    await query.message.answer(f"Общая сумма продаж для выбранной авиакомпании: {total_sales_by_airline}.")

# Функция для вычисления общей суммы продаж для выбранной авиакомпании
def calculate_total_sales_by_airline(tickets):
    total_sales = 0
    for ticket in tickets:
        for coupon in ticket.coupons:
            total_sales += coupon.fare
    return total_sales

# Отчёт: Список клиентов авиакомпаний на заданную дату
@router_a.message(Command("airlines_by_date"))
async def Airlines(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_TELEGRAM_ID:
        await message.answer(f'Выберите авикомпанию, чтобы продолжить получение отчёта', reply_markup=await kb.airlines_data())
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

@router_a.callback_query(F.data.startswith("airlines_data:"))
async def airlines_data_start(query: types.CallbackQuery, state: FSMContext):
    airlines_id_str = query.data.split(":")[1]
    airlines_id = int(airlines_id_str)
    await state.update_data(airlines_id=airlines_id)
    await query.message.answer(f'Введите начальную дату в формате "ДД.ММ.ГГГГ":')
    await state.set_state(DataAirlineStates.time_start)

@router_a.message(DataAirlineStates.time_start)
async def airlines_data_start_data(message: Message, state: FSMContext):
    time_start = message.text
    if time_start:
        try:
            await state.update_data(time_start=time_start)
            await message.answer(f'Введите конечную дату в формате "ДД.ММ.ГГГГ":')
            await state.set_state(DataAirlineStates.time_finish)
        except ValueError:
            await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате 'ДД.ММ.ГГГГ'.")

@router_a.message(DataAirlineStates.time_finish)
async def airlines_data_finish_data(message: Message, state: FSMContext):
    time_finish = message.text
    if time_finish:
        try:
            await state.update_data(time_finish=time_finish)

            data = await state.get_data()
            airlines_id = data.get('airlines_id')
            time_finish = data.get('time_finish')
            time_start = data.get('time_start')
            print(time_start, time_finish)
            # Получаем билеты для указанной авиакомпании в заданном временном диапазоне
            tickets = await get_tickets_info_by_date_and_airline(airlines_id, time_start, time_finish)

            if tickets:
                # Создаем Excel-файл
                excel_content = await create_excel_file(tickets, "Название авиакомпании", time_start, time_finish)
                input_file = BufferedInputFile(excel_content, filename=f"report_airline_{airlines_id}_dates_{time_start}_to_{time_finish}.xlsx")
                await message.answer_document(input_file, caption=f"Отчет по билетам за период с {time_start} по {time_finish} для авиакомпании {airlines_id}")
                await state.clear()
            else:
                await message.answer(f"Данные о билетах за период с {time_start} по {time_finish} для авиакомпании {airlines_id} не найдены.")
                await state.clear()
        except ValueError:
            await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате 'ГГГГ-ММ-ДД'.")
            
async def create_excel_file(tickets, airline_name, start_date, finish_date):
    # Создаем DataFrame
    df = pd.DataFrame([
        {
            "ID билета": ticket.id,
            "Тип билета": ticket.ticket_type,
            "Дата продажи": ticket.sale_date,
            "Касса": ticket.ticket_office.address,
            "Кассир": ticket.cashier.full_name,
            "Авиакомпания": ticket.airline.name,
            "Клиент": ticket.client.full_name,
            "Серия паспорта клиента": ticket.client.passport_series,
            "Номер паспорта клиента": ticket.client.passport_number,
            "ID купона": ticket.coupons[0].id if ticket.coupons else None,
            "Направление полета": ticket.coupons[0].flight_direction if ticket.coupons else None,
            "Цена билета": ticket.coupons[0].fare if ticket.coupons else None,
        } for ticket in tickets
    ])

    # Создаем Excel-файл
    excel_content = io.BytesIO()
    with pd.ExcelWriter(excel_content, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)
        worksheet = writer.sheets["Sheet1"]
        # Расширяем столбцы по ширине данных
        for i, col in enumerate(df.columns):
            max_len = df[col].astype(str).apply(len).max()
            worksheet.set_column(i, i, max_len + 2)

    # Отправляем Excel-файл
    return excel_content.getvalue()