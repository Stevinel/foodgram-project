FROM python:3.8.5

COPY . /code
WORKDIR /code
COPY requirements.txt /code
RUN pip install -r /code/requirements.txt
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
