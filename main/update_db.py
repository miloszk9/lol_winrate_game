import requests
import os.path
from bs4 import BeautifulSoup as soup
from .models import Champ_winrate


def update_db(data_source):
    ''' 
    Update winrates of the champions in database

    data_source = 1 - metasrc.com
    data_source = 2 - champion.gg
    '''
    if data_source == 1:
        # Delete data from db
        Champ_winrate.objects.filter(source=data_source).all().delete()

        url = 'https://www.metasrc.com/5v5/stats'
        webpage = requests.get(url)
        webpage_preety = soup(webpage.content, 'html.parser')
        champ_list = webpage_preety.find_all("tr", {"class": "_sbzxul"})

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

    if data_source == 2:
        # Delete data from db
        Champ_winrate.objects.filter(source=data_source).all().delete()

        url = 'https://champion.gg/tierlist'
        webpage = requests.get(url)
        webpage_preety = soup(webpage.content, 'html.parser')

        champ_list = webpage_preety.find_all("div", {"class": "fYmnzJ"})

        for champ in champ_list:
            try:
                data = champ.find_all("div")
                champ_name = data[3].get_text()
                champ_lane = data[0].get_text()[5:]
                champ_win = data[2].find_next("span").get_text()[:-1]
                
                champ = Champ_winrate(name= champ_name, role = champ_lane, win_rate = champ_win, source = 2)
                champ.save()
            except:
                redirect('home')

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
