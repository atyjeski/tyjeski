from django.contrib import admin
from django.contrib.auth.models import User
from .models import Player, Room

# Register your models here.
admin.site.register(Player)
admin.site.register(Room)
