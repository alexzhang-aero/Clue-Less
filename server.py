"""
This script should listen for new connections and start a new thread for each one.
It must give new players their initial states and player number
It must tell players who's turn it is
It must receive and update player positions.
"""

import socket
from _thread import *
import sys
import pickle
from Player import Player, PlayerState
from Deck import DealCards, ClueType, Deck

server = "127.0.0.1"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

player_count = 3

try:
    s.bind((server, port))
except socket.error as e:
    str(e)


s.listen(2)
print("Waiting for a connection, Server Started")

murderEnvelope, cardPiles = DealCards(player_count)
# Fill cardPiles with empty decks until it's length is 6
while len(cardPiles) < 6:
    # Dont deal to non-player decks
    cardPiles.append(Deck())

players = [Player([3, 0], cardPiles[0], id=0, name='Dwarf'),
           Player([0, 1], cardPiles[1], id=1, name='Knight'),
           Player([4, 1], cardPiles[2], id=2, name='Princess'),
           Player([0, 3], cardPiles[3], id=3, name='Vampire'),
           Player([1, 4], cardPiles[4], id=4, name='Witch'),
           Player([3, 4], cardPiles[5], id=5, name='Wizard')]


print(murderEnvelope[ClueType.ROOM].name)
print(murderEnvelope[ClueType.WEAPON].name)
print(murderEnvelope[ClueType.SUSPECT].name)

def threaded_client(conn, playerId:int):

    if playerId == 0:
        players[playerId].state = PlayerState.MOVING

    players[playerId].isOwned = True
    
    conn.send(pickle.dumps(players[playerId]))
    while True:
        try:
            dataReceived = conn.recv(8192)
            if dataReceived:
                playerReceived = pickle.loads(dataReceived)
                
                if playerReceived.state == PlayerState.ACCUSED:
                    if murderEnvelope[ClueType.ROOM].equals(playerReceived.guessingCards[ClueType.ROOM]) and\
                       murderEnvelope[ClueType.WEAPON].equals(playerReceived.guessingCards[ClueType.WEAPON]) and\
                       murderEnvelope[ClueType.SUSPECT].equals(playerReceived.guessingCards[ClueType.SUSPECT]):
                        for player in players:
                            player.state = PlayerState.LOSER
                        playerReceived.state = PlayerState.WINNER
                    else:
                        playerReceived.state = PlayerState.OUT

                players[playerReceived.id] = playerReceived


                print("Received: ", print(playerReceived))
                print("Sending : ", print(players))

                conn.sendall(pickle.dumps(players))
            else:
                print("No data received")
                break
        except EOFError as e:
            print ("End of file error: ", str(e))
            break
        except Exception as e:
            print ("General exception", str(e))
            break
        

    print("Lost connection")
    conn.close()


currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
