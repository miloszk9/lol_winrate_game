from django.db import models

class Champ_winrate(models.Model):
    name = models.CharField(max_length = 100)
    role = models.CharField(max_length = 100)
    win_rate = models.FloatField()
    source = models.IntegerField()
    date_update = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.name

class Game_log(models.Model):
    ip = models.CharField(max_length=15)
    score = models.IntegerField()
    source = models.IntegerField()
    champ1 = models.IntegerField()
    champ2 = models.IntegerField()
    is_finished = models.BooleanField()
    date = models.DateTimeField(auto_now = True)
