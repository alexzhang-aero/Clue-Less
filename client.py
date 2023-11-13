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
SCREEN_HEIGHT = 1200

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Clue-less - Client')
clock = pygame.time.Clock()


def GamePlayLoop(player:Player, otherPlayers):
    """ Main game loop

    other_player: Player dict representing the other player
    This other_player object should be updated to an array of Player objects
    in the future to support 6 players.
    """

    gameboard = GameBoard(screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
    gameboard.BuildGameBoard(otherPlayers, player.id)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            return None

    while(player.state in [PlayerState.GUESSING,
                           PlayerState.RESPONDING_TO_GUESS,
                           PlayerState.ACCUSING]):
        gameboard.BuildGameBoard(otherPlayers, player.id)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                player = gameboard.ClickScreen(mouse, player)
        otherPlayers[player.id] = player

    while player.state == PlayerState.MOVING:
        # move player and manage active state
        pygame.event.pump()
        player.MakeMove(gameboard.GetValidMoves(otherPlayers, player.id))

        gameboard.BuildGameBoard(otherPlayers, player.id)
        
    if player.state == PlayerState.WAITING:
        for otherPlayer in otherPlayers:
            if otherPlayer.state == PlayerState.AWAITING_GUESS_RESPONSE:
                suspectGuessed = otherPlayer.guessingCards[Deck.ClueType.SUSPECT]
                if suspectGuessed.name == player.name:
                    player.loc = otherPlayer.loc
                    player.movedByGuess = True

    playerIdBefore = GetIdBefore(player.id, len(otherPlayers))
    playerBefore = otherPlayers[playerIdBefore]
    while(playerBefore.state == PlayerState.NO_GUESS_RESPONSE and\
          playerIdBefore != player.id):
        playerIdBefore = GetIdBefore(playerIdBefore, len(otherPlayers))
        playerBefore = otherPlayers[playerIdBefore]

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

    if player.state == PlayerState.AWAITING_GUESS_RESPONSE:
        for otherPlayer in otherPlayers:
            if otherPlayer.state == PlayerState.GUESS_RESPONSE_SENT:
                player.knownCards.AddCard(otherPlayer.guessResponse.cards[0])
                player.state = PlayerState.TURN_OVER
                break
    
    if player.state in [PlayerState.GUESS_RESPONSE_SENT, PlayerState.NO_GUESS_RESPONSE]:
        guessResponseReceived = True
        for otherPlayer in otherPlayers:
            if otherPlayer.state == PlayerState.AWAITING_GUESS_RESPONSE:
                guessResponseReceived = False
        if guessResponseReceived:
            player.guessResponse = Deck.Deck()
            player.state = PlayerState.WAITING

    playerIdBefore = GetIdBefore(player.id, len(otherPlayers))
    playerBefore = otherPlayers[playerIdBefore]
    
    if player.state == PlayerState.WAITING and\
       playerBefore.state == PlayerState.TURN_OVER:
           player.state = PlayerState.MOVING

    if player.state == PlayerState.TURN_OVER:
        for otherPlayer in otherPlayers:
            if otherPlayer.state in [PlayerState.MOVING, PlayerState.GUESSING, PlayerState.AWAITING_GUESS_RESPONSE]:
                player.state == PlayerState.WAITING

    return player

def GetIdBefore(id, playerCount):
    if id == 0:
        return playerCount - 1
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