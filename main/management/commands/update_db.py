from django.core.management.base import BaseCommand

import requests
import os.path
from bs4 import BeautifulSoup as soup
from main.models import Champ_winrate

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        ''' 
        Update winrates of the champions in database
        '''
        url = 'https://www.metasrc.com/5v5/stats'
        webpage = requests.get(url)
        webpage_preety = soup(webpage.content, 'html.parser')
        champ_list = webpage_preety.find_all("tr", {"class": "_sbzxul"})

        if len(champ_list) > 100:
            # Delete data from db
            Champ_winrate.objects.filter(source = 1).all().delete()

            for champ in champ_list:
                try:
                    data = champ.find_all("td")
                    champ_name = data[0].find_next("span").get_text()
                    champ_lane = data[1].find_next("div").get_text().lower()
                    champ_win = data[5].get_text()[:-1]
                    champ = Champ_winrate(name= champ_name, role = champ_lane, win_rate = champ_win, source = 1)
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
