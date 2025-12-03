#!/usr/bin/env python
'''Talk to Google to get flights on a range of dates'''

import datetime
import logging
from typing import List
import google_flights
from google_flights.decoder import Itinerary
from govuk_bank_holidays.bank_holidays import BankHolidays

def sanitize_airport_list(airport_str: str) -> list[str]:
    """ Sanitize and validate airport input. """
    if not isinstance(airport_str, str):
        raise ValueError("Airport list must be a string")
    airports = [airport.strip().upper() for airport in airport_str.replace(',', ' ').split()]
    if any(len(airport) != 3 or not airport.isalpha() for airport in airports):
        raise ValueError("All airport codes must be three letters long and alphabetic.")
    return airports

def check_day(dt: datetime.datetime,
              from_airport: List[str],
              to_airport: List[str]) -> List[Itinerary]:
    '''Find all flights on a given day for a source/destination list'''
    d = dt.strftime("%Y-%m-%d")
    flight_filter = google_flights.create_filter(
        flight_data=[
            google_flights.FlightData(
                date=d,
                to_airport=to_airport,
                from_airport=from_airport,
            ),
        ],
        trip="one-way",
        passengers=google_flights.Passengers(adults=1,
                                             children=0,
                                             infants_in_seat=0,
                                             infants_on_lap=0),
        seat="economy",
        max_stops=0,
    )
    logging.debug(flight_filter)
    flight_data = google_flights.get_flights_from_filter(flight_filter,
                                                         data_source='js',
                                                         mode="common")
    logging.debug(flight_data)
    assert flight_data is not None

    return ((flight_data.best if flight_data.best is not None else []) +
            (flight_data.other if flight_data.other is not None else []))

def format_date_time(date: List[int], time: List[int]) -> str:
    '''Format an Itinery datetime into something human-readable'''
    dt = datetime.datetime(date[0], date[1], date[2], time[0], time[1] if len(time) > 1 else 0)
    return (f"{dt.strftime("%a")} "
            f"{date[0]:04d}/{date[1]:02d}/{date[2]:02d} "
            f"{time[0]:02d}:{time[1] if len(time) > 1 else 0:02d}")

def format_flight(flight: Itinerary,
                  html: bool = False,
                  preferred: str|None = None) -> List[str]:
    '''Format a flight Itinerary into a List for tabulate'''
    code = f"{flight.flights[0].airline}{flight.flights[0].flight_number}"

    airports = f"{flight.flights[0].departure_airport} - {flight.flights[0].arrival_airport}"
    if preferred in (flight.flights[0].departure_airport, flight.flights[0].arrival_airport):
        if html:
            code = f'<p class="highlight">{code}</p>'
            airports = f'<p class="highlight">{airports}</p>'
        else:
            airports = f"** {airports} **"
    elif not html:
        airports = f"   {airports}   "

    depdatetime = format_date_time(
        [
            flight.flights[0].departure_date[0],
            flight.flights[0].departure_date[1],
            flight.flights[0].departure_date[2]
        ],
        list(flight.flights[0].departure_time))

    arr_hours = (flight.flights[0].arrival_time[0]
                 if isinstance(flight.flights[0].arrival_time[0], int)
                 else 0)
    arr_minutes = (flight.flights[0].arrival_time[1]
                   if len(flight.flights[0].arrival_time) > 1
                   else 0)
    arrtime = f"{arr_hours:02d}:{arr_minutes:02d}"

    return [
        code,
        airports,
        depdatetime,
        arrtime,
        f"{flight.itinerary_summary.currency} {flight.itinerary_summary.price}",
    ]

def get_flights(start_date: datetime.datetime,
                end_date: datetime.datetime,
                from_airport: List[str],
                to_airport: List[str],
                split_working_hours: bool = False,
                html: bool = False,
                preferred: str|None = None) -> tuple[List[List[str]], List[List[str]]]:
    '''Gets flights on a range of dates'''
    assert isinstance(start_date, datetime.datetime)
    assert isinstance(end_date, datetime.datetime)
    assert isinstance(from_airport, list)
    assert isinstance(to_airport, list)
    assert isinstance(split_working_hours, bool)
    assert isinstance(html, bool)
    assert isinstance(preferred, str) or preferred is None

    logging.debug("Date range: %s %s", start_date, end_date)
    logging.debug("From: %s", from_airport)
    logging.debug("To: %s", to_airport)
    bank_holidays = BankHolidays(use_cached_holidays=True)
    flight_table: List[List[str]] = []
    reject_table: List[List[str]] = []

    for day in range((end_date - start_date).days + 1):
        dt = start_date + datetime.timedelta(days=day)
        all_flights = check_day(dt,
                                from_airport,
                                to_airport)

        for flight in sorted(
            all_flights
            if all_flights is not None else [], key=lambda x: format_date_time(
                [
                    x.flights[0].departure_date[0],
                    x.flights[0].departure_date[1],
                    x.flights[0].departure_date[2]
                ],
                list(x.flights[0].departure_time))):
            if len(flight.flights) != 1:
                continue

            if (not split_working_hours
                or not bank_holidays.is_work_day(dt, division="england-and-wales")
                or flight.flights[0].departure_time[0] > 18):
                flight_table.append(format_flight(flight, html, preferred))
            else:
                reject_table.append(format_flight(flight, html, preferred))

    logging.debug(flight_table)
    logging.debug(reject_table)
    return (flight_table, reject_table)
