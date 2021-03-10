FROM python:3.8

RUN pip install django gunicorn psycopg2 requests beautifulsoup4

COPY ./ /lol_winrate_game/

WORKDIR /lol_winrate_game/

CMD gunicorn --bind=0.0.0.0:8080 lol_winrate_game.wsgi