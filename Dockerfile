FROM python:3.8.5

WORKDIR /var/html/
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade pip
COPY . .
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000