FROM python:3.8

RUN apt-get update

RUN apt-get install cron -y

RUN pip install django gunicorn psycopg2 whitenoise requests beautifulsoup4 python-memcached

COPY ./ /lol_winrate_game/

WORKDIR /lol_winrate_game/

RUN echo "0 * * * * /usr/local/bin/python /lol_winrate_game/manage.py update_db\n" > my_cron

RUN crontab my_cron

RUN python manage.py collectstatic --noinput

CMD cron && gunicorn lol_winrate_game.wsgi:application --bind 0.0.0.0:80
