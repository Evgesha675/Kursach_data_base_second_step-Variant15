from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database.models import TicketOffice, Airline, Cashier, Client, Ticket, Coupon
from app.database.models import async_session 


# Запрос для клавиатуры списка уже имеющихся касс
async def get_kassa():
    async with async_session as session:
        result = await session.execute(select(TicketOffice))
        return result.scalars().all()

# Запрос для вывода информации по конкретной кассе по номеру кассы
async def get_kassa_info_by_id(kassa_id):
    async with async_session as session:
        query = (
            select(TicketOffice, Airline.name)
            .join(Airline, TicketOffice.airline_id == Airline.id, isouter=True)
            .where(TicketOffice.id == kassa_id)
        )
        result = await session.execute(query)
        row = result.fetchone()

        if row:
            ticket_office, airline_name = row
            return {
                "id": ticket_office.id,
                "address": ticket_office.address,
                "airline_name": airline_name if airline_name else "Нет данных"
            }
        else:
            return None
        
# Запрос для получения списка авиакомпаний при добавлении новой кассы
async def get_airlines_for_add_kassa():
    async with async_session as session:
        result = await session.execute(select(Airline))
        return result.scalars().all()

# Запрос для сохранения новой кассы в базе данных
async def save_kassa_to_db(data):
    async with async_session as session:
        airline_id = data['airline_code']
        airline = await session.execute(select(Airline).where(Airline.id == airline_id))
        airline = airline.scalar_one_or_none()

        # Если авиакомпания найдена, добавляем кассу
        if airline:
            new_kassa = TicketOffice(address=data['address'], airline=airline)
            session.add(new_kassa)
            await session.commit()

# Запрос для получения имени авиакомпании по её коду (id)
async def get_airline_name_by_code(airline_code):
    async with async_session as session:
        airline = await session.execute(select(Airline).where(Airline.id == airline_code))
        airline = airline.scalar_one_or_none()
        return airline.name if airline else "Нет данных"

# Запрос для вывода информации о кассе по её номеру (id)
async def get_kassa_by_number(kassa_number):
    async with async_session as session:
        kassa = await session.execute(select(TicketOffice).where(TicketOffice.id == kassa_number))
        return kassa.scalar_one_or_none()
        
    
# Запросы для обовления данных в бд    
async def update_kassa_address(kassa_id: int, new_address: str):
    async with async_session as session:
        async with session.begin():
            kassa = await session.get(TicketOffice, kassa_id)
            if kassa:
                kassa.address = new_address
        await session.commit()

async def update_kassa_airline(kassa_id: int, airline_id: int):
    async with async_session as session:
        async with session.begin():
            kassa = await session.get(TicketOffice, kassa_id)
            if kassa:
                kassa.airline_id = airline_id
        await session.commit()

async def get_all_airlines_for_edit_kassa():
    async with async_session as session:
        airlines_list = await session.execute(select(Airline).order_by(Airline.name))
        return airlines_list.scalars().all()
    
# Запросы для удаления данных из бд
async def delete_kassa_from_db(kassa_id):
    async with async_session as session:
        kassa = await session.get(TicketOffice, kassa_id)
        if kassa:
            await session.delete(kassa)
            await session.commit()
            return True
    return False

# Запрос для вывода информации о авиакомпании по её id
async def get_airline_info_by_id(airline_id: int):
    async with async_session as session:
        airline = await session.get(Airline, airline_id)
        if airline:
            return {
                'id': airline.id,
                'name': airline.name,
                'address': airline.address,
            }
    return None

# Запрос для клавиатуры списка уже имеющихся кассиров
async def get_cashiers():
    async with async_session as session:
        result = await session.execute(select(Cashier))
        return result.scalars().all()

# Запрос для вывода информации по конкретному кассиру по номеру кассира
async def get_kassir_info_by_id(kassir_id):
    async with async_session as session:
        query = (
            select(Cashier, TicketOffice.address.label("kassa_address"))
            .join(TicketOffice, Cashier.ticket_office_id == TicketOffice.id, isouter=True)
            .where(Cashier.id == kassir_id)
        )
        result = await session.execute(query)
        row = result.fetchone()

        if row:
            cashier, kassa_address = row
            return {
                "id": cashier.id,
                "full_name": cashier.full_name,
                "kassa_address": kassa_address if kassa_address else "Нет данных"
            }
        else:
            return None
        
# Запросы при добавления кассира
# Запрос для получения списка касс для добавления кассира
async def get_kassas_for_add_cashier():
    async with async_session as session:
        result = await session.execute(select(TicketOffice))
        return result.scalars().all()

# Запрос для сохранения нового кассира в базе данных
async def save_cashier_to_db(data):
    full_name = data.get('full_name')
    kassa_code = data.get('kassa_code')

    async with async_session as session:
        async with session.begin():
            kassa = await session.get(TicketOffice, kassa_code)
            if kassa:
                new_cashier = Cashier(full_name=full_name, ticket_office_id=kassa.id)
                session.add(new_cashier)
        await session.commit()

# Запрос для получения адреса кассы по её коду
async def get_kassa_address_by_code(kassa_code):
    async with async_session as session:
        kassa = await session.get(TicketOffice, kassa_code)
        return kassa.address if kassa else "Касса не найдена"

# Запросы для изменения кассира
# Запрос для обновления ФИО кассира
async def update_kassir_full_name(kassir_id, new_full_name):
    async with async_session as session:
        kassir = await session.get(Cashier, kassir_id)
        if kassir:
            kassir.full_name = new_full_name
            await session.commit()
            return True
    return False

# Запросы для обновления места работы кассира
async def update_kassir_ticket_office(kassir_id, ticket_office_id):
    async with async_session as session:
        kassir = await session.get(Cashier, kassir_id)
        if kassir:
            ticket_office = await session.get(TicketOffice, ticket_office_id)
            if ticket_office:
                kassir.ticket_office = ticket_office
                await session.commit()
                return True
    return False

async def get_all_ticket_offices():
    async with async_session as session:
        ticket_offices = await session.execute(select(TicketOffice).order_by(TicketOffice.address))
        return ticket_offices.scalars().all()

# Запросы для удаления кассира
async def delete_kassir_from_db(kassir_id):
    async with async_session as session:
        kassir = await session.get(Cashier, kassir_id)
        if kassir:
            await session.delete(kassir)
            await session.commit()
            return True
    return False

# Функция для добавления нового клиента
async def save_client_to_db(client_data):
    passport_number = client_data.get('passport_number', '')
    passport_series = client_data.get('passport_series', '')
    full_name = client_data.get('full_name', '')

    async with async_session as session:
        client = Client(passport_number=passport_number, passport_series=passport_series, full_name=full_name)
        session.add(client)
        await session.commit()
        return True
    
# Функция для изменения данных о клиенте
async def update_client_full_name(client_passport_number, new_full_name):
    async with async_session as session:
        client = await session.get(Client, client_passport_number)
        if client:
            client.full_name = new_full_name
            await session.commit()
            return True
    return False

# Функция удаления клиента из базы данных
async def delete_client_from_db(passport_number):
    async with async_session as session:
        client = await session.get(Client, passport_number)
        if client:
            await session.delete(client)
            await session.commit()
            return True
    return False

# Функция для получения списка всех клиентов
async def get_all_clients():
    async with async_session as session:
        clients = await session.execute(select(Client))
        return clients.scalars().all()
   
# Запрос для получения подробной информации о клиенте 
async def get_client_info_by_passport(passport_number):
    async with async_session as session:
        query = select(Client).where(Client.passport_number == passport_number)
        result = await session.execute(query)
        client = result.scalar()

        if client:
            return {
                'full_name': client.full_name,
                'passport_series': client.passport_series,
                'passport_number': client.passport_number,
            }
    return None

# Запрос для клавиатуры списка уже имеющихся кассиров
async def get_tickets():
    async with async_session as session:
        result = await session.execute(select(Ticket))
        return result.scalars().all()
    
# Запрос для вывода информации по конкретному билету по его ID
async def get_ticket_info_by_id(ticket_id):
    async with async_session as session:
        query = (
            select(Ticket, TicketOffice.address.label('ticket_office_address'),
                   Cashier.full_name.label('cashier_full_name'), Airline.name.label('airline_name'),
                   Client.full_name.label('client_full_name'))
            .join(TicketOffice, Ticket.ticket_office_id == TicketOffice.id, isouter=True)
            .join(Cashier, Ticket.cashier_id == Cashier.id, isouter=True)
            .join(Airline, Ticket.airline_id == Airline.id, isouter=True)
            .join(Client, Ticket.client_passport_number == Client.passport_number, isouter=True)
            .where(Ticket.id == ticket_id)
        )
        result = await session.execute(query)
        row = result.fetchone()

        if row:
            ticket, ticket_office_address, cashier_full_name, airline_name, client_full_name = row
            return {
                "ticket_type": ticket.ticket_type,
                "sale_date": ticket.sale_date,
                "ticket_office_address": ticket_office_address if ticket_office_address else "Нет данных",
                "cashier_full_name": cashier_full_name if cashier_full_name else "Нет данных",
                "airline_name": airline_name if airline_name else "Нет данных",
                "client_full_name": client_full_name if client_full_name else "Нет данных",
            }
        else:
            return None
        
# Запросы для добавления нового билета
# Запрос для сохранения нового билета в базу данных
async def save_ticket_to_db(data):
    async with async_session as session:
        ticket = Ticket(
            ticket_type=data['ticket_type'],
            sale_date=data['sale_date'],
            ticket_office_id=data['ticket_office_id'],
            cashier_id=data['cashier_id'],
            airline_id=data['airline_id'],
            client_passport_number=data['client_passport_number']
        )
        session.add(ticket)
        await session.commit()

# Запрос для получения списка всех касс
async def get_ticket_offices():
    async with async_session as session:
        query = select(TicketOffice)
        result = await session.execute(query)
        return result.scalars().all()

# Запрос для получения списка всех кассиров по ID кассы
async def get_cashiers_by_ticket_office(ticket_office_id):
    async with async_session as session:
        query = select(Cashier).where(Cashier.ticket_office_id == ticket_office_id)
        result = await session.execute(query)
        return result.scalars().all()

# Запрос для получения списка всех авиакомпаний
async def get_airlines():
    async with async_session as session:
        query = select(Airline)
        result = await session.execute(query)
        return result.scalars().all()

# Запрос для получения списка всех клиентов
async def get_clients():
    async with async_session as session:
        query = select(Client)
        result = await session.execute(query)
        return result.scalars().all()

# Запрос для получения адреса кассы по её ID
async def get_ticket_office_address(ticket_office_id):
    async with async_session as session:
        query = select(TicketOffice.address).where(TicketOffice.id == ticket_office_id)
        result = await session.execute(query)
        return result.scalar()

# Запрос для получения полного имени кассира по его ID
async def get_cashier_full_name(cashier_id):
    async with async_session as session:
        query = select(Cashier.full_name).where(Cashier.id == cashier_id)
        result = await session.execute(query)
        return result.scalar()

# Запрос для получения полного имени клиента по его номеру паспорта
async def get_client_full_name(client_passport_number):
    async with async_session as session:
        query = select(Client.full_name).where(Client.passport_number == client_passport_number)
        result = await session.execute(query)
        return result.scalar()

# Запрос для получения названия авиакомпании по её ID
async def get_airline_name(airline_id):
    async with async_session as session:
        query = select(Airline.name).where(Airline.id == airline_id)
        result = await session.execute(query)
        return result.scalar()

# Запрос для удаления билета из базы данных
async def delete_ticket_from_db(ticket_id):
    async with async_session as session:
        ticket = await session.get(Ticket, ticket_id)
        if ticket:
            await session.delete(ticket)
            await session.commit()
            return True
    return False

# Функции обновления параметров билета в базе данных
async def update_ticket_type(ticket_id, new_ticket_type):
    async with async_session as session:
        ticket = await session.get(Ticket, ticket_id)
        if ticket:
            ticket.ticket_type = new_ticket_type
            await session.flush()
            await session.commit()
            return True
    return False

async def update_ticket_sale_date(ticket_id, new_sale_date):
    async with async_session as session:
        ticket = await session.get(Ticket, ticket_id)
        if ticket:
            ticket.sale_date = new_sale_date
            await session.commit()
            return True
    return False

async def update_ticket_ticket_office(ticket_id, new_ticket_office_id):
    async with async_session as session:
        ticket = await session.get(Ticket, ticket_id)
        ticket_office = await session.get(TicketOffice, new_ticket_office_id)
        if ticket and ticket_office:
            ticket.ticket_office = ticket_office
            await session.commit()
            return True
    return False

async def update_ticket_cashier(ticket_id, new_cashier_id):
    async with async_session as session:
        ticket = await session.get(Ticket, ticket_id)
        cashier = await session.get(Cashier, new_cashier_id)
        if ticket and cashier:
            ticket.cashier = cashier
            await session.commit()
            return True
    return False

async def update_ticket_airline(ticket_id, new_airline_id):
    async with async_session as session:
        ticket = await session.get(Ticket, ticket_id)
        airline = await session.get(Airline, new_airline_id)
        if ticket and airline:
            ticket.airline = airline
            await session.commit()
            return True
    return False

async def update_ticket_client(ticket_id, new_client_passport_number):
    async with async_session as session:
        ticket = await session.get(Ticket, ticket_id)
        client = await session.get(Client, new_client_passport_number)
        if ticket and client:
            ticket.client = client
            await session.commit()
            return True
    return False

async def get_all_cashiers():
    async with async_session as session:
        query = select(Cashier)
        result = await session.execute(query)
        return result.scalars().all()

async def get_all_airlines():
    async with async_session as session:
        query = select(Airline)
        result = await session.execute(query)
        return result.scalars().all()

# Запрос для клавиатуры купонов
async def get_all_coupon():
    async with async_session as session:
        query = select(Coupon)
        result = await session.execute(query)
        return result.scalars().all()

# Запрос для получения информации о купоне по его ID
async def get_coupon_info_by_id(coupon_id):
    async with async_session as session:
        coupon = await session.execute(select(Coupon).where(Coupon.id == coupon_id))
        result = coupon.scalar()
        return result

# Запрос на сохранении нового купона в базу данных
async def save_selected_ticket_to_coupon(data: dict):
    ticket_id = data.get('ticket_id', '')
    flight_direction = data.get('flight_direction', '')
    fare = data.get('fare', '')

    async with async_session as session:
        ticket = await session.get(Ticket, ticket_id)
        if ticket:
            coupon = Coupon(flight_direction=flight_direction, fare=fare, ticket=ticket)
            session.add(coupon)
            await session.commit()

# Запрос для обновления купона в базе данных по его ID и ID билета
async def update_coupon_ticket(coupon_id, ticket_id):
    async with async_session as session:
        coupon = await session.get(Coupon, coupon_id)
        if coupon:
            ticket = await session.get(Ticket, ticket_id)
            if ticket:
                coupon.ticket = ticket
                await session.commit()

# Запрос для получения всех билетов для редактирования купона
async def get_all_tickets_for_edit_coupon():
    async with async_session as session:
        tickets = await session.execute(select(Ticket))
        return tickets.scalars().all()

# Запрос для обновления тарифа купона
async def update_coupon_fare(coupon_id, new_fare):
    async with async_session as session:
        coupon = await session.get(Coupon, coupon_id)
        if coupon:
            coupon.fare = new_fare
            await session.commit()

# Запрос для обновления направления полета купона
async def update_coupon_flight_direction(coupon_id, new_flight_direction):
    async with async_session as session:
        coupon = await session.get(Coupon, coupon_id)
        if coupon:
            coupon.flight_direction = new_flight_direction
            await session.commit()
                
# Запрос для удаления купона из базы данных
async def delete_coupon_from_db(coupon_id):
    async with async_session as session:
        coupon = await session.get(Coupon, coupon_id)
        if coupon:
            await session.delete(coupon)
            await session.commit()
            return True
    return False