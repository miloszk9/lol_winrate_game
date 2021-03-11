import requests
from bs4 import BeautifulSoup as soup
from .models import Champ_winrate

'''
Function save_champ_name()

Usage:
Select champion names from database and save to file 
'''
def save_champ_name():
    champs_db = Champ_winrate.objects.all()
    champs = [champ.name.replace(" ", "_") for champ in champs_db]
    champs = set(champs) # make 'champs' contain only unique values

    with open('champ_list.txt', 'a') as file:
        for champ in champs:
            file.write(champ+'\n')

'''
Function download_img()

Usage:
Function downloads images of champs and saves them in ./static/img folder
Checks every champion in database and download image if not already in ./static/img folder
'''
def download_img():
    url = 'https://lol.gamepedia.com/File:Skin_Loading_Screen_Classic_'

    # Read champs list from file
    with open('champ_list.txt', 'r') as file:
        champs = [line for line in file.read().splitlines() if len(line)>1]

    # Download images
    for champ in champs:
        try: # Can be exceptions if there is new champion
            webpage = requests.get(url+str(champ)+'.jpg')
            webpage_soup = soup(webpage.content, 'html.parser')
            
            img_url = webpage_soup.find("div", {"id": "file"}).find_next("a").find_next("img")['src']
            img = requests.get(img_url, allow_redirects=True)
            open('./static/img/'+champ+'.jpg', 'wb').write(img.content)
        except:
            print(champ)

download_img()
