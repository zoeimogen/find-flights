#!/usr/bin/env python
'''Flight finder web server'''

import datetime
import os
import tabulate
from dotenv import load_dotenv

from flask import Flask, request, Response, render_template, send_from_directory
from get_from_google import get_flights, sanitize_airport_list

app = Flask(__name__)

# Constants
HEADERS = ["Flight", "Route", "Departure", "Arrival", "Price"]

load_dotenv()
PREFERRED = os.environ.get("PREFERRED")
DEFAULT_FROM = os.environ.get("DEFAULT_FROM", "LON")
DEFAULT_TO = os.environ.get("DEFAULT_TO", "ORY CDG")

@app.after_request
def add_headers(response) -> Response:
    '''Standard security headers'''
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
    response.headers['Content-Security-Policy'] = "default-src 'self';"
    response.headers['Strict-Transport-Security'] = "max-age=31536000; includeSubDomains"
    return response

@app.route('/', methods=['GET', 'POST'])
def index() -> str:
    '''Main entry point'''
    form_data = {
        'from_airport': request.form.get('from_airport', DEFAULT_FROM),
        'to_airport': request.form.get('to_airport', DEFAULT_TO),
        'split_working_hours': request.form.get('split_working_hours', False)
    }

    try:
        start_date = request.form.get('start_date', datetime.datetime.now().strftime('%Y-%m-%d'))
        end_date = request.form.get('end_date', datetime.datetime.now().strftime('%Y-%m-%d'))
        start_date_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return render_template('index.html', form_data=form_data, error="Bad date format")

    form_data['start_date'] = start_date
    form_data['end_date'] = end_date

    if (end_date_dt - start_date_dt).days > 14:
        return render_template('index.html', error="Won't scan for more than two weeks at a time")
    if (end_date_dt - start_date_dt).days < 0:
        return render_template('index.html', error="Start date is after end date")

    if request.method == 'POST':
        try:
            from_airport = sanitize_airport_list(str(form_data['from_airport']))
            to_airport = sanitize_airport_list(str(form_data['to_airport']))
            split_working_hours: bool = bool(form_data['split_working_hours'])

            flights, rejected_flights = get_flights(start_date_dt,
                                                    end_date_dt,
                                                    from_airport,
                                                    to_airport,
                                                    split_working_hours=split_working_hours,
                                                    html=True,
                                                    preferred=PREFERRED)

            if not flights and not rejected_flights:
                return render_template('index.html', error="No flights found", form_data=form_data)

            flight_table = tabulate.tabulate(flights, headers=HEADERS, tablefmt="unsafehtml")
            if split_working_hours:
                rejected_flight_table = tabulate.tabulate(rejected_flights,
                                                          headers=HEADERS,
                                                          tablefmt="unsafehtml")
                return render_template('index.html',
                                       form_data=form_data,
                                       flights=flight_table,
                                       rejected_flights=rejected_flight_table)
            return render_template('index.html', form_data=form_data, flights=flight_table)
        except ValueError as e:
            return render_template('index.html', error=str(e), form_data=form_data)
    return render_template('index.html', form_data=form_data)

@app.route('/static/<path:filename>')
def serve_static(filename) -> Response:
    '''Serve static content'''
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
