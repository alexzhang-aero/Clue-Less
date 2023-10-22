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
conn,addr= None,None
 
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind((HOST,PORT))
sock.listen(2)

turn=True

def create_thread(target):
    thread=threading.Thread(target=target)
    thread.daemon=True
    thread.start()

def wait_connect():
    global connection_established,conn,addr
    conn,addr=sock.accept()
    print('[client connected]')
    connection_established=True
    receive_data()

def receive_data():
    global turn, connection_established, player

    while True:
        if not turn:
            # Wait for data from the other player
            data = conn.recv(1024).decode()
            data = data.split('-')

            if data[3] == 'Yourturn':
                turn = True  

        else:
            # If it's this player's turn, break from the loop and return to the game.
            break

# Modified GamePlayLoop to incorporate turn-based logic and network communication.
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
                    player.movesRemaining = randrange(1,6)
                    turn = False  # End the player's turn after rolling the dice.

                    # Send the player's move to the opponent.
                    move_data = f"{player.rect.x}-{player.rect.y}-{player.movesRemaining}-Yourturn-{'True'}"
                    conn.send(move_data.encode())

        # Player Movement
        if turn:
            player.update(pygame.key.get_pressed(), GameBoard.GetValidMoves(player.loc, roomList, (SCREEN_WIDTH, SCREEN_HEIGHT)))
            screen.blit(player.surf, player.rect)

        pygame.display.flip()
        clock.tick(30)

        if not turn:
            if not receive_data():  # Wait for the opponent's move if it's their turn.
                break

    return True

create_thread(wait_connect)

screen=pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Clue-less - Host')
player = Player([450, 450], None, None, None)
roomList = GameBoard.CreateRooms()
buttonLoc = []

running=True

while running:
    running = GamePlayLoop()

pygame.quit()