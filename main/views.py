from django.shortcuts import render, redirect
from django.http import JsonResponse
from requests.api import get
from .models import Champ_winrate, Game_log
from random import choice
import datetime

from .update_db import update_db
from .get_client_ip import get_client_ip

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
        
        # Make as finished unfinished games older than 1 day (prevent bugs which can exist with new data from database)
        now_date = datetime.datetime.now()
        games = Game_log.objects.filter(is_finished = False).all()
        for game in games:
            if (now_date - game.date.replace(tzinfo=None)).days > 0:
                game.is_finished = True
                game.save()

        # Update database if data older than 1 day
        all_champion = Champ_winrate.objects.filter(source=str(src)).all()
        if (now_date - all_champion[0].date_update.replace(tzinfo=None)).days > 0:
            update_db(src)

        # Getting 2 random champions
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
