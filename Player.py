import pygame
import os
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)

class Player(pygame.sprite.Sprite):
    def __init__(self,
                 loc,
                 weaponIn,
                 suspectIn,
                 roomIn):
        super(Player, self).__init__()
        self.surf = pygame.image.load(os.path.join('img', "WizardSprite.png"))
        self.surf.set_colorkey((0,0,0))
        self.rect = self.surf.get_rect(topleft=(loc[0], loc[1]))
        self.surf = pygame.transform.scale(self.surf, (50, 50)) 

        self.dealtCards = {'weapon':  weaponIn,
                           'suspect': suspectIn,
                           'room':    roomIn}
        self.knownCards = {'weapon':  [weaponIn],
                           'suspect': [suspectIn],
                           'room':    [roomIn]}

        self.movesRemaining = 0
        self.keyPressed = False
        self.loc = loc
        self.data = {"loc": loc,"weaponIn":weaponIn,"suspectIn":suspectIn,"roomIn":roomIn}

    # Move the sprite based on user keypresses
    def update(self, pressed_keys, validMoves):
        if self.movesRemaining:
            playerMoved = False
            if pressed_keys[K_UP] and validMoves['up']:
                if not self.keyPressed:
                    playerMoved = True
                    self.rect.move_ip(0, -50)
                    self.loc[1] -= 50
            elif pressed_keys[K_DOWN] and validMoves['down']:
                if not self.keyPressed:
                    playerMoved = True
                    self.rect.move_ip(0, 50)
                    self.loc[1] += 50
            elif pressed_keys[K_LEFT] and validMoves['left']:
                if not self.keyPressed:
                    playerMoved = True
                    self.rect.move_ip(-50, 0)
                    self.loc[0] -= 50
            elif pressed_keys[K_RIGHT] and validMoves['right']:
                if not self.keyPressed:
                    playerMoved = True
                    self.rect.move_ip(50, 0)
                    self.loc[0] += 50
            else:
                # This Is To Account For A Key Being Held Down
                self.keyPressed = False

            if playerMoved:
                self.keyPressed = True
                self.movesRemaining -= 1

        self.data = {"loc": self.loc,"weaponIn":self.weaponIn,"suspectIn":self.suspectIn,"roomIn":self.roomIn}
    
    def move(self,loc):
        self.rect.move_ip(loc[0], loc[1])
        self.loc = loc


        