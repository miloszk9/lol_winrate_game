from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from .models import Champ_winrate, Game_log
from random import choice
from datetime import datetime
import logging

@cache_page(60 * (59 - datetime.now().minute))
def home(request):
    data = {
        'update_date': Champ_winrate.objects.first().date_update.strftime("%H:%M, %B %d")
    }
    return render(request, 'main/home.html', data)

def game(request):
    #src = int(request.GET.get('src', 1)) # Default option set to '1'
    src = 1 # Currently only 1 source is avaiable 
    logger = logging.getLogger(__name__) # Enable loggin in docker

    # Save session key 
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # Getting all champions from the database - if not cached
    if cache.get(str(src)) is not None:
        logger.info("Got cache")
        all_champion = cache.get(str(src))
    else:
        try:
            logger.info("No cache")
            all_champion = Champ_winrate.objects.filter(source=str(src)).all()
            current_min = datetime.now().minute
            if current_min < 59:
                # Expire cache 1 minute before database update
                cache.set(str(src), all_champion, 60 * (59 - current_min))
        except:
            pass

    '''
    Ajax are sent if its second or later turn (any apart from the first one)
    '''
    if request.is_ajax() and request.method == 'GET':
        src = request.GET.get('src', 1)
        
        # Getting data from AJAX
        value = request.GET.get('button_value', None)
        src = request.GET.get('src', 1)
        champ1 = [request.GET.get('champ1_name', 0), request.GET.get('champ1_role', 0)]
        champ2 = [request.GET.get('champ2_name', 0), request.GET.get('champ2_role', 0)]
        
        # Getting champs from database 
        champ1_db = all_champion.filter(name=str(champ1[0]), \
                                        role=str(champ1[1])).first()
        champ2_db = all_champion.filter(name=str(champ2[0]), \
                                        role=str(champ2[1])).first()
        
        if champ1_db is None or champ2_db is None:
            # When data in db is not the same with data passed by user. 
            # Data could be inspected and modified by user.
            game = Game_log.objects.filter(session_key_db = session_key, is_finished = False).all().delete()
            try:
                cache.delete(str(src)) # Delete cache if exists
            except:
                pass

            return JsonResponse({'finish': "Error"}, status = 400)

        # Validate user's data - could be changed through page inspect
        game = Game_log.objects.filter(session_key_db = session_key, source = src, champ1 = champ1_db.id,\
                                       champ2 = champ2_db.id, is_finished = False).first()

        if game is None:
            # When data in db is not the same with data passed by user. 
            # Data could be inspected and modified by user.
            game = Game_log.objects.filter(session_key_db = session_key, is_finished = False).all().delete()
            try:
                cache.delete(str(src)) # Delete cache if exists
            except:
                pass

            return JsonResponse({'finish': "Error"}, status = 400)

        # Check if the answer is correct
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
            random_champ = choice(all_champion)

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
            return JsonResponse({'score': int(game.score), 'champ2_win': champ2_db.win_rate, 'finish': True}, status = 200)

    '''
    Checks if the player has any unfinished games
    '''
    game = Game_log.objects.filter(session_key_db = session_key, is_finished = False, source = str(src)).last()
    if game is not None:
        '''
        Resuming unfinished game
        '''
        champs = [all_champion.filter(id=game.champ1).first(), \
                  all_champion.filter(id=game.champ2).first()]
        score = game.score

    else:
        '''
        Start of the game (the first turn)
        '''
        # Getting 2 random champions
        try:
            champs = [choice(all_champion), choice(all_champion)]
        except:
            logger.info("Redirect to home")
            redirect('home')

        game = Game_log(session_key_db = session_key, score = 0, source = src, \
                        champ1 = champs[0].id, champ2 = champs[1].id, is_finished = False)
        game.save()

        score = 0

    # User's best score
    game = Game_log.objects.filter(session_key_db = session_key, is_finished = True).order_by('-score').first()
    if game is not None:
        best_score = game.score
    else:
        best_score = 0

    data = {
        'source': src,
        'champion': champs,
        'score': score,
        'best_score' : best_score
    }

    return render(request, 'main/game.html', data)
