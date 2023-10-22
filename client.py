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


turn = False

def GamePlayLoop(player:dict, other_player: dict):
    """ Main game loop
    
    other_player: Player dict representing the other player
    This other_player object should be updated to an array of Player objects
    in the future to support 6 players.
    """
    global turn
    roomList = GameBoard.CreateRooms()
    
    # while True:
    GameBoard.BuildGameBoard(screen, roomList, player.movesRemaining)

    for event in pygame.event.get():
        if event.type == QUIT:
            return False

        if turn and event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            if GameBoard.Collide((mouse[0], mouse[1]), 0, 300, 900, 1000):
                player.movesRemaining = randrange(1, 6)
                turn = False

                move_data = f"{player.rect.x}-{player.rect.y}-{player.movesRemaining}-Yourturn-{'True'}"
                # sock.send(move_data.encode())

    if turn:
        player.update(pygame.key.get_pressed(), GameBoard.GetValidMoves(player.loc, roomList, (SCREEN_WIDTH, SCREEN_HEIGHT)))
        screen.blit(player.surf, player.rect)

    pygame.display.flip()
    clock.tick(30)

    return player



def main():

    n = Network()
    buttonLoc = []
    # this returns the player object with the initial position dictated by the server
    player_data = n.get_player()
    p1 = Player(player_data['loc'], player_data['weaponIn'], player_data['suspectIn'], player_data['roomIn'])
    
    other_player_data = n.send(player_data) 
    p2 = Player(other_player_data['loc'], other_player_data['weaponIn'], other_player_data['suspectIn'], other_player_data['roomIn'])
    
    running = True

    while True:
        # when we send our players data we get back the other player's data
        other_player_data = n.send(p1.data)

        #update other player poz
        p2.move(other_player_data['loc'])

        # get player status after a game movement
        p1 = GamePlayLoop(p1, p2)

    sock.close()
    pygame.quit()


main()