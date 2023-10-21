#!/usr/bin/python3

import pygame
from pygame.locals import QUIT
from random import randrange 

from Player import Player
import GameBoard

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

def GamePlayLoop():
    GameBoard.BuildGameBoard(screen, roomList, player.movesRemaining)

    for event in pygame.event.get():
        if event.type == QUIT:
            return False
        # Checking If Roll Dice Gets Clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            if GameBoard.Collide((mouse[0], mouse[1]), 0, 300, 900, 1000):
                player.movesRemaining = randrange(1,6)

    # Player Movement
    player.update(pygame.key.get_pressed(), GameBoard.GetValidMoves(player.loc, roomList, (SCREEN_WIDTH, SCREEN_HEIGHT)))
    screen.blit(player.surf, player.rect)

    pygame.display.flip()
    clock.tick(30)
    return True


if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    player = Player([450, 450], None,None,None)
    roomList = GameBoard.CreateRooms()
    buttonLoc = []

    running = True
    
    # Main loop
    while running:
        running = GamePlayLoop()

    pygame.quit()