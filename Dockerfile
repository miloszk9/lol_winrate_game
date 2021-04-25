FROM python:3.8

RUN pip install django gunicorn psycopg2 whitenoise requests beautifulsoup4 python-memcached

COPY ./ /lol_winrate_game/

WORKDIR /lol_winrate_game/

RUN python manage.py collectstatic --noinput

CMD gunicorn lol_winrate_game.wsgi:application --bind 0.0.0.0:80
