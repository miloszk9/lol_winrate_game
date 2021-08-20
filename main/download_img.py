import requests
import os.path
from bs4 import BeautifulSoup as soup

'''
Function download_img()

Usage:
Function downloads images of champs and saves them in ./static/img folder
Checks every champion in database and download image if not already in ./static/img folder
'''
def download_img():
    dirname = os.path.dirname(__file__)
    
    # Read champs list from file
    with open(os.path.join(dirname, 'champ_list.txt'), 'r') as file:
        champs = [line for line in file.read().splitlines() if len(line)>1]

    # Download images
    for champ in champs:
        try: # Can be exceptions if there is new champion
            if not os.path.isfile(os.path.join(dirname, './static/img/'+champ+'.jpg')):
                url = 'https://lol.fandom.com/wiki/{}/Gallery/Loading_Screens'.format(champ)
                webpage = requests.get(url)
                webpage_soup = soup(webpage.content, 'html.parser')
                
                img_url = webpage_soup.find("a", {"class": "image"}).find_next("img")['src'].split('/revision')[0]
                img = requests.get(img_url, allow_redirects=True)
                open(os.path.join(dirname, './static/img/'+champ+'.jpg'), 'wb').write(img.content)
        except:
            print(champ)

if __name__ == '__main__':
    download_img()
