import pygame
import os
import Deck
import math
from enum import Enum
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)

class PlayerState(Enum):
    WAITING = 0
    MOVING = 1
    GUESSING = 2
    AWAITING_GUESS_RESPONSE = 3
    RESPONDING_TO_GUESS = 4
    GUESS_RESPONSE_SENT = 5
    NO_GUESS_RESPONSE = 6
    TURN_OVER = 7
    ACCUSING = 8
    ACCUSED = 9
    OUT = 10
    WINNER = 11
    LOSER = 12

class Player(pygame.sprite.Sprite):
    def __init__(self,
                 loc,
                 dealtCards,
                 id:int,
                 name,
                 isOwned=False):
        super(Player, self).__init__()

        self.dealtCards = dealtCards
        self.knownCards = dealtCards

        self.loc = loc
        self.id = id
        
        self.name = name
        self.isOwned = isOwned

        self.state = PlayerState.WAITING
        self.movedByGuess = False

        self.guessingCards = {Deck.ClueType.ROOM: None,
                              Deck.ClueType.WEAPON: None,
                              Deck.ClueType.SUSPECT: None}

        self.guessResponse = Deck.Deck()


    def CreateSprite(self, size):
        spriteSurf = pygame.image.load(os.path.join('img', 'Players', '{}.png'.format(self.name))).convert_alpha()
        spriteSurf = pygame.transform.scale(spriteSurf, (size[0], size[1])) 
        spriteSurf.set_colorkey((0, 0, 0))
        return spriteSurf

    def CreateHudImg(self, size):
        hudSurf = pygame.image.load(os.path.join('img', 'Players', '{}HUD.png'.format(self.name))).convert_alpha()
        hudSurf = pygame.transform.scale(hudSurf, (size[0], size[1])) 
        hudSurf.set_colorkey((0, 0, 0))
        return hudSurf

    def convert_alpha(self):
        self.spriteSurf = self.spriteSurf.convert_alpha()

    def CreateHudText(self, currentPlayerID):
        hudText = None
        if self.state == PlayerState.MOVING:
            if self.id == currentPlayerID:
                hudText = 'Your Move!'
            else:
                hudText = '{} To Move'.format(self.name)
        elif self.state == PlayerState.GUESSING:
            if self.id == currentPlayerID:
                hudText = 'Make A Guess!'
            else:
                hudText = '{} is Guessing'.format(self.name)
        elif self.state == PlayerState.RESPONDING_TO_GUESS:
            if self.id == currentPlayerID:
                hudText = 'Respond To The Guess!'
            else:
                hudText = '{} is Responding\n to a Guess'.format(self.name)

        return hudText

    # Move the sprite based on user keypresses
    def MakeMove(self, validMoves):
        pressedKeys = pygame.key.get_pressed()
        if self.state == PlayerState.MOVING:
            playerMoved = False

            # Checks player is in starting position and moves to adjacent hall with any keypress
            if any(pressedKeys) and (self.loc[0] % 1 != 0 or self.loc[1] % 1 != 0):
                playerMoved = True
                self.loc[0] = math.trunc(self.loc[0])
                self.loc[1] = math.trunc(self.loc[1])

            # Regular moves
            elif pressedKeys[K_UP] and validMoves['up']:
                playerMoved = True
                self.loc[1] -= 1
            elif pressedKeys[K_DOWN] and validMoves['down']:
                playerMoved = True
                self.loc[1] += 1
            elif pressedKeys[K_LEFT] and validMoves['left']:
                playerMoved = True
                self.loc[0] -= 1
            elif pressedKeys[K_RIGHT] and validMoves['right']:
                playerMoved = True
                self.loc[0] += 1

            if playerMoved:
                self.movedByGuess = False
                if self.loc[0] % 2 == 0 and self.loc[1] % 2 == 0:
                    self.state = PlayerState.GUESSING
                else:
                    self.state = PlayerState.TURN_OVER

    def __repr__(self):
        return f"Player {self.id} is at {self.loc}"

    def ToggleGuessedCard(self, card):
        newCardType = card.type
        if self.guessingCards[newCardType] is not None and self.guessingCards[newCardType].equals(card):
            self.guessingCards[newCardType] = None
        else:
            self.guessingCards[newCardType] = card

    def AllCardTypesGuessed(self):
        allGuessed = True
        for cardType in self.guessingCards:
            if self.guessingCards[cardType] is None:
                allGuessed = False
        return allGuessed

    def ClearGuesses(self):
        self.guessing = False
        self.guessingCards = {Deck.ClueType.ROOM: None,
                              Deck.ClueType.WEAPON: None,
                              Deck.ClueType.SUSPECT: None}
        if self.id==1:
            self.activePlayer = 0
        else:
            self.activePlayer = 1