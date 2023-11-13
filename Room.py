import pygame
import os
import Deck
from random import randrange

from pygame.locals import (
    RLEACCEL
)

white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
black = (0, 0, 0)
gray = (50, 50, 50)
gold = (218,165,32)
dimGold = (100,50,0)


class Room(pygame.sprite.Sprite):
    def __init__(self,
                 loc,
                 size,
                 clue):
        super(Room, self).__init__()
        self.loc = loc
        self.size = size
        self.clue = clue
        self.players = []
        self.surf = pygame.image.load(os.path.join('img', self.clue.fileName)).convert()
        self.surf = pygame.transform.scale(self.surf, (size[0], size[1])) 
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)

def CreateRooms(roomClueList, roomSize):
    roomList = []
    row = 0
    col = 0
    for roomClue in roomClueList:
        roomList.append(Room((col, row), roomSize, roomClue))
        col += 2
        if col > 4:
            col = 0
            row += 2

    return roomList