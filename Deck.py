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
        self.cards.append(card)
    
    def RemoveCard(self, card):
        self.cards.remove(card)

    def IsCardInDeck(self, cardIn):
        for card in self.cards:
            if cardIn.name == card.name:
                return True
        return False

def GetAllCards():
    roomList = [Card(ClueType.ROOM, 'Lab', 'Lab.png', 0),
                Card(ClueType.ROOM, 'Kitchen', 'Kitchen.png', 1),
                Card(ClueType.ROOM, 'Dorm', 'Dorm.png', 2)]
    weaponList = [Card(ClueType.WEAPON, 'Wand', 'Wand.png', 0),
                  Card(ClueType.WEAPON, 'Sword', 'Sword.png', 1),
                  Card(ClueType.WEAPON, 'Staff', 'Staff.png', 2)]
    suspectList = [Card(ClueType.SUSPECT, 'Wizard', 'Wizard.png', 0),
                   Card(ClueType.SUSPECT, 'Knight', 'Knight.png', 1),
                   Card(ClueType.SUSPECT, 'King', 'King.png', 2)]
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