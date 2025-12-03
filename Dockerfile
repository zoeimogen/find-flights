FROM python:3.13-alpine
WORKDIR /opt/flight-server
COPY flight_server.py get_from_google.py requirements.txt /opt/flight-server/
COPY templates /opt/flight-server/templates
COPY static /opt/flight-server/static
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt
RUN pip install gunicorn
RUN adduser -D flight_server
USER flight_server
EXPOSE 5001
CMD ["gunicorn", "-b", "0.0.0.0:5001", "flight_server:app"]