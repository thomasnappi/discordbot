import random

def get_card():
    colors = ['red','green','blue','yellow']
    values = ['1','2','3','4','5','6','7','8','9','skip','reverse','draw2','draw4','wildcard']
    card = {}
    card["color"] = colors[random.randint(0,len(colors)-1)]
    card["value"] = values[random.randint(0,len(values)-1)]
    return card

def print_card(c):
    return c["color"] + " " + c["value"]

def get_card_of_hand(card, hand):
    for c in hand:
        if print_card(c) == card:
            return c
    return None

def remove_card_from_hand(card, hand):
    for c in range(len(hand)):
        if print_card(hand[c]) == print_card(card):
            return hand.pop(c)
    return None

def can_play_over(card, top):
    return card['color'] == top['color'] or card['value'] == top['value'] or card['value'] == 'draw4' or card['value'] == 'wildcard' or top['value'] == 'wildcard' or top['value'] == 'draw4'