import numpy as np


class GameState:
    def __init__(self):
        self.state_matrix_0 = np.zeros((20, 148))
        self.state_matrix_1 = np.zeros((20, 148))

    def starting_state(self, all_cards):
        for group in all_cards.values():
            for card in group:
                self.state_matrix_0[16][card['Id']] = card['Strength']
                self.state_matrix_0[17][card['Id']] = self.transform(card['Type'])
                self.state_matrix_0[18][card['Id']] = self.transform(card['Ability'])
                self.state_matrix_0[19][card['Id']] = card['Placement']
                self.state_matrix_1[16][card['Id']] = card['Strength']
                self.state_matrix_1[17][card['Id']] = self.transform(card['Type'])
                self.state_matrix_1[18][card['Id']] = self.transform(card['Ability'])
                self.state_matrix_1[19][card['Id']] = card['Placement']

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
