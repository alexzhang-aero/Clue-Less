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

server = "192.168.1.202"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)


s.listen(2)
print("Waiting for a connection, Server Started")


p1 = {"loc": [450, 450], "weaponIn": None, "suspectIn": None, "roomIn": None}
p2 = {"loc": [475, 475], "weaponIn": None, "suspectIn": None, "roomIn": None}

players = [p1,p2]


def threaded_client(conn, player:int):
    conn.send(pickle.dumps(players[player]))
    other_player_data = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            players[player] = data

            if not data:
                print("Disconnected")
                break
            else:
                other_player_data = players[0] if player == 1 else players[1]

                print("Received: ", data)
                print("Sending : ", other_player_data)

            conn.sendall(pickle.dumps(other_player_data))
        except:
            break

    print("Lost connection")
    conn.close()


currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1