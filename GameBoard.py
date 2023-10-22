import pygame
import os


from pygame.locals import (
    RLEACCEL
)

white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
black = (0, 0, 0)

class Room(pygame.sprite.Sprite):
    def __init__(self,
                 loc,
                 size,
                 doorLoc,
                 fileName,
                 clue):
        super(Room, self).__init__()
        self.surf = pygame.image.load(os.path.join('img', fileName)).convert()
        self.surf = pygame.transform.scale(self.surf, (size[0], size[1])) 
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(topleft=(loc[0], loc[1]))
        self.loc = loc
        self.size = size
        self.doorLoc = doorLoc
        self.clue = clue

def CreateRooms():
    roomList = []
    roomDetails= [{'loc':[300,0], 'size':[350,350], 'doorLoc': [125, 300], 'fileName':'LabRoom.png', 'clue': None}]
    for room in roomDetails:
        roomList.append(Room(room['loc'], room['size'], room['doorLoc'], room['fileName'], room['clue']))
    return roomList
        
def BuildGameBoard(screen, roomList, movesRemaining):
    # Fill the screen with black
    screen.fill((0, 0, 0))

    for room in roomList:
        screen.blit(room.surf, room.rect)

    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render('Moves Remaining: {}'.format(movesRemaining), True, green, black)
    screen.blit(text, text.get_rect(topleft=(600, 900)))
    text = font.render('Roll The Dice'.format(movesRemaining), True, green, black)
    screen.blit(text, text.get_rect(topleft=(0, 900)))



def Collide(loc, xMin, xMax, yMin, yMax):
    return loc[0] >= xMin and loc[0] < xMax\
               and loc[1] >= yMin and loc[1] < yMax

def GetValidMoves(playerLoc, roomList, screenBounds):
    validMoves = {'up': True, 'right': True, 'down': True, 'left': True}
    newLocList = {'up': (playerLoc[0], playerLoc[1] - 50), 
                  'right': (playerLoc[0] + 50, playerLoc[1]), 
                  'down': (playerLoc[0], playerLoc[1] + 50), 
                  'left': (playerLoc[0] - 50, playerLoc[1])}
    
    for direction in newLocList:
        newLoc = newLocList[direction]

        # Check You Are Not On Edge Of Screen
        if newLoc[0] < 0 or newLoc[0] >= screenBounds[0] \
           or newLoc[1] < 0 or newLoc[1] >= screenBounds[1]:
            validMoves[direction] = False
            continue

        for room in roomList:
            if (not Collide(newLoc, # Check You Would Be In A Door (Allowed)
                            room.loc[0] + room.doorLoc[0],
                            room.loc[0] + room.doorLoc[0] + 50,
                            room.loc[1] + room.doorLoc[1],
                            room.loc[1] + room.doorLoc[1] + 50)) and\
                (not Collide(newLoc, # Check You Are Already In A Room (Allowed)
                            room.loc[0] + 50,
                            room.loc[0] + room.size[0] - 50,
                            room.loc[1] + 50,
                            room.loc[1] + room.size[1] - 50)) and\
                   Collide(newLoc, # Check You Would Be In The Wall (Not Allowed)
                           room.loc[0],
                           room.loc[0] + room.size[0],
                           room.loc[1],
                           room.loc[1] + room.size[1]):
                validMoves[direction] = False
                break

    return validMoves

def update_player_sprites(screen, p1, p2):
    #p1
    surf = pygame.image.load(os.path.join('img', "WizardSprite.png")).convert_alpha()
    surf.set_colorkey((0,0,0))
    rect = surf.get_rect(topleft=(p1.loc[0], p1.loc[1]))
    surf = pygame.transform.scale(surf, (50, 50)) 
    #p2
    surf2 = pygame.image.load(os.path.join('img', "WizardSprite.png")).convert_alpha()
    surf2.set_colorkey((0,0,0))
    rect2 = surf2.get_rect(topleft=(p2.loc[0], p2.loc[1]))
    surf2 = pygame.transform.scale(surf2, (50, 50)) 

    screen.blit(surf, rect)
    screen.blit(surf2, rect2)

