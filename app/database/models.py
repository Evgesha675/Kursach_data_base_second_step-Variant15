from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from config import SQLALCHEMY_URL

engine = create_async_engine(SQLALCHEMY_URL, echo=True)
async_session = AsyncSession(engine)
Base = declarative_base()

class Airline(Base):
    __tablename__ = 'airlines'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)

    ticket_offices = relationship('TicketOffice', back_populates='airline')
    tickets = relationship('Ticket', back_populates='airline')

class TicketOffice(Base):
    __tablename__ = 'ticket_offices'

    id = Column(Integer, primary_key=True)
    address = Column(String)
    airline_id = Column(Integer, ForeignKey('airlines.id'))

    airline = relationship('Airline', back_populates='ticket_offices')
    cashiers = relationship('Cashier', back_populates='ticket_office')
    tickets = relationship('Ticket', back_populates='ticket_office')

class Cashier(Base):
    __tablename__ = 'cashiers'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    ticket_office_id = Column(Integer, ForeignKey('ticket_offices.id'))

    ticket_office = relationship('TicketOffice', back_populates='cashiers')
    tickets = relationship('Ticket', back_populates='cashier')

class Client(Base):
    __tablename__ = 'clients'

    passport_number = Column(Integer, primary_key=True)
    passport_series = Column(Integer)
    full_name = Column(String)

    tickets = relationship('Ticket', back_populates='client')

class Coupon(Base):
    __tablename__ = 'coupons'

    id = Column(Integer, primary_key=True)
    flight_direction = Column(String)
    fare = Column(Integer)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))

    ticket = relationship('Ticket', back_populates='coupons')

class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    ticket_type = Column(String)
    sale_date = Column(String)
    ticket_office_id = Column(Integer, ForeignKey('ticket_offices.id'))
    cashier_id = Column(Integer, ForeignKey('cashiers.id'))
    airline_id = Column(Integer, ForeignKey('airlines.id'))
    client_passport_number = Column(Integer, ForeignKey('clients.passport_number'))

    ticket_office = relationship('TicketOffice', back_populates='tickets')
    cashier = relationship('Cashier', back_populates='tickets')
    airline = relationship('Airline', back_populates='tickets')
    client = relationship('Client', back_populates='tickets')
    coupons = relationship('Coupon', back_populates='ticket')

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
