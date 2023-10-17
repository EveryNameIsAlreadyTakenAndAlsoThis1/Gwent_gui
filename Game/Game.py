from Game.Board import Board
from Game.Player import Player
from Game.Card import Card
from Game.Deck import Deck
from Game.GameState import GameState
import numpy as np


class Game:
    """
    The `Game` class represents a game of Gwent.

    Attributes:
    -----------
        turn: int
            A value indicating whose turn it is. A value of 0 indicates that it is the first player's turn, and a value of 1 indicates that it is the second player's turn.
        all_cards: list
            A list of all available cards in the game.
        players: list
            A list containing two `Player` objects, representing the two players in the game.
        board: Board
            A `Board` object representing the game board.
        actions: list
            A list of actions that the current player can take in their turn.
        end: bool
            A boolean value indicating whether or not the game has ended.
        cards_by_id: dict
            A dictionary mapping card IDs to card objects.
        actions_index_by_id: dict
            A dictionary mapping actions by format of action  "<card_id>,<position>,<special_arg>".
    """

    def __init__(self, all_cards):
        """
        Initialize the game with a list of all cards available.
        Chooses deck for both players.

        Args:
            all_cards : list
                A list of all available cards.
        """

        self.turn = 0
        self.all_cards = all_cards
        self.game_state_matrix = GameState()
        self.game_state_matrix.starting_state(self.all_cards)
        self.cards_by_id = {}
        self.actions_index_by_id = {}
        for group in self.all_cards.values():
            for card in group:
                self.cards_by_id[card['Id']] = card
        self.players = [Player(0, self.create_deck(0, 2), self.game_state_matrix),
                        Player(1, self.create_deck(1, 2), self.game_state_matrix)]
        self.board = Board(self.players, self.game_state_matrix)
        self.starting_state()
        self.actions = self.create_actions()
        self.end = False

        self.starting_state = self.starting_state()

    def step(self, action):
        """
        This function performs a single step of the game, given an action to take.
        If one player passed their turn all next steps until the end of round will be played by the other player.

        Args:
            action (int): An index representing the action to take. This index corresponds to an element in the `actions` list.

        Returns:
            int: An integer value representing the outcome of the step. The possible values are:
                0: The step was successful and the turn is passed to the other player.
                1: Player in current turn won round.
                2: Opponent won round.
                3: The round ended in a tie.
                4: Player in current turn lost the game
                5: Player in current turn won the game
                6: The game ended in a tie.

        Raises:
            None
        """
        if self.actions[action] == '-1':
            # -1 is last action that is available until player takes this action
            self.players[self.turn].pass_game()
            # Both players passed end of round
            if self.players[self.turn].passed == True and self.players[self.turn ^ 1].passed == True:
                if self.board.player_strength[self.turn] > self.board.player_strength[self.turn ^ 1]:
                    # Player 0 wins round P1 take damage
                    self.players[self.turn ^ 1].take_damage()
                    self.players[self.turn].new_game()
                    self.players[self.turn ^ 1].new_game()
                    result = self.check_game_end()
                    if not result == 0:
                        return result
                    return 1
                elif self.board.player_strength[self.turn] < self.board.player_strength[self.turn ^ 1]:
                    # Player 1 wins round P0 take damage
                    self.players[self.turn].take_damage()
                    self.players[self.turn].new_game()
                    self.players[self.turn ^ 1].new_game()
                    result = self.check_game_end()
                    if not result == 0:
                        return result
                    return 2
                else:
                    # Tie both take damage
                    self.players[self.turn].take_damage()
                    self.players[self.turn ^ 1].take_damage()
                    self.players[self.turn].new_game()
                    self.players[self.turn ^ 1].new_game()
                    result = self.check_game_end()
                    if not result == 0:
                        return result
                    return 3
        else:
            # If action is other than pass find card in player's hand and set argument's than play card on board
            card_id = int(self.actions[action].split(',')[0])
            position = int(self.actions[action].split(',')[1])
            special_arg = int(self.actions[action].split(',')[2])
            card = self.players[self.turn].get_card_by_id(card_id)
            card.placement = position
            card.special_argument = special_arg
            self.board.place_card(card, self.turn)

        if not self.players[self.turn ^ 1].passed:
            self.turn = self.turn ^ 1
        return 0

    def game_state(self):
        """
        Creates a matrix 148x19 representing the current state of the game.
        The first dimension represents various elements, including the player's hand, graveyard,
        deck, and more. The second dimension represents card IDs, weather effects, player strength,
        and more.

        Returns:
            ndarray[int]:
                148x19 matrix representing the current state of the game.
        """

        state_row, state_col = self.board.get_state(self.turn)

        state_row = np.vstack((state_row, self.starting_state))

        state = np.hstack((state_row, state_col))

        compare = self.game_state_matrix.state_matrix_0
        if self.turn == 1:
            compare = self.game_state_matrix.state_matrix_1
        self.compare_matrices(state, compare)

        return state

    def create_deck(self, id, option):
        """
        Creates a deck for the specified option (1 for Northern Realms, 2 for Nilfgaard, 9 deck testing).

        The deck must contain at least 22 unit+hero cards, and no more than 10 hero cards.
        The total number of cards in the deck must not exceed 40, and there can be no more than 2 copies of any special card.

        Args:
            option (int): An integer indicating which faction to create the deck for. 1 for Northern Realms, 2 for Nilfgaard, 9 for Test deck.

        Returns:
            Deck: The created deck.
        """
        deck = Deck(id, self.game_state_matrix)

        # Northern Realms
        if option == 1:
            # List of card IDs for Northern Realms deck
            nr_card_ids = [0, 1, 2, 3, 4, 8, 14, 17, 17, 17, 24, 47, 48, 50, 52, 56, 58, 58, 60, 61, 62, 63, 61]

            # Add cards to deck
            for card_id in nr_card_ids:
                card = self.create_card(card_id)
                deck.add(card)

        # Nilfgaard
        elif option == 2:
            # List of card IDs for Nilfgaardian deck
            nilfgard_card_ids = [64, 65, 66, 67, 76, 77, 80, 84, 84, 85, 86, 87, 87, 88, 88, 88, 88, 91, 91, 47, 48, 52,
                                 56, 58, 58, 58, 60, 61, 62, 63]

            # Add cards to deck
            for card_id in nilfgard_card_ids:
                card = self.create_card(card_id)
                deck.add(card)

        # Testing deck
        elif option == 9:
            # List of card IDs for Nilfgaardian deck
            test_card_ids = [21, 21, 21, 19, 19, 24, 55, 55, 57, 57, 57, 57, 57, 57, 57, 58, 58, 59, 59, 50, 0, 1, 2, 3,
                             4, 8, 14, 17, 17, 17, 24, 47, 48, 50, 52, 56, 58, 58, 60, 61, 62, 63, 61]

            # Add cards to deck
            for card_id in test_card_ids:
                card = self.create_card(card_id)
                deck.add(card)

        return deck

    def get_card_data_by_id(self, id):
        """
        Get the data of a card by its ID.

        Args:
            id (int):
                The ID of the card.

        Returns:
            dict:
                A dictionary containing the data of the card.

        """
        return self.cards_by_id.get(id)

    def starting_state(self):
        """
        Initializes the starting state of the game by populating the `state` dictionary with information about every card.
        """

        # Starting state of game, information about every card

        state = np.zeros((4, 120))
        for group in self.all_cards.values():
            for card in group:
                state[0][card['Id']] = card['Strength']
                state[1][card['Id']] = self.transform(card['Type'])
                state[2][card['Id']] = self.transform(card['Ability'])
                state[3][card['Id']] = card['Placement']
        return state

    def transform(self, string):
        """
        Transforms a string into a corresponding numerical value.

        Args:
            string (str): The string to be transformed.

        Returns:
            int: The numerical value corresponding to the input string.

        """
        return {
            '0': 0,
            'Unit': 0,
            'Spy': 1,
            'Hero': 1,
            'Bond': 2,
            'Decoy': 2,
            'Morale': 3,
            'Medic': 4,
            'Scorch': 4,
            'Agile': 5,
            'Weather': 5,
            'Muster': 6,
        }.get(string, -1)

    def create_card(self, id_card):
        """
        Create a Card object with the specified information defined by id.

        Args:
            id_card (int):
                The unique identifier of the card to be created.

        Returns:
            Card:
                A Card object with the specified information.

        """
        card_data = self.get_card_data_by_id(id_card)
        return Card(
            name=card_data['Name'],
            ability=card_data['Ability'],
            strength=card_data['Strength'],
            id=int(card_data['Id']),
            type=card_data['Type'],
            placement=card_data['Placement'],
        )

    def create_actions(self):
        """
        Creates actions for all cards in the game.

        Returns:
            list:
                A list of actions as strings.
        """
        result = []  # Create an empty list to hold the resulting actions
        all_cards = []  # Create an empty list to hold all cards in the game

        # Loop through each card group in the game and add each card to the all_cards list
        for group, cards in self.all_cards.items():
            for card in cards:
                all_cards.append(card)

        # Loop through each card in the all_cards list and create actions for them
        for card in all_cards:
            special_arg = -1

            # If the card has the Decoy or Medic ability, create actions for it using all other units
            if card['Ability'] == 'Decoy' or card['Ability'] == 'Medic':
                if card['Ability'] == 'Medic':
                    # Action without revive
                    card_str = str(card['Id']) + ',' + str(card['Placement']) + ',' + str(special_arg)
                    result.append(card_str)
                for other_card in all_cards:
                    if other_card['Type'] == 'Unit':
                        if other_card['Faction'] == card['Faction'] or other_card['Ability'] == 'Spy' or card[
                            'Faction'] == 'Neutral' or other_card['Faction'] == 'Neutral':
                            if card['Type'] == 'Decoy':
                                result.append(
                                    str(card['Id']) + ',' + str(other_card['Placement']) + ',' + str(other_card['Id']))
                            else:
                                result.append(
                                    str(card['Id']) + ',' + str(card['Placement']) + ',' + str(other_card['Id']))
            elif card['Type'] == 'Morale':
                for i in range(3):
                    card_str = str(card['Id']) + ',' + str(i) + ',' + str(special_arg)
                    result.append(card_str)
            else:
                # Otherwise, create a simple action for the card with a default special_arg
                card_str = str(card['Id']) + ',' + str(card['Placement']) + ',' + str(special_arg)
                result.append(card_str)

        # Sort the resulting actions list by card_id, placement, and special_arg
        result = sorted(
            result,
            key=lambda x: (int(x.split(',')[0]), int(x.split(',')[1]), int(x.split(',')[2]))
        )

        # Add a pass action -1 to the end of the actions list
        result.append('-1')

        for index, action in enumerate(result):
            self.actions_index_by_id[action] = index

        return result

    def check_game_end(self):
        """
        Checks if the game has ended due to either player having zero or less lives.

        Returns:
            int:
                A code representing the reason for the game ending. The codes are:
                    - 0: Game has not ended
                    - 4: Current player has lost
                    - 5: Opponent player has lost
                    - 6: Both players have lost
        """

        # Check if the game ends due to a player running out of lives
        if self.players[self.turn].lives <= 0 and self.players[self.turn ^ 1].lives > 0:
            self.end = True
            return 4  # Current Player lost
        elif self.players[self.turn ^ 1].lives <= 0 and self.players[self.turn].lives > 0:
            self.end = True
            return 5  # Opponent Player lost
        elif self.players[self.turn].lives <= 0 and self.players[self.turn ^ 1].lives <= 0:
            self.end = True
            return 6  # Both players lost
        # Clear the game board
        self.board.end_game()
        return 0

    def valid_actions(self):
        """
        Generates a list of valid actions for the current player as a boolean array indicating which actions
        are valid along with list of actions.

        Returns:
            Tuple[List[bool], List[str]]:
                A tuple containing a boolean array indicating which actions are valid, and a list
                of valid actions.
        """
        # Create a list of zeros with the same length as the list of actions
        result = np.zeros(len(self.actions), dtype=bool).tolist()

        # Create an empty list to store only the valid actions
        valid_actions = []

        # Iterate through each card in the current player's hand
        for card in self.players[self.turn].hand:
            # Check if the card is not a Medic and not a Decoy
            if not card.ability == 'Medic' and not card.type == 'Decoy' and not card.type == 'Morale':
                # Generate a unique action ID for the card and get its index in the list of actions
                action_id = str(card.id) + ',' + str(card.placement) + ',' + str(card.special_argument)
                index = self.get_index_of_action(action_id)
                # Mark the corresponding element in the result list as True
                result[index] = True
                # Add the action ID to the list of valid actions
                valid_actions.append(action_id)

            # Check if the card is a Medic
            elif card.ability == 'Medic':
                # Action without revive
                action_no_revive = str(card.id) + ',' + str(card.placement) + ',' + str(-1)
                index = self.get_index_of_action(action_no_revive)
                result[index] = True
                valid_actions.append(action_no_revive)
                # Iterate through each card in the current player's graveyard
                for grave_card_list in self.board.graveyards[self.turn].cards.values():
                    # Check if the card in the graveyard is a Unit
                    if grave_card_list:
                        if grave_card_list[0].type == 'Unit':
                            # Generate a unique action ID for the Medic card and the graveyard card
                            action_id = str(card.id) + ',' + str(card.placement) + ',' + str(grave_card_list[0].id)
                            index = self.get_index_of_action(action_id)
                            # Mark the corresponding element in the result list as True
                            result[index] = True
                            # Add the action ID to the list of valid actions
                            valid_actions.append(action_id)

            # Check if the card is a Decoy
            elif card.type == 'Decoy':
                # Iterate through each row on the board that corresponds to the current player
                for i in range(3 * self.turn, 3 * self.turn + 3):
                    # Iterate through each card in the current row
                    for row_card_list in self.board.rows[i].cards.values():
                        # Generate a unique action ID for the Decoy card and the row card
                        if row_card_list and row_card_list[0].type == 'Unit':
                            action_id = str(card.id) + ',' + str(row_card_list[0].placement) + ',' + str(
                                row_card_list[0].id)
                            index = self.get_index_of_action(action_id)
                            # Mark the corresponding element in the result list as True
                            result[index] = True
                            # Add the action ID to the list of valid actions
                            valid_actions.append(action_id)
            elif card.type == 'Morale':
                for i in range(3):
                    action_id = str(card.id) + ',' + str(i) + ',' + str(card.special_argument)
                    index = self.get_index_of_action(action_id)
                    # Mark the corresponding element in the result list as True
                    result[index] = True
                    # Add the action ID to the list of valid actions
                    valid_actions.append(action_id)

        # Action for pass
        if not self.board.players[self.turn].passed:
            result[self.get_index_of_action('-1')] = True
            valid_actions.append('-1')
        # Return both the result list and the list of valid actions
        return result, valid_actions

    def get_index_of_action(self, action):
        """
        This function returns the index of the given action.

        Args:
            action (str):
                A string representing the action to search for. The string should be in the format "<card_id>,<position>,<special_arg>".

        Returns:
            int:
                An integer representing the index of the action in the list of actions.

        Raises:
            None
        """
        index = self.actions_index_by_id[action]
        return index

    def render_console_state(self):
        """
        This function transforms state of game based on created state from function game_state() and transforms it to colsole form.

        Returns:
            str:
                String representation of game state.

        Raises:
            None
        """
        state = self.game_state()

        out = 'Player ' + str(self.turn)
        out += '\nPlayer hand: '
        for i in range(120):
            if state[0][i] > 0:
                out += 'id: ' + str(i) + ' count: ' + str(state[0][i]) + ' '

        out += '\nPlayer meele: '
        for i in range(120):
            if state[1][i] > 0:
                out += 'id: ' + str(i) + ' count: ' + str(state[1][i]) + ' Current strength combined: ' + str(
                    state[2][i]) + ' '

        out += '\nPlayer ranged: '
        for i in range(120):
            if state[3][i] > 0:
                out += 'id: ' + str(i) + ' count: ' + str(state[3][i]) + ' Current strength combined: ' + str(
                    state[4][i]) + ' '

        out += '\nPlayer siege: '
        for i in range(120):
            if state[5][i] > 0:
                out += 'id: ' + str(i) + ' count: ' + str(state[5][i]) + ' Current strength combined: ' + str(
                    state[6][i]) + ' '

        out += '\nOpponent meele: '
        for i in range(120):
            if state[7][i] > 0:
                out += 'id: ' + str(i) + ' count: ' + str(state[7][i]) + ' Current strength combined: ' + str(
                    state[8][i]) + ' '

        out += '\nOpponent ranged: '
        for i in range(120):
            if state[9][i] > 0:
                out += 'id: ' + str(i) + ' count: ' + str(state[9][i]) + ' Current strength combined: ' + str(
                    state[10][i]) + ' '

        out += '\nOpponent siege: '
        for i in range(120):
            if state[11][i] > 0:
                out += 'id: ' + str(i) + ' count: ' + str(state[11][i]) + ' Current strength combined: ' + str(
                    state[12][i]) + ' '

        out += '\nPlayer graveyard: '
        for i in range(120):
            if state[13][i] > 0:
                out += 'id: ' + str(i) + ' count: ' + str(state[13][i]) + ' '

        out += '\nOpponent graveyard: '
        for i in range(120):
            if state[14][i] > 0:
                out += 'id: ' + str(i) + ' count: ' + str(state[14][i]) + ' '

        out += '\nPlayer deck:'
        for i in range(120):
            if state[15][i] > 0:
                out += 'id: ' + str(i) + ' count: ' + str(state[15][i]) + ' '

        out += '\nWeather: '
        for i in range(3):
            out += str(state[0][120 + i]) + ' '

        out += '\nLives player: '
        out += str(state[0][123])
        out += '\nLives opponent: '
        out += str(state[0][124])
        out += '\nCard count player: '
        out += str(state[0][125])
        out += '\nCard count opponent: '
        out += str(state[0][126])
        out += '\nAdditive modificator player meele: '
        out += str(state[0][127])
        out += '\nAdditive modificator player ranged: '
        out += str(state[0][128])
        out += '\nAdditive modificator player siege: '
        out += str(state[0][129])
        out += '\nAdditive modificator opponent meele: '
        out += str(state[0][130])
        out += '\nAdditive modificator opponent ranged: '
        out += str(state[0][131])
        out += '\nAdditive modificator opponent siege: '
        out += str(state[0][132])
        out += '\nMultiplicative modificator player meele: '
        out += str(state[0][133])
        out += '\nMultiplicative modificator player ranged: '
        out += str(state[0][134])
        out += '\nMultiplicative modificator player siege: '
        out += str(state[0][135])
        out += '\nMultiplicative modificator opponent meele: '
        out += str(state[0][136])
        out += '\nMultiplicative modificator opponent ranged: '
        out += str(state[0][137])
        out += '\nMultiplicative modificator opponent siege: '
        out += str(state[0][138])
        out += '\nScore row meele player: '
        out += str(state[0][139])
        out += '\nScore row ranged player: '
        out += str(state[0][140])
        out += '\nScore row siege player: '
        out += str(state[0][141])
        out += '\nScore row meele opponent: '
        out += str(state[0][142])
        out += '\nScore row ranged opponent: '
        out += str(state[0][143])
        out += '\nScore row siege opponent: '
        out += str(state[0][144])
        out += '\nScore player: '
        out += str(state[0][145])
        out += '\nScore opponent: '
        out += str(state[0][146])
        out += '\nPassed opponent: '
        out += str(state[0][147])
        out += '\nActions: '

        valid_actions_bool, valid_actions_list = self.valid_actions()

        for action in valid_actions_list:
            out += action + ' '
        out += '\n'

        return out

    def compare_matrices(self, matrix1, matrix2):
        if matrix1.shape != matrix2.shape:
            print("Matrices have different shapes.")
            return

        comparison = matrix1 == matrix2
        if comparison.all():
            print("Matrices are identical.")
        else:
            diff_positions = np.where(comparison == False)
            for row, col in zip(diff_positions[0], diff_positions[1]):
                val1 = matrix1[row, col]
                val2 = matrix2[row, col]
                print(f"Difference at position ({row}, {col}):")
                print(f"Matrix 1 value: {val1}")
                print(f"Matrix 2 value: {val2}")

    def give_card(self, player_id, card_id):
        self.players[player_id].add_card(self.create_card(card_id))
