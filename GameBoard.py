import pygame
import os
import Deck
from Room import CreateRooms
from random import randrange
from Player import PlayerState

from pygame.locals import (
    RLEACCEL
)

white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
red = (255, 0, 0)
black = (0, 0, 0)
gray = (50, 50, 50)
gold = (218,165,32)
dimGold = (100,50,0)

class GameBoard:
    def __init__(self, 
                 screen,
                 size):
        self.screen = screen
        self.size = (size[0], size[1] - 200)
        self.buttons = []

        roomsizeX = self.size[0] / 4
        roomsizeY = self.size[1] / 4
        roomClueList, weaponsList, _ = Deck.GetAllCards()
        self.roomList = CreateRooms(roomClueList, (roomsizeX, roomsizeY), weaponsList)

    def BuildGameBoard(self, players, userID):
        userPlayer = players[userID]
        self.screen.fill((0, 0, 0))
        
        if userPlayer.state in [PlayerState.WINNER, PlayerState.LOSER]:
            self.BuildGameOver(players)
            pygame.display.flip()
            return 

        backgroundSurf = pygame.image.load(os.path.join('img', 'Background.png')).convert()
        backgroundSurf = pygame.transform.scale(backgroundSurf, self.size) 
        backgroundSurf.set_colorkey((0, 0, 0), RLEACCEL)
        self.screen.blit(backgroundSurf, backgroundSurf.get_rect(topleft=(0, 0)))


        for room in self.roomList:
            roomXLoc = (room.loc[0] * (self.size[0] / 6)) + (room.loc[0] * (self.size[0] / 48))
            roomYLoc = (room.loc[1] * (self.size[1] / 6)) + (room.loc[1] * (self.size[1] / 48))
            self.screen.blit(room.surf,
                             room.surf.get_rect(topleft=(roomXLoc, roomYLoc)))
            if room.weapon:
                weapon_rect = room.weapon_surf.get_rect(topleft=(roomXLoc + (room.size[0] / 2) - (room.size[0] / 8),
                                                                  roomYLoc + (room.size[1] / 2) - (room.size[1] / 8)))
                self.screen.blit(room.weapon_surf, weapon_rect)

            playerInRoomCol = 0
            playerInRoomRow = 0
            for player in players:
                if player.state != PlayerState.OUT and\
                    room.loc[0] == player.loc[0] and room.loc[1] == player.loc[1]:
                    spriteXLoc = roomXLoc + (playerInRoomCol * (room.size[0] / 3))
                    spriteYLoc = roomYLoc + (playerInRoomRow * (room.size[1] / 2))
                    sprite = player.CreateSprite((room.size[0] / 3, room.size[1] / 3))
                    self.screen.blit(sprite,
                                    sprite.get_rect(topleft=(spriteXLoc, spriteYLoc)))
                    playerInRoomCol += 1
                    if playerInRoomCol == 3:
                        playerInRoomRow += 1

        for player in players:
            if player.state not in [PlayerState.OUT, PlayerState.TURN_OVER_OUT] and\
               player.loc[0] % 2 or player.loc[1] % 2:
                spriteXLoc = (player.loc[0] * ((self.size[0] * 3) / 16)) + (self.size[0] / 8) - (self.size[0] / 20)
                spriteYLoc = (player.loc[1] * ((self.size[1] * 3) / 16)) + (self.size[1] / 8) - (self.size[1] / 20)
                sprite = player.CreateSprite((self.size[0] / 10, self.size[1] / 10))
                self.screen.blit(sprite,
                                 sprite.get_rect(topleft=(spriteXLoc, spriteYLoc)))

        xPlayerLoc = 0
        yPlayerLoc = 0
        for player in players:
            if player.state != PlayerState.OUT:
                hudSurf = player.CreateHudImg((100,100), not player.IsActive())
                self.screen.blit(hudSurf, hudSurf.get_rect(topleft=(xPlayerLoc * 100, self.size[1] + yPlayerLoc * 100)))
            xPlayerLoc += 1
            if xPlayerLoc == 3:
                xPlayerLoc = 0
                yPlayerLoc = 1

        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render('SEE CARDS', True, gold, None)
        self.screen.blit(text, text.get_rect(topleft=(305, self.size[1] + 80)))
        self.buttons.append((305, 500 , self.size[1], self.size[1] + 200, LookAtCards, None))

        hudSurf = userPlayer.CreateHudImg((200,200), userPlayer.state == PlayerState.OUT)
        self.screen.blit(hudSurf, hudSurf.get_rect(topleft=(self.size[0]/2, self.size[1])))

        font = pygame.font.Font('freesansbold.ttf', 32)
        if userPlayer.state == PlayerState.OUT:
            text = font.render('YOU LOST', True, red, gray)
            self.screen.blit(text, text.get_rect(topleft=(self.size[0] - 285, self.size[1] + 80)))
        else:
            if userPlayer.state == PlayerState.WAITING_IN_ROOM:
                text = font.render('Make Guess', True, green, gray)
                self.screen.blit(text, text.get_rect(topleft=(self.size[0] - 285, self.size[1] + 20)))
                self.buttons.append((self.size[0] - 300, self.size[0] , self.size[1] + 20, self.size[1] + 120, MakeGuess, None))
            text = font.render('Make Accusation', True, red, gray)
            self.screen.blit(text, text.get_rect(topleft=(self.size[0] - 285, self.size[1] + 100)))
            self.buttons.append((self.size[0] - 300, self.size[0] , self.size[1] + 120, self.size[1] + 200, MakeAccusation, None))

        if userPlayer.state == PlayerState.GUESSING:
            currRoom = self.GetRoomFromLoc(userPlayer.loc)
            userPlayer.guessingCards[Deck.ClueType.ROOM] = currRoom.clue
            _, weaponList, suspectList = Deck.GetAllCards()
            clueScreenLocations = self.BuildGuessWindow([],
                                                        weaponList,
                                                        suspectList,
                                                        Deck.DictToDeck(userPlayer.guessingCards),
                                                        userPlayer.knownCards,
                                                        3,
                                                        'Submit Suggestion')
            lastLoc = 0
            for clue in clueScreenLocations:
                clueLoc = clueScreenLocations[clue]
                self.buttons.append((clueLoc[0], clueLoc[0] + 100 , clueLoc[1], clueLoc[1] + clueLoc[2], ToggleGuessedClue, clue))
                lastLoc = (clueLoc[0], clueLoc[1] + clueLoc[2])
            if userPlayer.AllCardTypesGuessed():
                self.buttons.append((lastLoc[0], lastLoc[0] + 100 , lastLoc[1], lastLoc[1] + clueLoc[2], SubmitGuess, None))

        elif userPlayer.state == PlayerState.RESPONDING_TO_GUESS:
            guessedCards = None
            for player in players:
                if player.state == PlayerState.AWAITING_GUESS_RESPONSE:
                    guessedCards = player.guessingCards

            roomList = []
            weaponList = []
            suspectList = []
            if userPlayer.dealtCards.IsCardInDeck(guessedCards[Deck.ClueType.ROOM]):
                roomList = [guessedCards[Deck.ClueType.ROOM]]
            if userPlayer.dealtCards.IsCardInDeck(guessedCards[Deck.ClueType.WEAPON]):
                weaponList = [guessedCards[Deck.ClueType.WEAPON]]
            if userPlayer.dealtCards.IsCardInDeck(guessedCards[Deck.ClueType.SUSPECT]):
                suspectList = [guessedCards[Deck.ClueType.SUSPECT]]

            clueScreenLocations = self.BuildGuessWindow(roomList,
                                                        weaponList,
                                                        suspectList,
                                                        userPlayer.guessResponse,
                                                        None,
                                                        1,
                                                        'Submit Response')
            lastLoc = 0
            for clue in clueScreenLocations:
                clueLoc = clueScreenLocations[clue]
                self.buttons.append((clueLoc[0], clueLoc[0] + 100 , clueLoc[1], clueLoc[1] + clueLoc[2], ToggleGuessedClueResponse, clue))
                lastLoc = (clueLoc[0], clueLoc[1] + clueLoc[2])
            if userPlayer.guessResponse.Count():
                self.buttons.append((lastLoc[0], lastLoc[0] + 100 , lastLoc[1], lastLoc[1] + clueLoc[2], SubmitGuessResponse, None))
        
        elif userPlayer.state == PlayerState.ACCUSING:
            roomList, weaponList, suspectList = Deck.GetAllCards()
            clueScreenLocations = self.BuildGuessWindow(roomList,
                                                        weaponList,
                                                        suspectList,
                                                        Deck.DictToDeck(userPlayer.guessingCards),
                                                        userPlayer.knownCards,
                                                        3,
                                                        'Submit Accusation')
            lastLoc = 0
            for clue in clueScreenLocations:
                clueLoc = clueScreenLocations[clue]
                self.buttons.append((clueLoc[0], clueLoc[0] + 100 , clueLoc[1], clueLoc[1] + clueLoc[2], ToggleGuessedClue, clue))
                lastLoc = (clueLoc[0], clueLoc[1] + clueLoc[2])
            if userPlayer.AllCardTypesGuessed():
                self.buttons.append((lastLoc[0], lastLoc[0] + 100 , lastLoc[1], lastLoc[1] + clueLoc[2], SubmitAccusation, None))

        elif userPlayer.state == PlayerState.LOOKING_AT_CARDS:
            clueScreenLocations = self.BuildGuessWindow(userPlayer.knownCards.GetAllCardsOfOneType(Deck.ClueType.ROOM),
                                                        userPlayer.knownCards.GetAllCardsOfOneType(Deck.ClueType.WEAPON),
                                                        userPlayer.knownCards.GetAllCardsOfOneType(Deck.ClueType.SUSPECT),
                                                        None,
                                                        None,
                                                        0,
                                                        'Close Window')
            lastLoc = 0
            for clue in clueScreenLocations:
                clueLoc = clueScreenLocations[clue]
                lastLoc = (clueLoc[0], clueLoc[1] + clueLoc[2])
            self.buttons.append((lastLoc[0], lastLoc[0] + 100 , lastLoc[1], lastLoc[1] + clueLoc[2], DoneLookingAtCards, None))

        pygame.display.flip()

    def BuildGuessWindow(self,
                         roomList,
                         weaponList,
                         suspectList,
                         pickedCards,
                         knownCards,
                         neededSelections,
                         guessTypeString):

        backgroundSurf = pygame.image.load(os.path.join('img', 'GuessBoard.png')).convert()
        backgroundSurf = pygame.transform.scale(backgroundSurf, (1000, 1000))
        backgroundSurf.set_colorkey((0, 0, 0), RLEACCEL)
        backgroundSurf = backgroundSurf.convert_alpha()
        self.screen.blit(backgroundSurf, backgroundSurf.get_rect(topleft=(0, 0)))
        
        if not roomList:
            roomList = []
        if not weaponList:
            weaponList = []
        if not suspectList:
            suspectList = []

        numOfClues = len(roomList) + len(weaponList) + len(suspectList) + 5
        
        spacePerClue = min(int(800 / numOfClues), 70)

        clueTypeFont = pygame.font.Font('freesansbold.ttf', spacePerClue)
        clueNameFont = pygame.font.Font('freesansbold.ttf', spacePerClue - 5)

        vertOffset = 120

        clueScreenLocations = {}

        for clueList, clueType, clueTypeString in [[roomList, Deck.ClueType.WEAPON, 'Room'],
                                                   [weaponList, Deck.ClueType.WEAPON, 'Weapon'],
                                                   [suspectList, Deck.ClueType.SUSPECT, 'Suspect']]:
            if not clueList:
                continue
            text = clueTypeFont.render(clueTypeString, True, blue, None)
            self.screen.blit(text, text.get_rect(topleft=(200, vertOffset)))
            vertOffset += spacePerClue
            for clue in clueList:

                textColor = black
                if pickedCards and pickedCards.IsCardInDeck(clue):
                    textColor = green
                elif knownCards and knownCards.IsCardInDeck(clue):
                    textColor = gray

                text = clueNameFont.render(clue.name, True, textColor, None)
                self.screen.blit(text, text.get_rect(topleft=(200, vertOffset)))
                clueScreenLocations[clue] = (200, vertOffset, spacePerClue)
                vertOffset += spacePerClue

        if neededSelections == 0 or pickedCards.Count() == neededSelections:
            text = clueNameFont.render(guessTypeString, True, green, None)
            self.screen.blit(text, text.get_rect(topleft=(200, vertOffset)))

        return clueScreenLocations

    def BuildGameOver(self, players):
        winner = None
        for player in players:
            if player.state == PlayerState.WINNER:
                winner = player

        font = pygame.font.Font('freesansbold.ttf', 50)
        text = font.render('Game Over', True, gold, None)
        self.screen.blit(text, text.get_rect(topleft=(self.size[0]/2 - 120, 30)))
        text = font.render('Winner:', True, gold, None)
        self.screen.blit(text, text.get_rect(topleft=(self.size[0]/2 - 70, 80)))
    
        hudSurf = winner.CreateHudImg((500,500), False)
        self.screen.blit(hudSurf, hudSurf.get_rect(topleft=(self.size[0]/2 - 250, 150)))

    def ClickScreen(self, mouseLoc, player):
        print(mouseLoc)
        for button in self.buttons:
            print(button)
            if collide((mouseLoc[0], mouseLoc[1]), button[0], button[1], button[2], button[3]):
                if button[5]:
                    player = button[4](player, button[5])
                else:
                    player = button[4](player)
        return player

    def GetValidMoves(self, allPlayers, playerId):
        playerLoc = allPlayers[playerId].loc
        validMoves = {'up': True, 'right': True, 'down': True, 'left': True}
        newLocList = {'up': (playerLoc[0], playerLoc[1] - 1),
                     'right': (playerLoc[0] + 1, playerLoc[1]),
                     'down': (playerLoc[0], playerLoc[1] + 1),
                     'left': (playerLoc[0] - 1, playerLoc[1])}

        for direction in newLocList:
            newLoc = newLocList[direction]

            if newLoc[0] < 0 or newLoc[0] > 4 or newLoc[1] < 0 or newLoc[1] > 4:
                validMoves[direction] = False
                continue
            
            # Ensure player moves Room -> Hallway or Hallway -> Room
            if newLoc[0] % 2 != 0 and newLoc[0] % 2 != 0:
                validMoves[direction] = False
                continue

            for player in allPlayers:
                # if other player... and potential loc is a hallway... and other player is in potential loc
                if player.id != playerId and\
                   (newLoc[0] % 2 != 0 or newLoc[1] % 2 != 0) and\
                   player.loc == newLoc:
                    validMoves[direction] = False
                    continue

        return validMoves
    

    def GetRoomFromLoc(self, loc):
        for room in self.roomList:
            if loc[0] == room.loc[0] and loc[1] == room.loc[1]:
                return room
        return None

def collide(loc, xMin, xMax, yMin, yMax):
    return loc[0] >= xMin and loc[0] < xMax and loc[1] >= yMin and loc[1] < yMax

def ToggleGuessedClue(player, clue):
    player.ToggleGuessedCard(clue)
    return player

def ToggleGuessedClueResponse(player, clue):
    player.guessResponse = Deck.Deck()
    player.guessResponse.AddCard(clue)
    return player

def SubmitGuess(player):
    player.state = PlayerState.AWAITING_GUESS_RESPONSE
    return player

def MakeAccusation(player):
    player.state = PlayerState.ACCUSING
    return player

def MakeGuess(player):
    player.state = PlayerState.GUESSING
    return player

def SubmitAccusation(player):
    player.state = PlayerState.ACCUSED
    return player

def SubmitGuessResponse(player):
    player.state = PlayerState.GUESS_RESPONSE_SENT
    return player

def LookAtCards(player):
    player.state = PlayerState.LOOKING_AT_CARDS
    return player

def DoneLookingAtCards(player):
    player.state = PlayerState.MOVING
    return player