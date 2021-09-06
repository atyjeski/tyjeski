from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from hanabi.models import *
from hanabi.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import random
from django.utils import timezone


def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'hanabi/login.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'hanabi/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('hanabi:home'))

def logout_action(request):
    logout(request)
    return redirect(reverse('hanabi:login'))

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'hanabi/register.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'hanabi/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()
    #create profile
    new_player = Player.objects.create(user=new_user)
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('hanabi:home'))

@login_required
def home_action(request):
    context = {}
    return render(request, 'hanabi/home.html', context)

@login_required
def create_room(request):
    context = {}
    if request.method == 'GET':
        context['form'] = RoomForm()
        return render(request, 'hanabi/create_room.html', context)
    form = RoomForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'hanabi/create_room.html', context)
    new_room = Room()
    new_room.size = form.cleaned_data['size']
    #white = 1, yellow = 2, green = 3, blue = 4, red = 5
    #first index is color, 2nd index is number
    data = {
        "deck" :   [[1, 1], [1, 1], [1, 1], [1, 2], [1, 2], [1, 3], [1, 3], [1, 4], [1, 4], [1, 5],
                    [2, 1], [2, 1], [2, 1], [2, 2], [2, 2], [2, 3], [2, 3], [2, 4], [2, 4], [2, 5],
                    [3, 1], [3, 1], [3, 1], [3, 2], [3, 2], [3, 3], [3, 3], [3, 4], [3, 4], [3, 5],
                    [4, 1], [4, 1], [4, 1], [4, 2], [4, 2], [4, 3], [4, 3], [4, 4], [4, 4], [4, 5],
                    [5, 1], [5, 1], [5, 1], [5, 2], [5, 2], [5, 3], [5, 3], [5, 4], [5, 4], [5, 5]],

        "hands" : {},
        "discard" : [],
        "tabletop" : [0, 0, 0, 0, 0],
        "log": [],
        "end_game": []
    }

    random.shuffle(data["deck"])
    hand_size = 5
    if new_room.size > 3:
        hand_size = 4

    player = Player.objects.get(user=request.user)
    data["hands"][str(player.id)] = []
    for _ in range(hand_size):
        data["hands"][str(player.id)].append(data["deck"].pop())

    new_room.game_data = json.dumps(data)

    new_room.save()
    #The person who made the room is added as one of the players
    new_room.players.add(Player.objects.get(user=request.user))
    room_id = new_room.id
    return redirect(reverse('hanabi:room', args=(room_id,)))

@login_required
def enter_room(request, room_id):
    context = {}
    room = Room.objects.get(id=room_id)
    players = room.players.all()
    context['players'] = players
    context['room'] = room
    player_self = Player.objects.get(user=request.user)
    context['player_self'] = player_self
    context['playing'] = player_self in players

    return render(request, 'hanabi/room.html', context)

@login_required
def play_game(request, room_id):
    room = Room.objects.get(id=room_id)
    player = Player.objects.get(user=request.user)
    
    # Cannot join if the game is full or player is already playing
    if room.players.filter(user=request.user) or room.players.count() >= room.size:
        return redirect(reverse('hanabi:room', args=(room_id,)))
    
    room.players.add(player)
    if room.players.count() >= room.size:
        room.active = True

    #grab a hand of cards
    data = json.loads(room.game_data)

    hand_size = 5
    if room.size > 3:
        hand_size = 4

    data["hands"][str(player.id)] = []
    for _ in range(hand_size):
        data["hands"][str(player.id)].append(data["deck"].pop())

    room.game_data = json.dumps(data)
    room.save()
    #
    return redirect(reverse('hanabi:room', args=(room_id,)))

@login_required
def join_room(request):
    context = {}
    rooms = []
    for room in Room.objects.all():
        rooms.append(room)
    context['rooms'] = rooms
    return render(request, 'hanabi/join_room.html', context)

def get_color_string(color_number):
    if color_number == 1:
        return "white"
    if color_number == 2:
        return "yellow"
    if color_number == 3:
        return "green"
    if color_number == 4:
        return "blue"
    if color_number == 5:
        return "red"
    return ""

@login_required
def discard_card(request, room_id, card_index):
    room = Room.objects.get(id=room_id)
    player = Player.objects.get(user=request.user)
    players = room.players.all()
    #It must be the player's turn to take an action
    if player != players[room.turn] or not room.active:
        return redirect(reverse('hanabi:room', args=(room_id,)))

    data = json.loads(room.game_data)
    hand = data["hands"][str(player.id)]
    card = hand[card_index]

    # Discarding a card grants a hint
    data["discard"].append(card)
    room.increase_hints()
    # Draw a new card to replace the discarded card
    if len(data["deck"]) > 0:
        hand[card_index] = data["deck"].pop()
    else:
        del hand[card_index]

    # Write action to the log
    log_text = player.user.username + " discarded the " + get_color_string(card[0]) + " " + str(card[1])
    data["log"].append(log_text)

    room.next_turn()
    room.game_data = json.dumps(data)
    room.save()

    # Check whether the game is over
    return end_state(request, room_id)

@login_required
def play_card(request, room_id, card_index):
    room = Room.objects.get(id=room_id)
    player = Player.objects.get(user=request.user)
    players = room.players.all()
    #It must be the player's turn to take an action
    if player != players[room.turn] or not room.active:
        return redirect(reverse('hanabi:room', args=(room_id,)))

    data = json.loads(room.game_data)
    hand = data["hands"][str(player.id)]
    card = hand[card_index]

    # If the played card is the next in the sequence, add it to the table.
    # Otherwise a fuse token is used and the card is sent to the discard pile
    if card[1] == data["tabletop"][card[0] - 1] + 1:
        data["tabletop"][card[0] - 1] += 1
        # Completing a color grants a hint token
        if card[1] == 5:
            room.increase_hints()
    else:
        room.use_strike()
        data["discard"].append(card)

    # Draw a card to replace the played card
    if len(data["deck"]) > 0:
        hand[card_index] = data["deck"].pop()
    else:
        del hand[card_index]

    # Write action to the log
    log_text = player.user.username + " played the " + get_color_string(card[0]) + " " + str(card[1])
    data["log"].append(log_text)

    room.next_turn()
    room.game_data = json.dumps(data)
    room.save()

    # Check whether the game is over
    return end_state(request, room_id)

@login_required
def give_hint_color(request, room_id, card_color, player_id):
    #white = 1, yellow = 2, green = 3, blue = 4, red = 5
    total_colors = 0
    indices = []
    room = Room.objects.get(id=room_id)
    self_player = Player.objects.get(user=request.user)
    player = Player.objects.get(id=player_id)
    players = room.players.all()

    #It must be the player's turn to take an action
    if self_player != players[room.turn] or not room.active:
        return redirect(reverse('hanabi:room', args=(room_id,)))

    #cannot give a hint without a token
    if room.hints <= 0:
        return redirect(reverse('hanabi:room', args=(room_id,)))

    data = json.loads(room.game_data)
    hand = data["hands"][str(player_id)]
    hint_color = card_color
    #send player, indices of card, and message
    for i in range(len(hand)):
        if hand[i][0] == hint_color:
            indices.append(i+1)

    player_username = player.user.username

    color = get_color_string(hint_color)
    message = ""
    if len(indices) == 1:
        message = "Card " + str(indices[0]) + " is " + color + " for " + player_username
    else:
        mini = ""
        for i in range(len(indices) - 1):
            mini += str(indices[i]) + ", "
        mini += str(indices[-1]) + " "
        message = "Cards " + mini + "are " + color + " for " + player_username

    # Display the hint in the log
    data["log"].append(message)

    room.decrease_hints()
    room.next_turn()
    room.game_data = json.dumps(data)
    room.save()
    return redirect(reverse('hanabi:room', args=(room_id,)))

@login_required
def give_hint_number(request, room_id, card_number, player_id):
    total_numbers = 0
    indices = []
    room = Room.objects.get(id=room_id)
    self_player = Player.objects.get(user=request.user)
    player = Player.objects.get(id=player_id)
    players = room.players.all()

    #It must be the player's turn to take an action
    if self_player != players[room.turn] or not room.active:
        return redirect(reverse('hanabi:room', args=(room_id,)))

    #cannot give a hint without a token
    if room.hints <= 0:
        return redirect(reverse('hanabi:room', args=(room_id,)))

    data = json.loads(room.game_data)
    hand = data["hands"][str(player_id)]
    hint_number = card_number
    #send player, indices of card, and message
    for i in range(len(hand)):
        if hand[i][1] == hint_number:
            indices.append(i+1)
    
    player_username = player.user.username
    message = ""
    if len(indices) == 1:
        message = "Card " + str(indices[0]) + " is " + str(hint_number) + " for " + player_username
    else:
        mini = ""
        for i in range(len(indices) - 1):
            mini += str(indices[i]) + ", "
        mini += str(indices[-1]) + " "
        message = "Cards " + mini + "are " + str(hint_number) + " for " + player_username
    data["log"].append(message)

    room.decrease_hints()
    room.next_turn()
    room.game_data = json.dumps(data)
    room.save()
    return redirect(reverse('hanabi:room', args=(room_id,)))

@login_required
def end_state(request, room_id):
    room = Room.objects.get(id=room_id)
    data = json.loads(room.game_data)
    hands = data['hands']
    deck = data["deck"]
    tabletop = data['tabletop']

    # Game is lost if all the fuse tokens are used
    if room.strikes <= 0:
        data["end_game"] = "Game over! Score: 0"

    # End game when no more cards can be played
    def tabletop_complete():
        for i in range(len(tabletop)):
            if tabletop[i] != 5:
                next_card = [i + 1, tabletop[i] + 1]
                if next_card in deck:
                    return False
                for hand in hands:
                    if next_card in hands[hand]:
                        return False
        return True

    if tabletop_complete() or room.final_turn == room.turn:
        score = 0
        for i in tabletop:
            score += i
        data["end_game"] = "Game over! Score: " + str(score)

    # When deck is empty, do one more round then end the game
    if room.final_turn == -1 and len(data['deck']) == 0:
        room.final_turn = room.turn

    if data["end_game"]:
        room.active = False

    room.game_data = json.dumps(data)
    room.save()

    return redirect(reverse('hanabi:room', args=(room_id,)))

@login_required
def get_game_info(request, room_id):
    room = Room.objects.get(id=room_id)
    players = room.players.all()
    player_self = Player.objects.get(user=request.user)
    data = json.loads(room.game_data)

    response_object = {
        "discard" : data["discard"],
        "tabletop" : data["tabletop"],
        "hints" : room.hints,
        "strikes" : room.strikes,
        "deck_size" : len(data["deck"]),
        "hands" : [],
        "log" : (data["log"])[-room.size:][::-1],
        "my_turn" : player_self == players[room.turn],
        "room_message" : "",
        "active" : room.active
    }
    for player in players:
        hand_object = {
            "username" : player.user.username,
            "player_id" : player.id,
            "cards" : data["hands"][str(player.id)],
            "self" : False
        }
        if player == player_self:
            hand_object["self"] = True
            if room.active or len(players) < room.size:
                hand_object["cards"] = len(data["hands"][str(player.id)])


        response_object["hands"].append(hand_object)

    if room.active:
        if player_self == players[room.turn]:
            response_object["room_message"] = "It's your turn!"
        else:
            response_object["room_message"] = "Waiting for " + players[room.turn].user.username + " to finish their turn..."
    elif data["end_game"]:
            response_object["room_message"] = '<b style="font-size:30px">' + data["end_game"] + '</b>'
    else:
        response_object["room_message"] = "Waiting for players..."

    response_json = json.dumps(response_object)
    response = HttpResponse(response_json, content_type='application/json')
    return response


def interface_overhaul(request):
    return render(request, 'hanabi/interface-overhaul.html')