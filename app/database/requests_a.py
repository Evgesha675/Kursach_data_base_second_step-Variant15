from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database.models import Airline, Ticket, Coupon, TicketOffice, Cashier, Client
from app.database.models import async_session 
    
    
# Запрос для сохранения авиакомпании в базу данных
async def save_airline_to_db(data: dict) -> None:
    try:
        async with async_session as session:
            new_airline = Airline(name=data['name'], address=data['address'])
            session.add(new_airline)
            await session.commit()
        return True 
    except Exception as e:
        return False  
    
# Запросы для обновления данных в бд авиакомпаний
async def update_airline_name(airline_id: int, new_name: str):
    async with async_session as session:
        async with session.begin():
            airline = await session.get(Airline, airline_id)
            if airline:
                airline.name = new_name
        await session.commit()
        await session.refresh(airline)  
    return airline

async def update_airline_address(airline_id: int, new_address: str):
    async with async_session as session:
        async with session.begin():
            airline = await session.get(Airline, airline_id)
            if airline:
                airline.address = new_address
        await session.commit()
        await session.refresh(airline)  
    return airline

# Запрос для удаления авиакомпании из бд
async def delete_airline_from_db(airline_id):
    async with async_session as session:
        airline = await session.get(Airline, airline_id)
        if airline:
            await session.delete(airline)
            await session.commit()
            return True
    return False

async def get_tickets_info_by_month_and_airline(airline_id, month):
    async with async_session as session:
        result = await session.execute(
            select(
                Ticket.id.label('ticket_id'),
                Ticket.ticket_type,
                Ticket.sale_date,
                TicketOffice.address.label('ticket_office_name'),
                Cashier.full_name.label('cashier_name'),
                Airline.name.label('airline_name'),
                Client.full_name.label('client_name'),
                Client.passport_series,
                Client.passport_number
            )
            .join(Airline, Ticket.airline_id == Airline.id)
            .join(TicketOffice, Ticket.ticket_office_id == TicketOffice.id)
            .join(Cashier, Ticket.cashier_id == Cashier.id)
            .join(Client, Ticket.client_passport_number == Client.passport_number)
            .filter(Airline.id == airline_id)
            .filter(func.substr(Ticket.sale_date, 4, 2) == str(month).lower())
        )
        tickets_info = [
            Ticket(
                id=ticket.ticket_id,
                ticket_type=ticket.ticket_type,
                sale_date=ticket.sale_date,
                ticket_office=TicketOffice(address=ticket.ticket_office_name),
                cashier=Cashier(full_name=ticket.cashier_name),
                airline=Airline(name=ticket.airline_name),
                client=Client(
                    full_name=ticket.client_name,
                    passport_series=ticket.passport_series,
                    passport_number=ticket.passport_number
                )
            ) for ticket in result.fetchall() if ticket.passport_series is not None and ticket.passport_number is not None]

        return tickets_info

# Запрос для получения информации о билетах по дате и авиакомпании
async def get_tickets_info_by_date_and_airline(airline_id, start_date, finish_date):
    async with async_session as session:
        result = await session.execute(
            select(
                Ticket.id.label('ticket_id'),
                Ticket.ticket_type,
                Ticket.sale_date,
                TicketOffice.address.label('ticket_office_name'),
                Cashier.full_name.label('cashier_name'),
                Airline.name.label('airline_name'),
                Client.full_name.label('client_name'),
                Client.passport_series,
                Client.passport_number,
                Coupon.id.label('coupon_id'),
                Coupon.flight_direction,
                Coupon.fare
            )
            .join(Airline, Ticket.airline_id == Airline.id)
            .join(TicketOffice, Ticket.ticket_office_id == TicketOffice.id)
            .join(Cashier, Ticket.cashier_id == Cashier.id)
            .join(Client, Ticket.client_passport_number == Client.passport_number)
            .outerjoin(Coupon, Ticket.id == Coupon.ticket_id) 
            .filter(Airline.id == airline_id)
            .filter(Ticket.sale_date >= start_date)
            .filter(Ticket.sale_date <= finish_date)
            .order_by(Ticket.sale_date)
        )

        print(f"SQL Query: {result}")

        tickets_info = [
            Ticket(
                id=ticket.ticket_id,
                ticket_type=ticket.ticket_type,
                sale_date=ticket.sale_date,
                ticket_office=TicketOffice(address=ticket.ticket_office_name),
                cashier=Cashier(full_name=ticket.cashier_name),
                airline=Airline(name=ticket.airline_name),
                client=Client(
                    full_name=ticket.client_name,
                    passport_series=ticket.passport_series,
                    passport_number=ticket.passport_number
                ),
                coupons=[Coupon(
                    id=ticket.coupon_id,
                    flight_direction=ticket.flight_direction,
                    fare=ticket.fare
                )] if ticket.coupon_id is not None else []  
            ) for ticket in result.fetchall()]

        print(f"Tickets Info: {tickets_info}")
        return tickets_info

async def get_tickets_info_by_airline(airline_id: int):
    async with async_session as session:
        # Выбираем авиакомпанию и связанные с ней билеты, а также связанные с билетами купоны
        result = await session.execute(
            select(Airline)
            .options(selectinload(Airline.tickets).selectinload(Ticket.coupons))
            .filter(Airline.id == airline_id)
        )

        airline = result.scalar()

        if airline:
            return airline.tickets
        else:
            return []
