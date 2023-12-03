import pygame
import socket
import threading
import Deck
from network import Network
from pygame.locals import QUIT
from random import randrange

from Player import Player, PlayerState
from GameBoard import GameBoard

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Clue-less - Client')
clock = pygame.time.Clock()


def GamePlayLoop(player:Player, otherPlayers:list):
    """ Main game loop

    This function runs the main game loop for Clue-Less. It takes a Player object
    representing the current player and a dictionary of Player objects representing
    the other players in the game. It returns the updated Player object after the
    loop has completed.

    :param player: The current player object
    :type player: Player
    :param otherPlayers: A dictionary of Player objects representing the other players
    :type otherPlayers: list of other Player objects

    :return: The updated Player object
    :rtype: Player
    """

    # Build the game board and handle quit events
    gameboard = GameBoard(screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
    gameboard.BuildGameBoard(otherPlayers, player.id)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            return None

    # Loop for guessing, responding to guesses, and accusing
    while(player.state in [PlayerState.GUESSING,
                           PlayerState.RESPONDING_TO_GUESS,
                           PlayerState.ACCUSING]):
        # Build the game board and handle quit events
        gameboard.BuildGameBoard(otherPlayers, player.id)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                player = gameboard.ClickScreen(mouse, player)
        otherPlayers[player.id] = player

    # Loop for moving
    while player.state == PlayerState.MOVING:
        # Move player and manage active state
        pygame.event.pump()
        player.MakeMove(gameboard.GetValidMoves(otherPlayers, player.id))

        # Build the game board
        gameboard.BuildGameBoard(otherPlayers, player.id)
        
    # Handle waiting state
    if player.state == PlayerState.WAITING:
        print("Waiting for other players to make their moves...")
        # Check if player can move based on guess
        for otherPlayer in otherPlayers:
            if otherPlayer.state == PlayerState.AWAITING_GUESS_RESPONSE:
                suspectGuessed = otherPlayer.guessingCards[Deck.ClueType.SUSPECT]
                if suspectGuessed.name == player.name:
                    player.loc = otherPlayer.loc
                    player.movedByGuess = True

        # Check if previous player is still waiting for guess response
        playerIdBefore = GetIdBefore(player.id, otherPlayers)
        playerBefore = otherPlayers[playerIdBefore]
        while(playerBefore.state == PlayerState.NO_GUESS_RESPONSE and\
              playerIdBefore != player.id):
            playerIdBefore = GetIdBefore(playerIdBefore, otherPlayers)
            playerBefore = otherPlayers[playerIdBefore]

        # Check if player can respond to guess
        if player.state == PlayerState.WAITING and\
           playerBefore.state == PlayerState.AWAITING_GUESS_RESPONSE:
            canRespToGuess = False
            for cardType in playerBefore.guessingCards:
                guessedCard = playerBefore.guessingCards[cardType]
                if player.dealtCards.IsCardInDeck(guessedCard):
                    canRespToGuess = True
                    break
            if canRespToGuess:
                player.state = PlayerState.RESPONDING_TO_GUESS
            else:
                player.state = PlayerState.NO_GUESS_RESPONSE

    # Handle guess response state
    if player.state == PlayerState.AWAITING_GUESS_RESPONSE:
        print("Waiting for other players to respond to guess...")
        for otherPlayer in otherPlayers:
            if otherPlayer.state == PlayerState.GUESS_RESPONSE_SENT:
                player.knownCards.AddCard(otherPlayer.guessResponse.cards[0])
                player.state = PlayerState.TURN_OVER
                break
    
    # Handle guess response received state
    if player.state in [PlayerState.GUESS_RESPONSE_SENT, PlayerState.NO_GUESS_RESPONSE]:
        guessResponseReceived = True
        for otherPlayer in otherPlayers:
            if otherPlayer.state == PlayerState.AWAITING_GUESS_RESPONSE:
                guessResponseReceived = False
        if guessResponseReceived:
            player.guessResponse = Deck.Deck()
            player.state = PlayerState.WAITING

    # Handle turn over state
    playerIdBefore = GetIdBefore(player.id, otherPlayers)
    playerBefore = otherPlayers[playerIdBefore]
    
    if player.state == PlayerState.WAITING and\
       playerBefore.state == PlayerState.TURN_OVER:
           player.state = PlayerState.MOVING

    # Handle waiting state again
    if player.state == PlayerState.TURN_OVER:
        for otherPlayer in otherPlayers:
            if otherPlayer.state in [PlayerState.MOVING, PlayerState.GUESSING, PlayerState.AWAITING_GUESS_RESPONSE]:
                player.state == PlayerState.WAITING
                break

    return player

def GetIdBefore(id, otherPlayers:list):
    # Count how many players are owned by clients Player.isOwned == True
    ownedPlayerCount = 0
    for i in range(len(otherPlayers)):
        if otherPlayers[i].isOwned:
            ownedPlayerCount += 1
    if ownedPlayerCount <3:
        ownedPlayerCount = 3

    if id == 0:
        print('Player ID is {}. Returning {}'.format(id, ownedPlayerCount - 1))
        return ownedPlayerCount - 1
    
    print('Player ID is {}. Returning {}'.format(id, id - 1))
    return id - 1

def main():
    n = Network()
    # this returns the player object with the initial position dictated by the server
    player = n.get_player()
    print('Connected to the server. Player ID: ', player.id)

    allPlayers = n.send(player)
    # print('Received other player data from server. Other Player ID: ', p2.id)
    running = True

    player.dealtCards.Print()
    while running:
        # when we send our players data we get back the other player's data and the current active player
        allPlayers = n.send(player) 
        player = GamePlayLoop(player, allPlayers)

        if player is None:
            running = False

main()