"use strict"

// Refreshes the entire page
function refresh(){
    window.location.reload()
}

function getGameInfo(){
    let request = new XMLHttpRequest()
    request.onreadystatechange = function() {
        if (request.readyState != 4) return
        updatePage(request)
    }

    let url = "/hanabi/get-game-info/" + room_id
    request.open("GET", url, true)
    request.send()
}

function updatePage(request) {
    if (request.status != 200) {
        displayError("Received status code = " + request.status)
        return
    }
    let response = JSON.parse(request.responseText)
    updateGameInfo(response)
}

function getColorString(color_number){
    switch(color_number){
        case 1:
            return "white"
        case 2:
            return "yellow"
        case 3:
            return "green"
        case 4:
            return "blue"
        case 5:
            return "red"
        default:
            return "back"
    }
}

function updateGameInfo(items) {
    // DISCARD PILE
    // Removes the old discard items
    let discard_list = document.getElementById("id_discard")
    while (discard_list.hasChildNodes()) {
        discard_list.removeChild(discard_list.firstChild)
    }

    let discard = items["discard"]
    // Adds each new discard item to the list
    for (let i = 0; i < discard.length; i++) {
        let card = discard[i]
        let color = getColorString(card[0])
        
        let element = document.createElement("li")
        element.innerHTML = '<div class="card-' + color + '">' + card[1].toString() + '</div>'

        // Adds the discard item to the HTML list
        discard_list.appendChild(element)
    }

    // TABLETOP
    // Removes the old tabletop items
    let tabletop_list = document.getElementById("id_tabletop")
    while (tabletop_list.hasChildNodes()) {
        tabletop_list.removeChild(tabletop_list.firstChild)
    }

    let tabletop = items["tabletop"]
    // Adds each new tabletop item to the list
    for (let i = 0; i < tabletop.length; i++) {
        let number = tabletop[i]
        let color = getColorString(i+1)
        
        let element = document.createElement("li")
        element.innerHTML = '<div class="card-' + color + '">' + number.toString() + '</div>'

        // Adds the tabletop item to the HTML list
        tabletop_list.appendChild(element)
    }

    // LOG
    // Removes the old log items
    let log_list = document.getElementById("id_log")
    while (log_list.hasChildNodes()) {
        log_list.removeChild(log_list.firstChild)
    }

    let log = items["log"]
    // Adds each new log item to the list
    for (let i = 0; i < log.length; i++) {

        let curr_log = log[i]
        
        let element = document.createElement("li")
        element.innerHTML = curr_log

        // Adds the log item to the HTML list
        log_list.appendChild(element)
    }

    // HINTS
    let hints_element = document.getElementById("id_hints")
    hints_element.innerHTML = items["hints"]

    // STRIKES
    let strikes_element = document.getElementById("id_strikes")
    strikes_element.innerHTML = items["strikes"]

    // DECK SIZE
    let deck_size_element = document.getElementById("id_deck_size")
    deck_size_element.innerHTML = items["deck_size"]

    // HANDS
    // Removes the old hands
    let hands_list = document.getElementById("id_hands")
    while (hands_list.hasChildNodes()) {
        hands_list.removeChild(hands_list.firstChild)
    }
    let hands = items["hands"]
    // Adds each new hand
    for (let hand_index = 0; hand_index < hands.length; hand_index++) {
        let hand = hands[hand_index]
        let hand_element = document.createElement("li")
        let inner_html = hand["username"] + '<div class="hand">'
        if (hand["self"] && typeof(hand["cards"]) == "number") {
            for(let i = 0; i < hand["cards"]; i++) {
                if(items['my_turn'] && items["active"]){
                    inner_html +=
                        '<div class="card-back" style="cursor: pointer;" onclick="Dropdown(' + i.toString() + ')">' +
                        '<div id="self-card-dropdown-' + i.toString() + '" class="dropdown-content">' +
                        '<a href="../play_card/' + room_id.toString() + "/" + i.toString() + '">Play</a>' +
                        '<a href="../discard_card/' + room_id.toString() + "/" + i.toString() + '">Discard</a></div></div>'
                }
                else {
                    inner_html += '<div class="card-back"></div>'
                }
            }
        }
        else {
            for(let i = 0; i < hand["cards"].length; i++) {
                let card = hand["cards"][i]
                if(items['my_turn'] && items['active'] && items["hints"] > 0){
                    inner_html +=
                        '<div class="card-' + getColorString(card[0]) + '" style="cursor: pointer;" onclick="Dropdown2(' + i.toString() + ',' + hand["player_id"] + ')">' + card[1].toString() +
                        '<div id="player-' + hand["player_id"].toString() + '-card-dropdown-' + i.toString() + '" class="dropdown-content">' +
                        '<a href="../give_hint_color/' + room_id.toString() + "/" + card[0].toString() + "/" + hand["player_id"] + '">Color</a>' +
                        '<a href="../give_hint_number/' + room_id.toString() + "/" + card[1].toString() + "/" + hand["player_id"] + '">Number</a></div></div>'
                }
                else {
                    inner_html +=
                        '<div class="card-' + getColorString(card[0]) + '">' + card[1].toString() + '</div>'
                }
            }
        }
        inner_html += '</div>'
        hand_element.innerHTML = inner_html

        // Adds the tabletop item to the HTML list
        hands_list.appendChild(hand_element)
    }

    // ROOM MESSAGE
    let room_message_element = document.getElementById("id_room_message")
    room_message_element.innerHTML = items["room_message"]

}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}




// Close all dropdowns
function closeDropdowns(){
    var dropdowns = document.getElementsByClassName("dropdown-content")
    var i;
    for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
            openDropdown.classList.remove('show')
        }
    }
}

// Open dropdown menu for player actions if it is the player's turn
function Dropdown(i) {
    closeDropdowns()
    var element_id = "self-card-dropdown-" + i.toString()
    document.getElementById(element_id).classList.toggle("show")
    
}

function Dropdown2(i, player_id) {
    closeDropdowns()
    var element_id = "player-" + player_id.toString() + "-card-dropdown-" + i.toString()
    document.getElementById(element_id).classList.toggle("show")
    
}
  
// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.card-white') &&
        !event.target.matches('.card-yellow') &&
        !event.target.matches('.card-green') &&
        !event.target.matches('.card-blue') &&
        !event.target.matches('.card-red') &&
        !event.target.matches('.card-back')) {
        closeDropdowns()
    }
}
