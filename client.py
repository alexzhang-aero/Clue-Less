import pygame
import socket
import threading
from network import Network
from pygame.locals import QUIT
from random import randrange

from Player import Player
import GameBoard

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Clue-less - Client')
clock = pygame.time.Clock()


def GamePlayLoop(player:Player, other_player: Player):
    """ Main game loop
    
    other_player: Player dict representing the other player
    This other_player object should be updated to an array of Player objects
    in the future to support 6 players.
    """
    roomList = GameBoard.CreateRooms()
    
    # while True:
    GameBoard.BuildGameBoard(screen, roomList, player.movesRemaining)

    for event in pygame.event.get():
        if event.type == QUIT:
            return False

        if player.activePlayer==player.id and event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            if GameBoard.Collide((mouse[0], mouse[1]), 0, 300, 900, 1000):
                player.movesRemaining = randrange(1, 6)

    while player.activePlayer==player.id:
        player.update(pygame.key.get_pressed(), GameBoard.GetValidMoves(player.loc, roomList, (SCREEN_WIDTH, SCREEN_HEIGHT)))
        GameBoard.update_player_sprites(screen, player, other_player)

        pygame.display.flip()
        clock.tick(30)

    return player

def main():

    n = Network()
    buttonLoc = []
    # this returns the player object with the initial position dictated by the server
    p1 = n.get_player()
    print('Connected to the server. Player ID: ', p1.id)

    p2 = n.send(p1) 
    print('Received other player data from server. Other Player ID: ', p2.id)
    running = True

    while True:
        # when we send our players data we get back the other player's data
        p2 = n.send(p1)
        # get player status after a game movement
        p1 = GamePlayLoop(p1, p2)

    sock.close()
    pygame.quit()


main()