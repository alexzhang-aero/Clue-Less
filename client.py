import pygame
import socket
import threading

from pygame.locals import QUIT
from random import randrange

from Player import Player
import GameBoard

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

pygame.init()
clock = pygame.time.Clock()

HOST = '127.0.0.1'
PORT = 9009
connection_established = False

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

turn = False

try:
    sock.connect((HOST, PORT))
    connection_established = True
except Exception as e:
    print("Failed to connect to server:", e)
    pygame.quit()
    exit()

def receive_data():
    global turn, connection_established, player

    while True:
        if not turn:
            data = sock.recv(1024).decode()
            data = data.split('-')
            
            if data[3] == 'Yourturn':
                turn = True

        else:
            break

def GamePlayLoop():
    global turn

    while True:
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
                    sock.send(move_data.encode())

        if turn:
            player.update(pygame.key.get_pressed(), GameBoard.GetValidMoves(player.loc, roomList, (SCREEN_WIDTH, SCREEN_HEIGHT)))
            screen.blit(player.surf, player.rect)

        pygame.display.flip()
        clock.tick(30)

        if not turn:
            receive_data()

    return True


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Clue-less - Client')
player = Player([450, 450], None, None, None)
roomList = GameBoard.CreateRooms()
buttonLoc = []

running = True

while running:
    running = GamePlayLoop()

sock.close()
pygame.quit()
