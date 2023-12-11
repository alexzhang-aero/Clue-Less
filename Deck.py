from enum import Enum
import pygame
import os
from random import randrange

class ClueType(Enum):
    ROOM = 0
    WEAPON = 1
    SUSPECT = 2

class Card():
    def __init__(self,
                 type,
                 name,
                 fileName,
                 id):
        self.type = type
        self.name = name
        self.fileName = fileName
        self.id = id

    def equals(self, cardIn):
        return cardIn.type == self.type and cardIn.id == self.id

class Deck():
    def __init__(self):
        self.cards = []
        
    def AddCard(self, card):
        if not self.IsCardInDeck(card):
            self.cards.append(card)
    
    def RemoveCard(self, card):
        self.cards.remove(card)

    def IsCardInDeck(self, cardIn):
        for card in self.cards:
            if cardIn.name == card.name:
                return True
        return False
    
    def GetAllCardsOfOneType(self, typeIn):
        cardsOut = []
        for card in self.cards:
            if card.type == typeIn:
                cardsOut.append(card)
        return cardsOut

    def Count(self):
        return len(self.cards)
    
    def Print(self):
        for card in self.cards:
            print(card.name)

def GetAllCards():
    roomList = [Card(ClueType.ROOM, 'Lab', 'Rooms/lab.png', 0),
                Card(ClueType.ROOM, 'Armory', 'Rooms/armory.png', 1),
                Card(ClueType.ROOM, 'Ballroom', 'Rooms/ballroom.png', 2),
                Card(ClueType.ROOM, 'Bedroom', 'Rooms/bedroom.png', 3),
                Card(ClueType.ROOM, 'Courtyard', 'Rooms/courtyard.png', 4),
                Card(ClueType.ROOM, 'Dragon\'s Lair', 'Rooms/dragonlair.png', 5),
                Card(ClueType.ROOM, 'Library', 'Rooms/library.png', 6),
                Card(ClueType.ROOM, 'Main Hall', 'Rooms/mainhall.png', 7),
                Card(ClueType.ROOM, 'Observation room', 'Rooms/observationroom.png', 8)]

    weaponList = [Card(ClueType.WEAPON, 'Wand', 'Clues/wand.png', 0),
                  Card(ClueType.WEAPON, 'Dagger', 'Clues/dagger.png', 1),
                  Card(ClueType.WEAPON, 'Staff', 'Clues/staff.png', 2),
                  Card(ClueType.WEAPON, 'Mace', 'Clues/mace.png', 3),
                  Card(ClueType.WEAPON, 'Whip', 'Clues/whip.png', 4),
                  Card(ClueType.WEAPON, 'Poison', 'Clues/poison.png', 5)]

    suspectList = [Card(ClueType.SUSPECT, 'Wizard', 'Players/Wizard.png', 0),
                   Card(ClueType.SUSPECT, 'Knight', 'Players/Knight.png', 1),
                   Card(ClueType.SUSPECT, 'Dwarf', 'Players/Dwarf.png', 2),
                   Card(ClueType.SUSPECT, 'Princess', 'Players/Princess.png', 3),
                   Card(ClueType.SUSPECT, 'Vampire', 'Players/Vampire.png', 4),
                   Card(ClueType.SUSPECT, 'Witch', 'Players/Witch.png', 5)]

    return roomList, weaponList, suspectList

def DealCards(numPlayers):
    roomList, weaponList, suspectList = GetAllCards()

    murderEnvelope = {}
    for cardList, clueType in [[roomList, ClueType.ROOM],
                               [weaponList, ClueType.WEAPON],
                               [suspectList, ClueType.SUSPECT]]:
        murderEnvelope[clueType] = cardList.pop(randrange(len(cardList) - 1))

    cardPiles = []
    for _ in range(numPlayers):
        cardPiles.append(Deck())

    playerId = 0
    for cardList in [roomList, weaponList, suspectList]:
        while len(cardList):
            cardPiles[playerId].AddCard(cardList.pop(randrange(len(cardList))))
            playerId += 1
            if playerId == numPlayers:
                playerId = 0
        
    return murderEnvelope, cardPiles

def DictToDeck(dictOfCards):
    deckOut = Deck()
    for x in dictOfCards:
        if dictOfCards[x]:
            deckOut.AddCard(dictOfCards[x])
    return deckOut