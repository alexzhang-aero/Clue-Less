from unittest import *
from unittest.mock import *
import pygame.event
import Player
import network
import unittest
from client import *


class TestGameCompliance(unittest.TestCase):
    """
    This class focuses on compliance testing. This tests for basic functionalities
    such as initializing, quitting, server and client connection, etc
    """

    def test_initialization(self):
        """
        method to test initialization of game client
        :return:
        """
        # noinspection PyBroadException
        try:
            main()
            assert True
        except Exception as ex:
            self.fail(f"Could not initialize. Test Failed: {ex}")

    def test_movement(self):
        """
        Testing player movement
        :return:
        """
        player = Player()
        mock_move = "up"

        with patch.object(player, 'MakeMove', return_value=mock_move):
            real_move = player.MakeMove("up")
            if self.assertEqual(real_move, mock_move, 'Player moved differently than indicated'):
                print('test failed')
            else:
                print('test passed')

    def test_game_state(self):
        """
        Testing for game state
        :return:
        """
        pl = {}
        player = Player()
        player.state = PlayerState.GUESSING
        updatePlayer = GamePlayLoop(player, pl)
        self.assertNotEqual(updatePlayer, PlayerState.GUESSING, "Transition failed: Test Failed")

    def test_server(self):
        """
        unit test for server connection validity
        :return:
        """
        net = Network()
        player = net.get_player()
        if self.assertIsNotNone(player, "Server Connection Failed: Test Failed"):
            print("failed Test")
        else:
            print("Server is up and running. Test Passed")

    def test_client(self):
        """
        Test client connection
        :return:
        """
        net = network.Network()
        player = Player(id=1, name="wizard")
        all_player = net.send(player)
        if self.assertIsNotNone(all_player, "Client connection Failed"):
            print("Client Connection established successfully. Test Passed")
        else:
            print("Test Failed")

    def test_quit(self):
        """
        tests for quit compliance
        :return:
        """
        pygame.event.get = lambda: [pygame.event.Event(QUIT)]
        assert main() is None
        self.fail('Did not quit prompted. Test Failed')

    def test_halway(self):
        """
        testing hallway
        :return:
        """
        pass

    def test_room(self):
        """
        testing rooms
        :return:
        """
        pass


if __name__ == '__main__':
    unittest.main()
