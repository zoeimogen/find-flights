#!/usr/bin/env python
'''Flight finder'''
import datetime
import os
import logging
import tabulate
import tap
from dotenv import load_dotenv
from get_from_google import get_flights, sanitize_airport_list

class ArgumentParser(tap.Tap):
    '''Force typing of arguments'''
    from_airport: str
    to_airport: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    split_working_hours: bool
    preferred: str

    def configure(self):
        self.add_argument("from_airport",
                          type=str,
                          help="List of starting airports, as a comma separated list")
        self.add_argument("to_airport",
                          type=str,
                          help="List of destination airports, as a comma separated list")
        self.add_argument("start_date",
                          type=lambda d: datetime.datetime.strptime(d, "%Y-%m-%d"),
                          help="Start date of the range in YYYY-MM-DD format")
        self.add_argument("end_date",
                          type=lambda d: datetime.datetime.strptime(d, "%Y-%m-%d"),
                          help="End date of the range in YYYY-MM-DD format")
        self.add_argument("--split-working-hours",
                          action='store_true',
                          help="Split output by flights outside/inside working hours")
        self.add_argument("--preferred",
                          type=str,
                          default=os.environ.get("PREFERRED"),
                          help="Preferred airport to highlight in results")

def main() -> None:
    '''Main'''
    load_dotenv()
    parser = ArgumentParser(description="Fetch and display flight data from Google Flights.")
    args = parser.parse_args()

    logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(module)s %(funcName)s - %(message)s",
            level=logging.WARN,
        )

    from_airports = sanitize_airport_list(args.from_airport)
    to_airports = sanitize_airport_list(args.to_airport)

    flights, rejected_flights = get_flights(args.start_date,
                                            args.end_date,
                                            from_airports,
                                            to_airports,
                                            split_working_hours=args.split_working_hours,
                                            preferred=args.preferred)

    if args.split_working_hours:
        print("Inside working hours\n")

    print(tabulate.tabulate(flights,
                            headers=["Flight", "Route", "Departure", "Arrival", "Price"],
                            tablefmt="github"))

    if len(rejected_flights) > 0:
        print("\nDuring working hours\n")
        print(tabulate.tabulate(rejected_flights,
                                headers=["Flight", "Route", "Departure", "Arrival", "Price"],
                                tablefmt="github"))

if __name__ == "__main__":
    main()
