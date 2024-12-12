from sqlalchemy import (
    Column,
    Integer,
    String,
    VARCHAR,
    ForeignKey,
    DateTime,
    Double,
    Text,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app import db


class Country(db.Model):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    code = Column(VARCHAR(5), unique=True, nullable=False)

    def __repr__(self):
        return f"Country({self.id}, '{self.name}', '{self.code}')"


class Airport(db.Model):
    __tablename__ = "airports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    code = Column(VARCHAR(5), unique=True, nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    country = relationship("Country", backref="airports", lazy=True)

    def __repr__(self):
        return f"Airport({self.id}, '{self.name}', '{self.code}', '{self.country_id}')"

    @property
    def country_name(self):
        return self.country.name if self.country else None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "country_name": self.country_name,
        }


class Airline(db.Model):
    __tablename__ = "airlines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    def __repr__(self):
        return f"Airline({self.id}, '{self.name}')"


class Aircraft(db.Model):
    __tablename__ = "aircrafts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    airline = relationship("Airline", backref="aircrafts", lazy=True)

    def __repr__(self):
        return f"Aircraft({self.id}, '{self.airline.name}', '{self.name}')"

    def is_available(self, depart_time, arrive_time):
        for flight in self.flights:
            if flight.depart_time < arrive_time and flight.arrive_time > depart_time:
                return False
        return True

    @property
    def airline_name(self):
        return self.airline.name if self.airline else "N/A"


class SeatClass(db.Model):
    __tablename__ = "seat_classes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    def __repr__(self):
        return f"SeatClass({self.id}, '{self.name}')"


class AircraftSeat(db.Model):
    __tablename__ = "aircraft_seats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    aircraft_id = Column(Integer, ForeignKey("aircrafts.id"), nullable=False)
    seat_class_id = Column(Integer, ForeignKey("seat_classes.id"), nullable=False)
    seat_name = Column(String(5), nullable=False)
    aircraft = relationship("Aircraft", backref="seats", lazy=True)
    seat_class = relationship("SeatClass", backref="seats", lazy=True)

    def __repr__(self):
        return f"AircraftSeat({self.id}, {self.aircraft}, '{self.seat_class.name}', '{self.seat_name}')"


class FlightSeat(db.Model):
    __tablename__ = "flight_seats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    aircraft_seat_id = Column(Integer, ForeignKey("aircraft_seats.id"), nullable=False)
    price = Column(Double, nullable=False)
    currency = Column(VARCHAR(20), nullable=False)
    flight = relationship("Flight", backref="seats", lazy=True)
    aircraft_seat = relationship("AircraftSeat", backref="flight_seats", lazy=True)

    def __repr__(self):
        return f"FlightSeat({self.id}, Flight-{self.flight_id}, '{self.aircraft_seat.seat_name}', '{self.aircraft_seat.seat_class.name}', {self.price}-{self.currency})"


class Route(db.Model):
    __tablename__ = "routes"
    __table_args__ = (
        UniqueConstraint("depart_airport_id", "arrive_airport_id", name="unique_route"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    depart_airport_id = Column(
        Integer, ForeignKey("airports.id", ondelete="CASCADE"), nullable=False
    )
    arrive_airport_id = Column(
        Integer, ForeignKey("airports.id", ondelete="CASCADE"), nullable=False
    )
    depart_airport = relationship(
        "Airport", foreign_keys=[depart_airport_id], backref="depart_routes"
    )
    arrive_airport = relationship(
        "Airport", foreign_keys=[arrive_airport_id], backref="arrive_routes"
    )

    def __repr__(self):
        return f"Route({self.id}, '{self.depart_airport}', '{self.arrive_airport}')"

    def to_dict(self):
        return {
            "id": self.id,
            "depart_airport": self.depart_airport.name,
            "arrive_airport": self.arrive_airport.name,
        }


class Flight(db.Model):
    __tablename__ = "flights"
    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    depart_time = Column(DateTime, nullable=False)
    arrive_time = Column(DateTime, nullable=False)
    aircraft_id = Column(Integer, ForeignKey("aircrafts.id"), nullable=False)
    route = relationship("Route", backref="flights", lazy=True)
    aircraft = relationship("Aircraft", backref="flights", lazy=True)

    __table_args__ = (
        CheckConstraint("depart_time < arrive_time", name="check_depart_time"),
    )

    def __repr__(self):
        return f"Flight({self.id}, {self.route}, '{self.depart_time}', '{self.arrive_time}', {self.aircraft})"

    def to_dict(self):
        return {
            "id": self.id,
            "route_id": self.route_id,
            "depart_time": self.depart_time.isoformat(),
            "arrive_time": self.arrive_time.isoformat(),
            "aircraft_id": self.aircraft_id,
        }


class IntermediateAirport(db.Model):
    __tablename__ = "intermediate_airports"

    airport_id = Column(
        Integer, ForeignKey("airports.id"), primary_key=True, nullable=False
    )  # Sân bay
    flight_id = Column(
        Integer, ForeignKey("flights.id"), primary_key=True, nullable=False
    )  # Chuyến bay
    arrival_time = Column(DateTime, primary_key=True, nullable=False)  # Thời gian đến
    departure_time = Column(DateTime, nullable=False)  # Thời gian đi
    order = Column(Integer, nullable=False)  # Thứ tự

    # Quan hệ
    airport = relationship("Airport", backref="intermediate_airports", lazy=True)
    flight = relationship("Flight", backref="intermediate_airports", lazy=True)

    def __repr__(self):
        return (
            f"IntermediateAirport('{self.airport_id}', '{self.flight_id}', "
            f"'{self.arrival_time}', '{self.departure_time}', '{self.order}')"
        )

    def to_dict(self):
        return {
            "airport_id": self.airport_id,
            "flight_id": self.flight_id,
            "arrival_time": self.arrival_time.isoformat(),
            "departure_time": self.departure_time.isoformat(),
            "order": self.order,
        }


class Regulation(db.Model):
    __tablename__ = "regulations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(150), unique=True, nullable=False)
    value = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
