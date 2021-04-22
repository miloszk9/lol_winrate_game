# Lol winrate game

A similar game to “Higher lower game” but you have to decide which of two random champions from the League of Legends game has a higher win rate.

## Prerequirements (no need to install anything else)
* Docker
* Docker-compose

## Installation
```sh
$ docker-compose up -d --build
$ docker exec lol_winrate_game_lol_winrate_django_1 python manage.py migrate
```

### Used frameworks / tools
* Django
* PostreSQL
* psycopg2 
* Bootstrap
* Docker

### Game screenshots
![screen1](https://github.com/miloszk9/lol_winrate_game/blob/main/example_images/lol_1.png?raw=true)
![screen2](https://github.com/miloszk9/lol_winrate_game/blob/main/example_images/lol_2.png?raw=true)
![screen3](https://github.com/miloszk9/lol_winrate_game/blob/main/example_images/lol_3.png?raw=true)

### Sources
* background image: www.leagueoflegends.fandom.com
* champion's images: www.lol.gamepedia.com
* winrate source 1: www.metasrc.com
* winrate source 2: www.champion.gg

Made by: Miłosz Kaszuba