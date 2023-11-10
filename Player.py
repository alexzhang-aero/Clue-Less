import pygame
import os
import Deck
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)

class Player(pygame.sprite.Sprite):
    def __init__(self,
                 loc,
                 dealtCards,
                 id:int,
                 activePlayer:int):
        super(Player, self).__init__()
        

        self.dealtCards = dealtCards
        self.knownCards = dealtCards

        self.movesRemaining = 0
        self.keyPressed = False
        self.loc = loc
        self.id = id
        self.activePlayer = activePlayer

        self.guessing = False
        self.guessingCards = {Deck.ClueType.ROOM: None,
                              Deck.ClueType.WEAPON: None,
                              Deck.ClueType.SUSPECT: None}

    def convert_alpha(self):
        self.surf = self.surf.convert_alpha()

    def set_moves_remaining(self, moves):
        self.movesRemaining = moves

    # Move the sprite based on user keypresses
    def update(self,  validMoves):
        pressed_keys = pygame.key.get_pressed()
        if self.movesRemaining>0:
            playerMoved = False
            if pressed_keys[K_UP] and validMoves['up']:
                if not self.keyPressed:
                    playerMoved = True
                    self.loc[1] -= 50
            elif pressed_keys[K_DOWN] and validMoves['down']:
                if not self.keyPressed:
                    playerMoved = True
                    self.loc[1] += 50
            elif pressed_keys[K_LEFT] and validMoves['left']:
                if not self.keyPressed:
                    playerMoved = True
                    self.loc[0] -= 50
            elif pressed_keys[K_RIGHT] and validMoves['right']:
                if not self.keyPressed:
                    playerMoved = True
                    self.loc[0] += 50
            else:
                # This Is To Account For A Key Being Held Down
                self.keyPressed = False

            if playerMoved:
                self.keyPressed = True
                self.movesRemaining -= 1
            
            if self.movesRemaining == 0:
                # swap active turn value so the server sees it when passed
                if self.id==1:
                    self.activePlayer = 0
                else:
                    self.activePlayer = 1

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