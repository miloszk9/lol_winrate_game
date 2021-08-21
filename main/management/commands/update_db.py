from django.core.management.base import BaseCommand
from django.core.cache import cache

import requests
import os.path
from bs4 import BeautifulSoup as soup
from datetime import datetime
from main.models import Champ_winrate, Game_log

from main.download_img import download_img

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        src = 1 # currently only one source
        '''
        Update any unfinished games older than 1 day to finished (prevent bugs which can exist with new data from database)
        '''
        games = Game_log.objects.filter(is_finished = False, source = src).all()
        for game in games:
            if (datetime.now() - game.date.replace(tzinfo=None)).days > 0:
                game.is_finished = True
                game.save()

        '''
        Clearing the cache if exists
        '''
        try:
            cache.delete(str(src))
        except:
            pass

        ''' 
        Update winrates of the champions in database
        '''
        url = 'https://www.metasrc.com/5v5/stats'
        webpage = requests.get(url)
        webpage_preety = soup(webpage.content, 'html.parser')
        champ_list = webpage_preety.find_all("tr", {"class": "_sbzxul"})

        if len(champ_list) > 100:
            # Delete data from db
            Champ_winrate.objects.filter(source = src).all().delete()

            for champ in champ_list:
                try:
                    data = champ.find_all("td")
                    champ_name = data[0].find_next("span").get_text()
                    champ_lane = data[1].find_next("div").get_text().lower()
                    champ_win = data[5].get_text()[:-1]
                    champ = Champ_winrate(name= champ_name, role = champ_lane, win_rate = champ_win, source = src)
                    champ.save()
                except:
                    pass

        '''
        Select champion names from database and save to file
        '''
        champs_db = Champ_winrate.objects.all()
        champs = [champ.name.replace(" ", "_") for champ in champs_db]
        champs = set(champs) # make 'champs' contain only unique values

        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'champ_list.txt'), 'w') as file:
            for champ in champs:
                file.write(champ+'\n')

        '''
        Check and download missing champion's images
        '''
        download_img()
