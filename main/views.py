from django.shortcuts import render, redirect
from django.http import JsonResponse
from requests.api import get
from .models import Champ_winrate, Game_log
from random import choice

from .get_client_ip import get_client_ip

# Imports for update() function
import requests
from bs4 import BeautifulSoup as soup

def home(request):
    data = {}
    return render(request, 'main/home.html', data)

def game(request):
    src = int(request.GET.get('src', 1)) # Default option set to '1'

    '''
    Ajax when its second or later turns (not the first one)
    '''
    if request.is_ajax() and request.method == 'GET':
        src = request.GET.get('src', 1)
        
        # Getting data from AJAX
        value = request.GET.get('button_value', None)
        src = request.GET.get('src', 1)
        champ1 = [request.GET.get('champ1_name', 0), request.GET.get('champ1_role', 0)]
        champ2 = [request.GET.get('champ2_name', 0), request.GET.get('champ2_role', 0)]
        # Getting champs from database 
        champ1_db = Champ_winrate.objects.filter(source=int(src), name=str(champ1[0]), \
                                                 role=str(champ1[1])).first()
        champ2_db = Champ_winrate.objects.filter(source=int(src), name=str(champ2[0]), \
                                                 role=str(champ2[1])).first()
        
        if champ1_db is None or champ2_db is None:
            # When data in db is not the same with data passed by user. 
            # Data could be inspected and modified by user.
            game = Game_log.objects.filter(ip = get_client_ip(request), is_finished = False).all().delete()

            return JsonResponse({'finish': "Error"}, status = 400)

        # Validate user's data - could be changed through page inspect
        game = Game_log.objects.filter(ip = get_client_ip(request), source = src, champ1 = champ1_db.id,\
                                       champ2 = champ2_db.id, is_finished = False).first()

        if game is None:
            # When data in db is not the same with data passed by user. 
            # Data could be inspected and modified by user.
            game = Game_log.objects.filter(ip = get_client_ip(request), is_finished = False).all().delete()

            return JsonResponse({'finish': "Error"}, status = 400)

        # Check if answer is correct
        if float(champ1_db.win_rate) < float(champ2_db.win_rate):
            if str(value) == 'higher':
                correct = True
            else:
                correct = False
        elif float(champ1_db.win_rate) > float(champ2_db.win_rate):
            if str(value) == 'lower':
                correct = True
            else:
                correct = False
        else: # If winrates are the same
            correct = True
        
        if correct == True:
            champion = Champ_winrate.objects.filter(source=str(src)).all()
            random_champ = choice(champion)

            # Increase score update champs and save in database
            game.score += 1
            game.champ1 = game.champ2
            game.champ2 = random_champ.id
            game.save()

            return JsonResponse({'score': int(game.score), \
                                 'new_champ': [random_champ.name, random_champ.role], \
                                 'champ1_win': champ2_db.win_rate, \
                                 'finish': False}, status = 200)
        else:
            game.is_finished = True
            game.save()
            return JsonResponse({'score': int(game.score), 'finish': True}, status = 200)

    '''
    Chacks if the player has any unfinished games
    '''
    game = Game_log.objects.filter(ip = get_client_ip(request), is_finished = False, source = str(src)).first()
    if game is not None:
        '''
        Resuming unfinished game
        '''
        champs = [Champ_winrate.objects.filter(id=game.champ1).first(), \
                  Champ_winrate.objects.filter(id=game.champ2).first()]
        score = game.score

    else:
        '''
        Start of the game (the first turn)
        '''
        
        # Getting 2 random champions
        all_champion = Champ_winrate.objects.filter(source=str(src)).all()
        champs = [choice(all_champion), choice(all_champion)]

        game = Game_log(ip = get_client_ip(request), score = 0, source = src, \
                        champ1 = champs[0].id, champ2 = champs[1].id, is_finished = False)
        game.save()

        score = 0

    data = {
        'source': src,
        'champion': champs,
        'score': score,
    }

    return render(request, 'main/game.html', data)


def update(reqeust):
    '''
    Update winrates of the champions in database

    data_source = 1 - metasrc.com
    data_source = 2 - champion.gg

    '''
    data_source = 1
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

    data_source = 2
    if data_source == 2:
        # Delete data from db
        Champ_winrate.objects.filter(source=data_source).all().delete()

        url = 'https://champion.gg/statistics/overview?queue=ranked-solo-duo&rank=platinum_plus&region=world'
        webpage = requests.get(url)
        webpage_preety = soup(webpage.content, 'html.parser')
        champ_list = webpage_preety.find_all("div", {"class": "champion-row"})

        for champ in champ_list:
            try:
                data = champ.find_all("div")
                champ_name = data[2].find_next("span").get_text()
                champ_lane = data[1].find_next("svg").find_next("title").get_text()[5:]
                champ_win = data[5].get_text()[:-1]
                
                champ = Champ_winrate(name= champ_name, role = champ_lane, win_rate = champ_win, source = 2)
                champ.save()
            except:
                pass

    return redirect('home')
