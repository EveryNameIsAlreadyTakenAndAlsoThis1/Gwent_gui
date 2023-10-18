import random

import numpy as np


def transform(string):
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


class Game:
    """
    The `Game` class represents a game of Gwent.

    Attributes:
    -----------
        turn: int
            A value indicating whose turn it is. A value of 0 indicates that it is the first player's turn,
            and a value of 1 indicates that it is the second player's turn.
        all_cards: list
            A list of all available cards in the game.
        players: list
            A list containing two `Player` objects, representing the two players in the game.
        board: Board
            A `Board` object representing the game board.
        actions: list
            A list of actions that the current player can take in their turn.
        end: bool
            A boolean value indicating whether the game has ended.
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
            action (int): An index representing the action to take. This index corresponds to an element in the
            `actions` list.

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
            if self.players[self.turn].passed and self.players[self.turn ^ 1].passed:
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

        state = self.game_state_matrix.state_matrix_0
        if self.turn == 1:
            state = self.game_state_matrix.state_matrix_1

        return state

    def create_deck(self, _id, option):
        """
        Creates a deck for the specified option (1 for Northern Realms, 2 for Nilfgaard, 9 deck testing).

        The deck must contain at least 22 unit+hero cards, and no more than 10 hero cards.
        The total number of cards in the deck must not exceed 40, and there can be no more than 2 copies of any
        special card.

        Args:
            _id (int): Id of a deck
            option (int): An integer indicating which faction to create the deck for. 1 for Northern Realms,
            2 for Nilfgaard, 9 for Test deck.

        Returns:
            Deck: The created deck.
        """
        deck = Deck(_id, self.game_state_matrix)

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
            nilfgaard_card_ids = [64, 65, 66, 67, 76, 77, 80, 84, 84, 85, 86, 87, 87, 88, 88, 88, 88, 91, 91, 47, 48,
                                  52,
                                  56, 58, 58, 58, 60, 61, 62, 63]

            # Add cards to deck
            for card_id in nilfgaard_card_ids:
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

    def get_card_data_by_id(self, _id):
        """
        Get the data of a card by its ID.

        Args:
            _id (int):
                The ID of the card.

        Returns:
            dict:
                A dictionary containing the data of the card.

        """
        return self.cards_by_id.get(_id)

    def starting_state(self):
        """
        Initializes the starting state of the game by populating the `state` dictionary with information about every
        card.
        """

        # Starting state of game, information about every card

        state = np.zeros((4, 120))
        for group in self.all_cards.values():
            for card in group:
                state[0][card['Id']] = card['Strength']
                state[1][card['Id']] = transform(card['Type'])
                state[2][card['Id']] = transform(card['Ability'])
                state[3][card['Id']] = card['Placement']
        return state

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
            _id=int(card_data['Id']),
            _type=card_data['Type'],
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

            # If the card has the Decoy or Medic ability, create actions for it using all others units
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
        Checks if the game has ended due to either player having zero or fewer lives.

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
        result = [False for _ in range(len(self.actions))]
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
                A string representing the action to search for. The string should be in the format "<card_id>,
                <position>,<special_arg>".

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
        This function transforms state of game based on created state from function game_state() and transforms it to
        console form.

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

        out += '\nPlayer melee: '
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

        out += '\nOpponent melee: '
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
        out += '\nAdditive modifier player melee: '
        out += str(state[0][127])
        out += '\nAdditive modifier player ranged: '
        out += str(state[0][128])
        out += '\nAdditive modifier player siege: '
        out += str(state[0][129])
        out += '\nAdditive modifier opponent melee: '
        out += str(state[0][130])
        out += '\nAdditive modifier opponent ranged: '
        out += str(state[0][131])
        out += '\nAdditive modifier opponent siege: '
        out += str(state[0][132])
        out += '\nMultiplicative modifier player melee: '
        out += str(state[0][133])
        out += '\nMultiplicative modifier player ranged: '
        out += str(state[0][134])
        out += '\nMultiplicative modifier player siege: '
        out += str(state[0][135])
        out += '\nMultiplicative modifier opponent melee: '
        out += str(state[0][136])
        out += '\nMultiplicative modifier opponent ranged: '
        out += str(state[0][137])
        out += '\nMultiplicative modifier opponent siege: '
        out += str(state[0][138])
        out += '\nScore row melee player: '
        out += str(state[0][139])
        out += '\nScore row ranged player: '
        out += str(state[0][140])
        out += '\nScore row siege player: '
        out += str(state[0][141])
        out += '\nScore row melee opponent: '
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

    def give_card(self, player_id, card_id):
        self.players[player_id].add_card(self.create_card(card_id))


class Board:
    """
    A class representing the game board.

    Attributes:
    -----------
        rows (list[Row]):
            A list of 6 Rows representing each row on the board.
        graveyards (list):
            A list of 2 empty lists representing the graveyards for each player.
        players (list):
            A list of 2 player objects.
        player_strength (list):
            A list with value of player's combined rows.
    """

    def __init__(self, players, game_state_matrix):
        """
        Initializes a Board instance with empty rows and empty graveyards.

        Args:
            players (list):
                A list of 2 player objects representing the players in the game.

        Returns:
            None.
        """
        self.game_state_matrix = game_state_matrix
        self.rows = [Row(0, self.game_state_matrix), Row(1, self.game_state_matrix), Row(2, self.game_state_matrix),
                     Row(3, self.game_state_matrix), Row(4, self.game_state_matrix), Row(5, self.game_state_matrix)]
        self.graveyards = [Graveyard(0, self.game_state_matrix), Graveyard(1, self.game_state_matrix)]
        self.players = players
        self.player_strength = [0, 0]

    def place_card(self, card, turn):
        """
        Places a card on the board and applies its ability if it has one.

        Args:
            card (Card):
                The card to be placed.
            turn (int):
                The index of the player who is placing the card (0 or 1).

        Returns:
            bool:
                True if the card was successfully placed, False otherwise.
        """
        placement = card.placement
        # Turn 0 - player 0, turn 1 - player 1
        row_index = card.placement + (3 * turn)

        # Check if the card's ability is "Weather"
        if card.ability == "Weather":
            if card.placement < 3:
                self.rows[card.placement].activate_weather()
                self.rows[card.placement + 3].activate_weather()
            else:
                for row in self.rows:
                    row.clear_weather()
            self.calculate_strength()
            return True

        # Check if the card's ability is "Spy"
        elif card.ability == "Spy":
            # Change the placement as if the turn was opposite to current turn
            if turn == 0:
                row_index = placement + 3
            elif turn == 1:
                row_index = placement
            # Player draws 2 cards if Spy is played
            self.players[turn].draw()
            self.players[turn].draw()
            self.rows[row_index].add_card(card)
            self.calculate_strength()
            return True

        # Check if the card's ability is "Bond"
        elif card.ability == "Bond":
            self.rows[row_index].add_card(card)
            self.calculate_strength()
            return True

        # Check if the card's ability is "Morale"
        elif card.ability == "Morale":
            self.rows[row_index].add_card(card)
            self.calculate_strength()
            return True

        # Check if the card's ability is "Scorch"
        elif card.ability == "Scorch":
            highest = -1
            to_remove = []
            for row in self.rows:
                if row.highest_value_non_hero > highest:
                    highest = row.highest_value_non_hero
            for row in self.rows:
                if row.highest_value_non_hero == highest:
                    to_remove.append(row)

            for row in to_remove:
                cards = row.remove_highest_value_cards()
                index = self.rows.index(row)
                if index < 3:
                    self.graveyards[0].add_cards(cards)
                else:
                    self.graveyards[1].add_cards(cards)
            if card.placement < 3:
                self.rows[row_index].add_card(card)
            self.calculate_strength()
            return True

        # Check if the card's ability is "Muster"
        elif card.ability == "Muster":
            player_deck = self.players[turn].deck
            cards_to_place = player_deck.draw_card_by_id(card.id)
            cards_to_place.append(card)
            self.rows[row_index].add_cards(card.id, cards_to_place)
            self.calculate_strength()
            return True

        # Check if the card's ability is "Medic"
        elif card.ability == "Medic":
            player_graveyard = self.graveyards[turn]
            if card.special_argument == -1:
                self.rows[row_index].add_card(card)
                self.calculate_strength()
                return True
            revived_cards = player_graveyard.revive_cards(card.special_argument)
            self.rows[row_index].add_card(card)
            for revived_card in revived_cards:
                index = revived_card.placement + (3 * turn)
                self.rows[index].add_card(revived_card)
            self.calculate_strength()
            return True

        # Check if the card's ability is "Decoy"
        elif card.ability == "Decoy":
            removed_card = self.rows[row_index].remove_card_by_id(card.special_argument)
            self.players[turn].add_card(removed_card)
            self.calculate_strength()
            return True

        self.rows[row_index].add_card(card)
        self.calculate_strength()
        return True

    def calculate_strength(self):
        """
        Recalculates strength after placing card.
        """
        self.player_strength = [0, 0]
        for i in range(6):
            if i < 3:
                self.player_strength[0] += self.rows[i].row_strength
                self.game_state_matrix.change_score_player(0, self.player_strength[0])
            else:
                self.player_strength[1] += self.rows[i].row_strength
                self.game_state_matrix.change_score_player(1, self.player_strength[1])

    def end_game(self):
        """
        Move all cards on the board to their respective graveyard.
        Recalculates board strength after moving all cards to graveyards.
        """
        for i in range(6):
            if i < 3:
                self.graveyards[0].add_row(self.rows[i])
            else:
                self.graveyards[1].add_row(self.rows[i])
            self.rows[i].clear_row()
            self.rows[i] = Row(i, self.game_state_matrix)

        self.calculate_strength()


class Card:
    """
    A class representing a card in a game.

    Attributes:
    -----------
        ability : str
            The ability of the card.
        id : int
            The ID of the card.
        strength : int
            The strength of the card.
        type : str
            The type of the card.
        placement : int
            The placement of the card.
        strength_modifier : int, optional
            The strength modifier of the card. Defaults to 1.
        name : str, optional
            The name of the card.
        current_strength : int
            The current strength of card with all modifiers and weather applied
        special_argument: int
            Attribute used for medics and decoys to determined who to resurrect.
    """

    def __init__(self, ability, _id, strength, _type, placement, strength_modifier=1, name=None):
        self.name = name
        self.ability = ability
        self.id = _id
        self.strength = strength
        self.type = _type
        self.placement = placement
        self.strength_modifier = strength_modifier
        self.special_argument = -1
        self.current_strength = strength


class Deck:
    """
    Represents a deck of cards used in the game.

    Attributes:
    -----------
        cards (list):
            A list of cards in the deck.
        cards_count (ndarray):
            An ndarray of length 120 containing counts of each card in deck.
    """

    def __init__(self, _id, game_state_matrix):
        """
        Initializes an empty deck.
        """
        self.game_state_matrix = game_state_matrix
        self.id = _id
        self.cards = []
        self.cards_count = np.zeros(120)
        # random.seed(0)

    def draw(self):
        """
        Draws a random card from the deck.

        Returns:
            Card or None:
                The drawn card if the deck is not empty, None otherwise.
        """
        if len(self.cards) == 0:
            return None
        else:
            index = random.randrange(len(self.cards))
            card = self.cards.pop(index)
            self.cards_count[card.id] -= 1
            self.game_state_matrix.change_deck_count(self.id, card.id, self.cards_count[card.id])
            return card

    def add(self, card):
        """
        Adds a card to the deck.

        Args:
            card (Card):
                The card to add to the deck.
        """
        self.cards.append(card)
        self.cards_count[card.id] += 1
        self.game_state_matrix.change_deck_count(self.id, card.id, self.cards_count[card.id])

    def draw_card_by_id(self, card_id):
        """
        Draws all cards with the specified ID from the deck.

        Args:
            card_id (int): The ID of the card to draw.

        Returns:
            List[Card]:
                A list of cards with the specified ID.
        """
        drawn_cards = [card for card in self.cards if card.id == card_id]
        self.cards = [card for card in self.cards if card.id != card_id]
        self.cards_count[card_id] = 0
        self.game_state_matrix.change_deck_count(self.id, card_id, self.cards_count[card_id])
        return drawn_cards

    def get_state(self):
        """
        Gets state of deck

        Returns:
            ndarray[int]:
                Number of each card in deck
        """
        return self.cards_count


class GameState:
    def __init__(self):
        self.state_matrix_0 = np.zeros((20, 148))
        self.state_matrix_1 = np.zeros((20, 148))

    def starting_state(self, all_cards):
        for group in all_cards.values():
            for card in group:
                self.state_matrix_0[16][card['Id']] = card['Strength']
                self.state_matrix_0[17][card['Id']] = transform(card['Type'])
                self.state_matrix_0[18][card['Id']] = transform(card['Ability'])
                self.state_matrix_0[19][card['Id']] = card['Placement']
                self.state_matrix_1[16][card['Id']] = card['Strength']
                self.state_matrix_1[17][card['Id']] = transform(card['Type'])
                self.state_matrix_1[18][card['Id']] = transform(card['Ability'])
                self.state_matrix_1[19][card['Id']] = card['Placement']

    def change_lives(self, id_player, new_value):
        if id_player == 0:
            self.state_matrix_0[:, 123] = new_value
            self.state_matrix_1[:, 124] = new_value
        else:
            self.state_matrix_1[:, 123] = new_value
            self.state_matrix_0[:, 124] = new_value

    def change_card_count_on_hand(self, id_player, new_value):
        if id_player == 0:
            self.state_matrix_0[:, 125] = new_value
            self.state_matrix_1[:, 126] = new_value
        else:
            self.state_matrix_1[:, 125] = new_value
            self.state_matrix_0[:, 126] = new_value

    def change_deck_count(self, id_player, id_card, new_value):
        if id_player == 0:
            self.state_matrix_0[15, id_card] = new_value
        else:
            self.state_matrix_1[15, id_card] = new_value

    def change_weather(self, id_row, weather_value):
        if id_row in [0, 3]:
            self.state_matrix_0[:, 120] = int(weather_value)
            self.state_matrix_1[:, 120] = int(weather_value)
        elif id_row in [1, 4]:
            self.state_matrix_0[:, 121] = int(weather_value)
            self.state_matrix_1[:, 121] = int(weather_value)
        else:
            self.state_matrix_0[:, 122] = int(weather_value)
            self.state_matrix_1[:, 122] = int(weather_value)

    def change_row_card_count(self, id_row, id_card, new_count_value):
        if id_row == 0:
            self.state_matrix_0[1, id_card] = new_count_value
            self.state_matrix_1[7, id_card] = new_count_value
        elif id_row == 1:
            self.state_matrix_0[3, id_card] = new_count_value
            self.state_matrix_1[9, id_card] = new_count_value
        elif id_row == 2:
            self.state_matrix_0[5, id_card] = new_count_value
            self.state_matrix_1[11, id_card] = new_count_value
        elif id_row == 3:
            self.state_matrix_1[1, id_card] = new_count_value
            self.state_matrix_0[7, id_card] = new_count_value
        elif id_row == 4:
            self.state_matrix_1[3, id_card] = new_count_value
            self.state_matrix_0[9, id_card] = new_count_value
        elif id_row == 5:
            self.state_matrix_1[5, id_card] = new_count_value
            self.state_matrix_0[11, id_card] = new_count_value

    def change_row_card_strength(self, id_row, id_card, new_strength_value):
        if id_row == 0:
            self.state_matrix_0[2, id_card] = new_strength_value
            self.state_matrix_1[8, id_card] = new_strength_value
        elif id_row == 1:
            self.state_matrix_0[4, id_card] = new_strength_value
            self.state_matrix_1[10, id_card] = new_strength_value
        elif id_row == 2:
            self.state_matrix_0[6, id_card] = new_strength_value
            self.state_matrix_1[12, id_card] = new_strength_value
        elif id_row == 3:
            self.state_matrix_1[2, id_card] = new_strength_value
            self.state_matrix_0[8, id_card] = new_strength_value
        elif id_row == 4:
            self.state_matrix_1[4, id_card] = new_strength_value
            self.state_matrix_0[10, id_card] = new_strength_value
        elif id_row == 5:
            self.state_matrix_1[6, id_card] = new_strength_value
            self.state_matrix_0[12, id_card] = new_strength_value

    def change_hand_card_count(self, id_player, id_card, new_count_value):
        if id_player == 0:
            self.state_matrix_0[0, id_card] = new_count_value
        else:
            self.state_matrix_1[0, id_card] = new_count_value

    def change_graveyard_card_count(self, id_player, id_card, new_count_value):
        if id_player == 0:
            self.state_matrix_0[13, id_card] = new_count_value
            self.state_matrix_1[14, id_card] = new_count_value
        else:
            self.state_matrix_1[13, id_card] = new_count_value
            self.state_matrix_0[14, id_card] = new_count_value

    def change_row_additive_modifier(self, id_row, new_value):
        if id_row == 0:
            self.state_matrix_0[:, 127] = new_value
            self.state_matrix_1[:, 130] = new_value
        elif id_row == 1:
            self.state_matrix_0[:, 128] = new_value
            self.state_matrix_1[:, 131] = new_value
        elif id_row == 2:
            self.state_matrix_0[:, 129] = new_value
            self.state_matrix_1[:, 132] = new_value
        elif id_row == 3:
            self.state_matrix_1[:, 127] = new_value
            self.state_matrix_0[:, 130] = new_value
        elif id_row == 4:
            self.state_matrix_1[:, 128] = new_value
            self.state_matrix_0[:, 131] = new_value
        elif id_row == 5:
            self.state_matrix_1[:, 129] = new_value
            self.state_matrix_0[:, 132] = new_value

    def change_row_multiplicative_modifier(self, id_row, new_value):
        if id_row == 0:
            self.state_matrix_0[:, 133] = new_value
            self.state_matrix_1[:, 136] = new_value
        elif id_row == 1:
            self.state_matrix_0[:, 134] = new_value
            self.state_matrix_1[:, 137] = new_value
        elif id_row == 2:
            self.state_matrix_0[:, 135] = new_value
            self.state_matrix_1[:, 138] = new_value
        elif id_row == 3:
            self.state_matrix_1[:, 133] = new_value
            self.state_matrix_0[:, 136] = new_value
        elif id_row == 4:
            self.state_matrix_1[:, 134] = new_value
            self.state_matrix_0[:, 137] = new_value
        elif id_row == 5:
            self.state_matrix_1[:, 135] = new_value
            self.state_matrix_0[:, 138] = new_value

    def change_row_score(self, id_row, new_value):
        if id_row == 0:
            self.state_matrix_0[:, 139] = new_value
            self.state_matrix_1[:, 142] = new_value
        elif id_row == 1:
            self.state_matrix_0[:, 140] = new_value
            self.state_matrix_1[:, 143] = new_value
        elif id_row == 2:
            self.state_matrix_0[:, 141] = new_value
            self.state_matrix_1[:, 144] = new_value
        elif id_row == 3:
            self.state_matrix_1[:, 139] = new_value
            self.state_matrix_0[:, 142] = new_value
        elif id_row == 4:
            self.state_matrix_1[:, 140] = new_value
            self.state_matrix_0[:, 143] = new_value
        elif id_row == 5:
            self.state_matrix_1[:, 141] = new_value
            self.state_matrix_0[:, 144] = new_value

    def change_score_player(self, id_player, new_value):
        if id_player == 0:
            self.state_matrix_0[:, 145] = new_value
            self.state_matrix_1[:, 146] = new_value
        else:
            self.state_matrix_1[:, 145] = new_value
            self.state_matrix_0[:, 146] = new_value

    def change_passed(self, id_player, new_value):
        if id_player == 0:
            self.state_matrix_1[:, 147] = int(new_value)
        else:
            self.state_matrix_0[:, 147] = int(new_value)


class Row:
    """
    A class representing a row of Gwent cards.

    Attributes
    ----------
    cards : dict
        A dictionary that stores cards in the row as a list, with the card id as key.
    cards_list_count : numpy.ndarray
        An array of shape (120,) that stores the number of cards of each card id in the row.
    cards_list_current_strength : numpy.ndarray
        An array of shape (120,) that stores the current strength of each card in the row.
    multiplier_additive : int
        An integer representing the additive modifier that affects the strength of cards in the row.
    multiplier_multiplicative : float
        A float representing the multiplicative modifier that affects the strength of cards in the row.
    weather : bool
        A boolean indicating whether weather effect is applied to the row.
    row_strength : int
        An integer representing the current total strength of the row.
    highest_value_non_hero : int
        An integer representing the current highest strength of non-hero cards in the row.
    highest_value_non_hero_list : list
        A list of cards that have the highest strength of non-hero cards in the row.

    """

    def __init__(self, _id, game_state_matrix):
        """
        Initializes a new instance of the Row class.
        """
        self.game_state_matrix = game_state_matrix
        self.id = _id
        self.cards = {}
        self.cards_list_count = np.zeros(120)
        self.cards_list_current_strength = np.zeros(120)
        self.multiplier_additive = 0
        self.multiplier_multiplicative = 1
        self.weather = False
        self.row_strength = 0
        self.highest_value_non_hero = -1
        self.highest_value_non_hero_list = []
        self.game_state_matrix.change_weather(self.id, self.weather)
        self.game_state_matrix.change_row_multiplicative_modifier(self.id, self.multiplier_multiplicative)
        self.game_state_matrix.change_row_score(self.id, self.row_strength)

    def activate_weather(self):
        """
        Activates the weather effect on the row.
        """
        self.weather = True
        self.game_state_matrix.change_weather(self.id, self.weather)
        self.row_strength = 0
        for card_lists in self.cards.values():
            for card in card_lists:
                if card.type == 'Unit':
                    card.current_strength = self.calculate_card_strength(card)
                    self.row_strength += card.current_strength
                else:
                    self.row_strength += card.current_strength
            self.cards_list_current_strength[card_lists[0].id] = len(card_lists) * card_lists[0].current_strength
            self.game_state_matrix.change_row_card_strength(self.id, card_lists[0].id,
                                                            self.cards_list_current_strength[card_lists[0].id])
            self.game_state_matrix.change_row_score(self.id, self.row_strength)

    def clear_weather(self):
        """
        Clears the weather effect on the row.
        """
        self.weather = False
        self.game_state_matrix.change_weather(self.id, self.weather)
        self.row_strength = 0
        for card_lists in self.cards.values():
            for card in card_lists:
                if card.type == 'Unit':
                    card.current_strength = self.calculate_card_strength(card)
                    self.row_strength += card.current_strength
                else:
                    self.row_strength += card.current_strength
            self.cards_list_current_strength[card_lists[0].id] = len(card_lists) * card_lists[0].current_strength
            self.game_state_matrix.change_row_card_strength(self.id, card_lists[0].id,
                                                            self.cards_list_current_strength[card_lists[0].id])
            self.game_state_matrix.change_row_score(self.id, self.row_strength)

    def add_card(self, card):
        """
        Adds a card to the row.

        Args:
            card : Card
                A Card object representing the card to be added to the row.
        """
        if card.id in self.cards:
            self.cards[card.id].append(card)
        else:
            self.cards[card.id] = [card]
        self.cards_list_count[card.id] += 1
        self.game_state_matrix.change_row_card_count(self.id, card.id, self.cards_list_count[card.id])
        self.activate_cards_modifier(card)
        self.recalculate_current_strength(card, True)

    def add_cards(self, card_id, card_list):
        """
        Adds multiple cards to the row.

        Args:
            card_id : int
                The ID of the card to which the new cards will be added.
            card_list : list of Card objects
                A list of Card objects to be added to the row.
        """
        if card_id in self.cards:
            self.cards[card_id].extend(card_list)
        else:
            self.cards[card_id] = card_list
        self.cards_list_count[card_id] += len(card_list)
        self.game_state_matrix.change_row_card_count(self.id, card_id, self.cards_list_count[card_id])
        for card in card_list:
            self.activate_cards_modifier(card)
            self.recalculate_current_strength(card, True)

    def remove_card_by_id(self, card_id):
        """
        Removes a card from the row based on its ID.

        Args:
            card_id : int
                The ID of the card to be removed from the row.
        """
        if card_id in self.cards and self.cards[card_id]:
            self.cards_list_count[card_id] -= 1
            self.game_state_matrix.change_row_card_count(self.id, card_id, self.cards_list_count[card_id])
            card = self.cards[card_id].pop()
            if len(self.cards[card_id]) == 0:
                del self.cards[card_id]
            self.remove_cards_modifiers(card)
            self.recalculate_current_strength(card, False)
            if card in self.highest_value_non_hero_list:
                self.highest_value_non_hero_list.remove(card)
                self.find_new_highest()
            return card

    def remove_highest_value_cards(self):
        """
        Removes all cards with the highest strength value from the row.
        Returns a copy of the list of removed cards.
        """
        self.find_new_highest()
        for card in self.highest_value_non_hero_list:
            self.cards[card.id].remove(card)
            if len(self.cards[card.id]) == 0:
                del self.cards[card.id]
            self.recalculate_current_strength(card, False)
            if card.id in self.cards:
                self.cards_list_count[card.id] = len(self.cards[card.id])
                self.game_state_matrix.change_row_card_count(self.id, card.id, self.cards_list_count[card.id])
            else:
                self.cards_list_count[card.id] = 0
                self.game_state_matrix.change_row_card_count(self.id, card.id, self.cards_list_count[card.id])
        for card in self.highest_value_non_hero_list:
            self.remove_cards_modifiers(card)

        copy = self.highest_value_non_hero_list.copy()
        self.find_new_highest()
        return copy

    def recalculate_current_strength(self, card, insert):
        """
        Recalculates the current strength of a card and updates the
        `current_strength` attribute of that card, and the `cards_list_current_strength`
        attribute of the player instance. If `insert` is True, the function also checks if
        the card's strength is higher than the highest non-hero value and updates
        the `highest_value_non_hero` and `highest_value_non_hero_list` attributes.

        Args:
            card (Card):
                The card whose current strength needs to be recalculated.
            insert (bool):
                If True, check if the card's strength is higher than the highest
                non-hero value and update the relevant attributes.

        Returns:
            None
        """
        if card.type == 'Weather' or card.ability == 'Morale':
            for card_lists in self.cards.values():
                for c in card_lists:
                    if c.type == 'Unit':
                        current_strength = self.calculate_card_strength(c)
                        c.current_strength = current_strength
                        self.cards_list_current_strength[c.id] = len(card_lists) * current_strength
                        self.game_state_matrix.change_row_card_strength(self.id, c.id,
                                                                        self.cards_list_current_strength[c.id])
                        if insert:
                            self.check_max(c)
        elif card.ability == 'Bond' and card.id in self.cards:
            for c in self.cards[card.id]:
                c.strength_modifier = len(self.cards[card.id])
                current_strength = self.calculate_card_strength(c)
                c.current_strength = current_strength
                self.cards_list_current_strength[c.id] = len(self.cards[card.id]) * current_strength
                self.game_state_matrix.change_row_card_strength(self.id, c.id,
                                                                self.cards_list_current_strength[c.id])
                if insert:
                    self.check_max(c)
        elif card.type == 'Unit' and not card.ability == 'Bond' and not card.ability == 'Morale':
            current_strength = self.calculate_card_strength(card)
            card.current_strength = current_strength
            self.cards_list_current_strength[card.id] = current_strength * len(self.cards[card.id])
            self.game_state_matrix.change_row_card_strength(self.id, card.id,
                                                            self.cards_list_current_strength[card.id])
            if insert:
                self.check_max(card)
        else:
            self.cards_list_current_strength[card.id] = card.current_strength * len(self.cards[card.id])
            self.game_state_matrix.change_row_card_strength(self.id, card.id,
                                                            self.cards_list_current_strength[card.id])

        self.row_strength = 0
        for card_list in self.cards.values():
            for card_c in card_list:
                self.row_strength += card_c.current_strength
        self.game_state_matrix.change_row_score(self.id, self.row_strength)

    def calculate_card_strength(self, card):
        """
        Calculates the strength of a card, taking into account any modifiers
        that are currently active on the player instance.

        Args:
            card (Card):
                The card whose strength needs to be calculated.

        Returns:
            int: The calculated strength of the card.
        """
        if not self.weather:
            return ((
                            card.strength * card.strength_modifier) + self.multiplier_additive) * \
                   self.multiplier_multiplicative
        elif self.weather:
            return ((1 * card.strength_modifier) + self.multiplier_additive) * self.multiplier_multiplicative

    def remove_cards_modifiers(self, card):
        """
        Removes the effects of a card's modifiers on the player's deck.

        Args:
            card (Card):
                The card object to remove the modifiers from.
        """
        if card.ability == 'Morale':
            if card.name == 'Dandelion' or card.type == 'Morale':
                # If the card is either Dandelion or has the Morale type, divide the player's multiplier by 2
                self.multiplier_multiplicative /= 2
                self.game_state_matrix.change_row_multiplicative_modifier(self.id, self.multiplier_multiplicative)
            elif card.ability == 'Morale' and not card.name == 'Dandelion' and not card.type == 'Morale':
                # If the card is of Morale type but not Dandelion, subtract 1 from the player's additive multiplier
                self.multiplier_additive -= 1
                self.game_state_matrix.change_row_additive_modifier(self.id, self.multiplier_additive)
        elif card.ability == 'Bond':
            # For each card in the player's deck with the same ID as the given card, set its strength modifier to the
            # length of the deck
            if card.id in self.cards:
                for c in self.cards[card.id]:
                    c.strength_modifier = len(self.cards[card.id])

    def activate_cards_modifier(self, card):
        """
        Activates the effects of a card's modifiers on the player's deck.

        Args:
            card (Card):
                The card object to activate the modifiers for.
        """
        if card.ability == 'Morale':
            if (card.name == 'Dandelion' or card.type == 'Morale') and len(self.cards[card.id]) == 1:
                # If the card is either Dandelion or has the Morale type and only one of it is in the row,
                # multiply the multiplier by 2
                self.multiplier_multiplicative *= 2
                self.game_state_matrix.change_row_multiplicative_modifier(self.id, self.multiplier_multiplicative)
            elif card.ability == 'Morale' and not card.name == 'Dandelion' and not card.type == 'Morale':
                # If the card is of Morale type but not Dandelion, add 1 to the row's additive multiplier
                self.multiplier_additive += 1
                self.game_state_matrix.change_row_additive_modifier(self.id, self.multiplier_additive)
        elif card.ability == 'Bond':
            # For each card in the player's deck with the same ID as the given card, set its strength modifier to the
            # length of the row
            for c in self.cards[card.id]:
                c.strength_modifier = len(self.cards[card.id])

    def check_max(self, card):
        """
        Checks if a card has the highest non-hero strength value in the player's deck.

        Args:
            card (Card):
                The card object to check.
        """
        if card.current_strength > self.highest_value_non_hero:
            # If the card has a higher strength value than the current highest value, set it as the new highest value
            # and create a new list containing only this card
            self.highest_value_non_hero = card.current_strength
            self.highest_value_non_hero_list = [card]
        elif card.current_strength == self.highest_value_non_hero:
            # If the card has the same strength value as the current highest value, add it to the list of cards with
            # the highest value
            self.highest_value_non_hero_list.append(card)

    def find_new_highest(self):
        """
        Finds the non-hero card(s) with the highest current strength from the list of cards stored in the class
        instance variable 'cards',
        and updates the instance variables 'highest_value_non_hero' and 'highest_value_non_hero_list' accordingly...
        """
        self.highest_value_non_hero = -1
        self.highest_value_non_hero_list = []
        for card_list in self.cards.values():
            for card in card_list:
                if card.type == 'Unit' and card.current_strength > self.highest_value_non_hero:
                    self.highest_value_non_hero_list = [card]
                    self.highest_value_non_hero = card.current_strength
                elif card.type == 'Unit' and card.current_strength == self.highest_value_non_hero:
                    self.highest_value_non_hero_list.append(card)

    def get_state(self):
        """
        Creates 120x2 matrix indicating state of row,
        first row number of each card in row,
        second row combined current strength of cards with same id

        Returns :
            ndarray[int] 120x2:
                number of cards and combined strength of each card
        """
        state = np.vstack((self.cards_list_count, self.cards_list_current_strength))
        return state

    def clear_row(self):
        for card_list in self.cards.values():
            for card in card_list:
                self.game_state_matrix.change_row_card_count(self.id, card.id, 0)
                self.game_state_matrix.change_row_card_strength(self.id, card.id, 0)


class Graveyard:
    """
    This class represents a graveyard of cards. It provides methods to add and insert cards, as well as
    to retrieve cards from the graveyard.

    Attributes:
    -----------
        cards: dict
            A dictionary containing lists of cards, where the keys are card IDs.
    """

    def __init__(self, _id, game_state_matrix):
        """
        Constructor for Graveyard class. Initializes an empty dictionary to store the cards.
        """
        self.game_state_matrix = game_state_matrix
        self.id = _id
        self.cards = {}
        self.cards_count = np.zeros(120)

    def add_row(self, row: Row):
        """
        Adds a row of cards to the graveyard.

        Args:
            row: Row
                An object where cards are stored in dictionary.

        Returns:
        None
        """
        for card_id, card_list in row.cards.items():
            self.insert_list(card_id, card_list)

    def insert_list(self, card_id, card_list):
        """
        Inserts a list of cards into the graveyard for a given card ID.

        Args:
            card_id: int
                The ID of the card to add to the graveyard.
            card_list: List
                The list of cards to add to the graveyard.

        Returns:
        None
        """
        if card_id in self.cards:
            self.cards[card_id].extend(card_list)
        else:
            self.cards[card_id] = card_list
        self.cards_count[card_id] += len(card_list)
        self.game_state_matrix.change_graveyard_card_count(self.id, card_id, self.cards_count[card_id])

    def revive_cards(self, card_id):
        """
        Removes and returns the top card from the list of cards for the given card ID,
        and all medics which are units in graveyard.

        Args:
            card_id: int
                The ID of the card to revive.

        Returns:
            Optional[Card]
                The top card from the list of cards for the given card ID, along with all medics.
        """
        if card_id in self.cards:
            cards_to_revive = []
            for card_list in self.cards.values():
                if len(card_list) > 0 and card_list[0].ability == 'Medic' and card_list[0].type == 'Unit':
                    cards_to_revive.extend(card_list)
                    self.cards_count[card_list[0].id] = 0
                    self.game_state_matrix.change_graveyard_card_count(self.id, card_list[0].id,
                                                                       self.cards_count[card_list[0].id])
            cards_to_revive.extend([self.cards[card_id].pop()])
            self.cards_count[card_id] -= 1
            self.game_state_matrix.change_graveyard_card_count(self.id, card_id,
                                                               self.cards_count[card_id])

            return cards_to_revive

    def add_cards(self, card_list):
        """
        Adds a list of cards to the graveyard by calling insert_card() method for each card in the list.

        Args:
            card_list: List[Card]
                A list of Card objects to be added to the graveyard.
        """
        for card in card_list:
            self.insert_card(card)

    def insert_card(self, card):
        """
        Inserts a card into the graveyard. If a list for the given card ID exists in the dictionary, the card is
        appended to the list. If not, a new list is created with the card as its first element.

        Args:
            card:
                A Card object to be inserted into the graveyard.
        """
        if card.id in self.cards:
            self.cards[card.id].append(card)
        else:
            self.cards[card.id] = [card]
        self.cards_count[card.id] += 1
        self.game_state_matrix.change_graveyard_card_count(self.id, card.id,
                                                           self.cards_count[card.id])

    def get_state(self):
        """
        Gets state of graveyard

        Returns:
            ndarray[int]:
                Number of each card in graveyard
        """
        return self.cards_count


class Player:
    """
    Represents a player in the game.

    Attributes:
    -----------
        hand (list):
            A list of cards in the player's hand.
        lives (int):
            The number of lives the player has remaining.
        deck (Deck):
            The deck of cards from which the player draws.
        passed (bool):
            A flag indicating whether the player has passed their turn.
        cards_count(ndarray):
            Array representing counts of each card in player's hand.
    """

    def __init__(self, _id, deck, game_state_matrix):
        """
        Initializes a player object with a deck of cards.

        Args:
            deck (Deck):
                The deck of cards to draw from.
        """
        self.game_state_matrix = game_state_matrix
        self.id = _id
        self.hand = []
        self.cards_count = np.zeros(120)
        self.lives = 2
        self.deck = deck
        self.passed = False
        self.game_state_matrix.change_lives(self.id, self.lives)
        self.game_state_matrix.change_card_count_on_hand(self.id, len(self.hand))
        for _ in range(10):
            self.draw()

    def draw(self):
        """
        Draws a card from the deck and adds it to the player's hand.
        """
        card = self.deck.draw()
        self.hand.append(card)
        self.cards_count[card.id] += 1
        self.game_state_matrix.change_card_count_on_hand(self.id, len(self.hand))
        self.game_state_matrix.change_hand_card_count(self.id, card.id, self.cards_count[card.id])

    def play(self, card):
        """
        Removes a card from the player's hand.

        Args:
            card (Card):
                The card to remove from the player's hand.
        """
        self.hand.remove(card)
        self.cards_count[card.id] -= 1
        self.game_state_matrix.change_card_count_on_hand(self.id, len(self.hand))
        self.game_state_matrix.change_hand_card_count(self.id, card.id, self.cards_count[card.id])

    def take_damage(self):
        """
        Decreases the player's lives by 1.
        """
        self.lives -= 1
        self.game_state_matrix.change_lives(self.id, self.lives)

    def pass_game(self):
        """
        Flags the player as having passed their turn.
        """
        self.passed = True
        self.game_state_matrix.change_passed(self.id, self.passed)

    def new_game(self):
        """
        Resets the player's passed flag and draws a new card from the deck.
        """
        if self.lives > 0:
            self.passed = False
            self.game_state_matrix.change_passed(self.id, self.passed)
            card = self.deck.draw()
            self.hand.append(card)
            self.cards_count[card.id] += 1
            self.game_state_matrix.change_card_count_on_hand(self.id, len(self.hand))
            self.game_state_matrix.change_hand_card_count(self.id, card.id, self.cards_count[card.id])

    def get_card_by_id(self, card_id):
        """
        Searches the player's hand for a card with the specified ID and removes it.

        Args:
            card_id (int):
                The ID of the card to retrieve.

        Returns:
            Card:
                The card with the specified ID, or None if the card is not found in the player's hand.
        """
        for card in self.hand:
            if card.id == card_id:
                self.hand.remove(card)
                self.cards_count[card.id] -= 1
                self.game_state_matrix.change_card_count_on_hand(self.id, len(self.hand))
                self.game_state_matrix.change_hand_card_count(self.id, card.id, self.cards_count[card.id])
                return card
        return None

    def add_card(self, card):
        """
        Adds card to player's hand.

        Args:
            card (Card):
                The card object to add to player's hand.
        """
        self.hand.append(card)
        self.cards_count[card.id] += 1
        self.game_state_matrix.change_card_count_on_hand(self.id, len(self.hand))
        self.game_state_matrix.change_hand_card_count(self.id, card.id, self.cards_count[card.id])

    def get_number_of_cards(self):
        """
        Gets number of cards in player's hand

        Returns:
            int:
                Number of cards

        """
        return len(self.hand)

    def get_state(self):
        """
        Gets state of hand

        Returns:
            ndarray[int]:
                Number of each card in hand
        """
        return self.cards_count
