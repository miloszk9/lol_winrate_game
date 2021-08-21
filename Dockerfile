FROM python:3.8

RUN apt-get update

RUN apt-get install cron vim -y

RUN pip install django gunicorn psycopg2 whitenoise django-crontab requests beautifulsoup4 python-memcached

COPY ./ /lol_winrate_game/

WORKDIR /lol_winrate_game/

RUN echo "* * * * * /usr/local/bin/python /lol_winrate_game/manage.py update_db\n" > my_cron

# Problem: it works only after running '$ cron' manually after
RUN crontab my_cron

#RUN touch /var/log/cron.log && cron
#RUN /etc/init.d/cron start

RUN python manage.py collectstatic --noinput

CMD cron && gunicorn lol_winrate_game.wsgi:application --bind 0.0.0.0:80
