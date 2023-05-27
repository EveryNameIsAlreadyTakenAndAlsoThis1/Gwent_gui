from Game.Row import Row
from Game.Graveyard import Graveyard
import numpy as np
from numpy.core.shape_base import hstack


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

    def get_state(self, turn):
        """
        Creates two matrixes of current state of board.

        Returns:
            ndarray[int]:
                120x16 - 15 rows with 120 elements representing counts of cards and collective strength of that card in each row
            ndarray[int]:
                28x20 - 28 columns representing all other information on board all rows contain same information as the one above

        """
        state = None
        if turn == 0:
            state = np.vstack((self.players[0].get_state(), self.rows[0].get_state(), self.rows[1].get_state(),
                               self.rows[2].get_state(), self.rows[3].get_state(),
                               self.rows[4].get_state(), self.rows[5].get_state(),
                               self.graveyards[0].get_state(), self.graveyards[1].get_state()))
        else:
            state = np.vstack((self.players[1].get_state(), self.rows[3].get_state(), self.rows[4].get_state(),
                               self.rows[5].get_state(), self.rows[0].get_state(),
                               self.rows[1].get_state(), self.rows[2].get_state(),
                               self.graveyards[1].get_state(), self.graveyards[0].get_state()))

        state = np.vstack((state, self.players[turn].deck.get_state()))

        number_of_rows = 20

        column_state = np.vstack((np.full((number_of_rows), int(self.rows[0].weather)),
                                  np.full((number_of_rows), int(self.rows[1].weather)),
                                  np.full((number_of_rows), int(self.rows[2].weather))))

        column_state = np.vstack((column_state, np.full((number_of_rows), self.players[turn].lives),
                                  np.full((number_of_rows), self.players[turn ^ 1].lives)))

        column_state = np.vstack((column_state, np.full((number_of_rows), self.players[turn].get_number_of_cards()),
                                  np.full((number_of_rows), self.players[turn ^ 1].get_number_of_cards())))

        if turn == 0:
            for i in range(6):
                column_state = np.vstack((column_state, np.full((number_of_rows), self.rows[i].multiplier_additive)))
        else:
            for i in range(3, 6):
                column_state = np.vstack((column_state, np.full((number_of_rows), self.rows[i].multiplier_additive)))
            for i in range(3):
                column_state = np.vstack((column_state, np.full((number_of_rows), self.rows[i].multiplier_additive)))

        if turn == 0:
            for i in range(6):
                column_state = np.vstack(
                    (column_state, np.full((number_of_rows), self.rows[i].multiplier_multiplicative)))
        else:
            for i in range(3, 6):
                column_state = np.vstack(
                    (column_state, np.full((number_of_rows), self.rows[i].multiplier_multiplicative)))
            for i in range(3):
                column_state = np.vstack(
                    (column_state, np.full((number_of_rows), self.rows[i].multiplier_multiplicative)))

        if turn == 0:
            for i in range(6):
                column_state = np.vstack((column_state, np.full((number_of_rows), self.rows[i].row_strength)))
        else:
            for i in range(3, 6):
                column_state = np.vstack((column_state, np.full((number_of_rows), self.rows[i].row_strength)))
            for i in range(3):
                column_state = np.vstack((column_state, np.full((number_of_rows), self.rows[i].row_strength)))

        column_state = np.vstack((column_state, np.full((number_of_rows), self.player_strength[turn])))
        column_state = np.vstack((column_state, np.full((number_of_rows), self.player_strength[turn ^ 1])))

        column_state = np.vstack((column_state, np.full((number_of_rows), int(self.players[turn ^ 1].passed)))).T

        return state, column_state
