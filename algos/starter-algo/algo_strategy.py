import gamelib
import random
import math
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replcement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('STARTING...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]


    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.AdvancedGameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algorithm strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safey be replaced for your custom algo.
    """
    def starter_strategy(self, game_state):

        self.build_initial_defense(game_state)

        side = self.get_attacked_locations(game_state)

        if side == "left":
            self.fortify_channel_left(game_state)
        elif side == "right":
            self.fortify_channel_right(game_state)
        else:
            self.fortify_channel_left(game_state)
            self.fortify_channel_right(game_state)

        self.fortify_defenses(game_state)

        self.add_defenses(game_state)

        self.attack(game_state, side)

    def build_initial_defense(self, game_state):
        firewall_locations = [[x, 13] for x in range(4, 24)]
        firewall_locations += [[0, 13], [1, 13], [26, 13], [27, 13]]
        for location in firewall_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

    def fortify_channel_left(self, game_state):
        firewall_locations = [[2, 12], [3, 11], [4, 10]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
        encryptor_locations = [[1, 12], [2, 11], [3, 10]]
        for location in encryptor_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)

    def fortify_channel_right(self, game_state):
        firewall_locations = [[25, 12], [24, 11], [23, 10]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
        encryptor_locations = [[26, 12], [25, 11], [24, 10]]
        for location in encryptor_locations:
            if game_state.can_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)

    def fortify_defenses(self, game_state):
        firewall_locations = [[x, 12] for x in range(4, 26, 3)]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

    def add_defenses(self, game_state):
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT) \
                         + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT)
        friendly_edges.remove([4, 9])
        friendly_edges.remove([5, 8])
        for location in friendly_edges:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

    def attack(self, game_state, side):
        if side == "left":
            location = [23, 9]
        elif side == "right":
            location = [4, 9]
        else:
            location = [4, 9]
        half_currency = math.floor(game_state.get_resource(game_state.BITS))
        gamelib.debug_write(half_currency)
        if game_state.can_spawn(EMP, location, half_currency):
                game_state.attempt_spawn(EMP, location, half_currency)

    def get_attacked_locations(self, game_state):
        one_l = game_state.get_attackers([0, 13], 0)
        two_l = game_state.get_attackers([1, 13], 0)
        three_l = game_state.get_attackers([2, 13], 0)
        four_l = game_state.get_attackers([3, 13], 0)
        left = len(one_l) + len(two_l) + len(three_l) + len(four_l)

        one_r = game_state.get_attackers([27, 13], 0)
        two_r = game_state.get_attackers([26, 13], 0)
        three_r = game_state.get_attackers([25, 13], 0)
        four_r = game_state.get_attackers([24, 13], 0)
        right = len(one_r) + len(two_r) + len(three_r) + len(four_r)
        if left > right:
            return "left"
        elif right > left:
            return "right"
        else:
            return "equal"

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
