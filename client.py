import pygame
import socket
import threading
from network import Network
from pygame.locals import QUIT
from random import randrange

from Player import Player
from GameBoard import GameBoard

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
    playerRolled = False

    gameboard = GameBoard(screen)
    gameboard.build_game_board(player.movesRemaining)
    gameboard.update_player_sprites(player, other_player)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            # return False

        if player.activePlayer==player.id and event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            if gameboard.collide((mouse[0], mouse[1]), 0, 300, 900, 1000):
                print('Rolling dice...')
                player.set_moves_remaining(randrange(1, 6))
                gameboard.build_game_board(player.movesRemaining)
                playerRolled = True

        while player.activePlayer==player.id and playerRolled:
            pygame.event.pump()
            # move player and manage active state
            player.update(gameboard.get_valid_moves(player.loc, (SCREEN_WIDTH, SCREEN_HEIGHT)))
            
            gameboard.build_game_board(player.movesRemaining)
            gameboard.update_player_sprites(player, other_player)
            clock.tick(30)

        print("player ",player.id, " finished turn")
        playerRolled = False

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
        if p2.activePlayer == p1.id:
            print("Your turn")
            p1.activePlayer = p1.id
        # get player status after a game movement
        p1 = GamePlayLoop(p1, p2)




main()