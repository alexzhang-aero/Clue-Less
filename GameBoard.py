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
                 doorLoc,
                 fileName,
                 clue):
        super(Room, self).__init__()
        self.surf = pygame.image.load(os.path.join('img', 'Rooms', fileName)).convert()
        self.surf = pygame.transform.scale(self.surf, (size[0], size[1])) 
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(topleft=(loc[0], loc[1]))
        self.loc = loc
        self.size = size
        self.doorLoc = doorLoc
        self.clue = clue

class GameBoard:
    def __init__(self, screen):
        self.screen = screen
        self.roomList = self.create_rooms()

        self.surf = pygame.image.load(os.path.join('img', "WizardSprite.png")).convert_alpha()
        self.surf.set_colorkey((0, 0, 0))

        self.surf2 = pygame.image.load(os.path.join('img', "WizardSprite.png")).convert_alpha()
        self.surf2.set_colorkey((0, 0, 0))
        
        self.buttons = []

    def create_rooms(self):
        roomList = []
        roomDetails = [{'loc': [300, 0], 'size': [350, 350], 'doorLoc': [125, 300], 'fileName': 'LabRoom.png', 'clue': None}]
        for room in roomDetails:
            roomList.append(Room(room['loc'], room['size'], room['doorLoc'], room['fileName'], room['clue']))
        return roomList

    def build_game_board(self, player):
        movesRemaining = player.movesRemaining
        self.screen.fill((0, 0, 0))
        self.buttons = []

        backgroundSurf = pygame.image.load(os.path.join('img', 'Background.png')).convert()
        backgroundSurf = pygame.transform.scale(backgroundSurf, (1000, 1000)) 
        backgroundSurf.set_colorkey((0, 0, 0), RLEACCEL)
        self.screen.blit(backgroundSurf, backgroundSurf.get_rect(topleft=(0, 0)))

        for room in self.roomList:
            self.screen.blit(room.surf, room.rect)

        hudTextColor = dimGold
        if player.guessing:
            clueScreenLocations = self.BuildGuessWindow(player)
            lastLoc = 0
            for clue in clueScreenLocations:
                clueLoc = clueScreenLocations[clue]
                self.buttons.append((clueLoc[0], clueLoc[0] + 100 , clueLoc[1], clueLoc[1] + 40, ToggleGuessedClue, clue))
                lastLoc= (clueLoc[0], clueLoc[1] + 40)
            if player.AllCardTypesGuessed():
                self.buttons.append((lastLoc[0], lastLoc[0] + 100 , lastLoc[1], lastLoc[1] + 40, SubmitGuess, None))
        elif player.id == player.activePlayer:
            self.buttons.append((0, 300, 1000, 1200, RollDice, None))
            self.buttons.append((300, 900, 1000, 1200, SetGuessing, None))
            hudTextColor = gold
            
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render('Moves Remaining: {}'.format(movesRemaining), True, hudTextColor, None)
        self.screen.blit(text, text.get_rect(topleft=(600, 1100)))
        text = font.render('Roll The Dice', True, hudTextColor, None)
        self.screen.blit(text, text.get_rect(topleft=(50, 1100)))
        text = font.render('Make Guess', True, hudTextColor, None)
        self.screen.blit(text, text.get_rect(topleft=(300, 1100)))
        pygame.display.flip()

    def update_player_sprites(self, p1, p2):
        if not p1.guessing:
            # Player 1
            rect = self.surf.get_rect(topleft=(p1.loc[0], p1.loc[1]))
            self.surf = pygame.transform.scale(self.surf, (50, 50))

            # Player 2
            rect2 = self.surf2.get_rect(topleft=(p2.loc[0], p2.loc[1]))
            self.surf2 = pygame.transform.scale(self.surf2, (50, 50))

            self.screen.blit(self.surf, rect)
            self.screen.blit(self.surf2, rect2)
            pygame.display.flip()

    def collide(self, loc, xMin, xMax, yMin, yMax):
        return loc[0] >= xMin and loc[0] < xMax and loc[1] >= yMin and loc[1] < yMax

    def get_valid_moves(self, playerLoc, screenBounds):
        validMoves = {'up': True, 'right': True, 'down': True, 'left': True}
        newLocList = {'up': (playerLoc[0], playerLoc[1] - 50),
                      'right': (playerLoc[0] + 50, playerLoc[1]),
                      'down': (playerLoc[0], playerLoc[1] + 50),
                      'left': (playerLoc[0] - 50, playerLoc[1])}

        for direction in newLocList:
            newLoc = newLocList[direction]

            if newLoc[0] < 0 or newLoc[0] >= screenBounds[0] or newLoc[1] < 0 or newLoc[1] >= screenBounds[1]:
                validMoves[direction] = False
                continue

            for room in self.roomList:
                if (not self.collide(newLoc, room.loc[0] + room.doorLoc[0], room.loc[0] + room.doorLoc[0] + 50, room.loc[1] + room.doorLoc[1], room.loc[1] + room.doorLoc[1] + 50)) and \
                        (not self.collide(newLoc, room.loc[0] + 50, room.loc[0] + room.size[0] - 50, room.loc[1] + 50, room.loc[1] + room.size[1] - 50)) and \
                        self.collide(newLoc, room.loc[0], room.loc[0] + room.size[0], room.loc[1], room.loc[1] + room.size[1]):
                    validMoves[direction] = False
                    break

        return validMoves
    
    def BuildGuessWindow(self, player):
        backgroundSurf = pygame.image.load(os.path.join('img', 'GuessBoard.png')).convert()
        backgroundSurf = pygame.transform.scale(backgroundSurf, (1000, 1000)) 
        backgroundSurf.set_colorkey((0, 0, 0), RLEACCEL)
        backgroundSurf.convert_alpha()
        self.screen.blit(backgroundSurf, backgroundSurf.get_rect(topleft=(0, 0)))
        backgroundSurf.convert_alpha()
        roomList, weaponList, suspectList = Deck.GetAllCards()
        
        clueTypeFont = pygame.font.Font('freesansbold.ttf', 50)
        clueNameFont = pygame.font.Font('freesansbold.ttf', 40)

        vertOffset = 120

        clueScreenLocations = {}

        for clueList, clueType, clueTypeString in [[roomList, Deck.ClueType.ROOM, 'Rooms'],
                                                   [weaponList, Deck.ClueType.WEAPON, 'Weapons'],
                                                   [suspectList, Deck.ClueType.SUSPECT, 'Suspects']]:
            text = clueTypeFont.render(clueTypeString, True, blue, None)
            self.screen.blit(text, text.get_rect(topleft=(200, vertOffset)))
            vertOffset += 70
            for clue in clueList:

                textColor = black
                if player.guessingCards[clueType] and player.guessingCards[clueType].equals(clue):
                    textColor = green
                elif player.knownCards.IsCardInDeck(clue):
                    textColor = gray

                text = clueNameFont.render(clue.name, True, textColor, None)
                self.screen.blit(text, text.get_rect(topleft=(200, vertOffset)))
                clueScreenLocations[clue] = (200, vertOffset)
                vertOffset += 40
            vertOffset += 40
        if player.AllCardTypesGuessed():
            text = clueNameFont.render('SUBMIT GUESS', True, green, None)
            self.screen.blit(text, text.get_rect(topleft=(200, vertOffset)))
        return clueScreenLocations
    
    def ClickScreen(self, mouseLoc, player):
        print(mouseLoc)
        for button in self.buttons:
            print(button)
            if self.collide((mouseLoc[0], mouseLoc[1]), button[0], button[1], button[2], button[3]):
                if button[5]:
                    player = button[4](player, button[5])
                else:
                    player = button[4](player)
        return player


def RollDice(player):
    print('Rolling dice...')
    player.set_moves_remaining(randrange(1, 6))
    return player

def SetGuessing(player):
    print('Starting Guessing...')
    player.guessing = True
    return player

def ToggleGuessedClue(player, clue):
    player.ToggleGuessedCard(clue)
    return player

def SubmitGuess(player):
    player.ClearGuesses()
    return player