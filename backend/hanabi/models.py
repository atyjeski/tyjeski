from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Player(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, default=None, on_delete=models.PROTECT, related_name="player")

    def __str__(self):
        return self.user.get_username()

class Room(models.Model):
    id = models.AutoField(primary_key=True)
    choices = [(2, 2), (3, 3), (4, 4), (5, 5)]
    size = models.IntegerField(choices=choices)
    players = models.ManyToManyField(Player)
    hints = models.IntegerField(default=8)
    strikes = models.IntegerField(default=3)
    game_data = models.JSONField()
    turn = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    final_turn = models.IntegerField(default=-1)

    def __str__(self):
        return "Room " + str(self.id)

    def increase_hints(self):
        if self.hints < 8:
            self.hints = self.hints + 1
        self.save()
    
    def decrease_hints(self):
        if self.hints > 0:
            self.hints = self.hints - 1
        self.save()

    def use_strike(self):
        self.strikes = self.strikes - 1
        self.save()

    def next_turn(self):
        self.turn = self.turn + 1
        if(self.turn >= self.size):
            self.turn = 0
        self.save()