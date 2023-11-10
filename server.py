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
from Player import Player
from Deck import DealCards

server = "127.0.0.1"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)


s.listen(2)
print("Waiting for a connection, Server Started")

murderEnvelope, cardPiles = DealCards(2)
p1 = Player([450, 450], cardPiles[0], id=0, activePlayer=0)
p2 = Player([500, 450], cardPiles[1], id=1, activePlayer=0)


players = [p1,p2]

def threaded_client(conn, player:int):
    playerWaitingForTurnCompletion = 0

    conn.send(pickle.dumps(players[player]))
    other_player_data = ""
    while True:
        try:
            data_received = conn.recv(2048)
            if data_received:

                data = pickle.loads(data_received)
                players[player] = data
                
                other_player_data = players[0] if player == 1 else players[1]
                    
                # check if the players have changed turns
                if players[player].activePlayer!=playerWaitingForTurnCompletion:
                    playerWaitingForTurnCompletion = other_player_data.id
                    other_player_data.activePlayer = playerWaitingForTurnCompletion

                print("Received: ", print(data))
                print("Sending : ", print(other_player_data))

                conn.sendall(pickle.dumps(other_player_data))
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