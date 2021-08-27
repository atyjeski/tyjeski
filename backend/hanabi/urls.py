from django.contrib import admin
from django.urls import path
from hanabi import views

app_name = 'hanabi'
urlpatterns = [
    path('', views.home_action, name='home'),
    path('login', views.login_action, name = 'login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    path('create_room', views.create_room, name='create_room'),
    path('room/<int:room_id>', views.enter_room, name='room'),
    path('join_room', views.join_room, name='join_room'),
    path('play_game/<int:room_id>', views.play_game, name='play_game'),
    path('end_state/<int:room_id>', views.end_state, name='end_state'),
    path('discard_card/<int:room_id>/<int:card_index>', views.discard_card, name='discard_card'),
    path('play_card/<int:room_id>/<int:card_index>', views.play_card, name='play_card'),
    path('give_hint_color/<int:room_id>/<int:card_color>/<int:player_id>', views.give_hint_color, name='give_hint_color'),
    path('give_hint_number/<int:room_id>/<int:card_number>/<int:player_id>', views.give_hint_number, name='give_hint_number'),
    path('get-game-info/<int:room_id>', views.get_game_info),
]
