import numpy as np


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

    def __init__(self):
        """
        Initializes a new instance of the Row class.
        """
        self.cards = {}
        self.cards_list_count = np.zeros(120)
        self.cards_list_current_strength = np.zeros(120)
        self.multiplier_additive = 0
        self.multiplier_multiplicative = 1
        self.weather = False
        self.row_strength = 0
        self.highest_value_non_hero = -1
        self.highest_value_non_hero_list = []

    def activate_weather(self):
        """
        Activates the weather effect on the row.
        """
        self.weather = True
        self.row_strength = 0
        for card_lists in self.cards.values():
            for card in card_lists:
                if card.type == 'Unit':
                    card.current_strength = self.calculate_card_strength(card)
                    self.row_strength += card.current_strength
                else:
                    self.row_strength += card.current_strength
            self.cards_list_current_strength[card_lists[0].id] = len(card_lists) * card_lists[0].current_strength

    def clear_weather(self):
        """
        Clears the weather effect on the row.
        """
        self.weather = False
        self.row_strength = 0
        for card_lists in self.cards.values():
            for card in card_lists:
                if card.type == 'Unit':
                    card.current_strength = self.calculate_card_strength(card)
                    self.row_strength += card.current_strength
                else:
                    self.row_strength += card.current_strength
            self.cards_list_current_strength[card_lists[0].id] = len(card_lists) * card_lists[0].current_strength

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
            else:
                self.cards_list_count[card.id] = 0
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
                        if insert:
                            self.check_max(c)
        elif card.ability == 'Bond' and card.id in self.cards:
            for c in self.cards[card.id]:
                c.strength_modifier = len(self.cards[card.id])
                current_strength = self.calculate_card_strength(c)
                c.current_strength = current_strength
                self.cards_list_current_strength[c.id] = len(self.cards[card.id]) * current_strength
                if insert:
                    self.check_max(c)
        elif card.type == 'Unit' and not card.ability == 'Bond' and not card.ability == 'Morale':
            current_strength = self.calculate_card_strength(card)
            card.current_strength = current_strength
            self.cards_list_current_strength[card.id] = current_strength
            if insert:
                self.check_max(card)
        else:
            self.cards_list_current_strength[card.id] = card.current_strength

        self.row_strength = 0
        for card_list in self.cards.values():
            for card_c in card_list:
                self.row_strength += card_c.current_strength

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
                                card.strength * card.strength_modifier) + self.multiplier_additive) * self.multiplier_multiplicative
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
            elif card.ability == 'Morale' and not card.name == 'Dandelion':
                # If the card is of Morale type but not Dandelion, subtract 1 from the player's additive multiplier
                self.multiplier_additive -= 1
        elif card.ability == 'Bond':
            # For each card in the player's deck with the same ID as the given card, set its strength modifier to the length of the deck
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
                # If the card is either Dandelion or has the Morale type and only one of it is in the row, multiply the multiplier by 2
                self.multiplier_multiplicative *= 2
            elif card.ability == 'Morale' and not card.name == 'Dandelion':
                # If the card is of Morale type but not Dandelion, add 1 to the row's additive multiplier
                self.multiplier_additive += 1
        elif card.ability == 'Bond':
            # For each card in the player's deck with the same ID as the given card, set its strength modifier to the length of the row
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
            # If the card has a higher strength value than the current highest value, set it as the new highest value and create a new list containing only this card
            self.highest_value_non_hero = card.current_strength
            self.highest_value_non_hero_list = [card]
        elif card.current_strength == self.highest_value_non_hero:
            # If the card has the same strength value as the current highest value, add it to the list of cards with the highest value
            self.highest_value_non_hero_list.append(card)

    def find_new_highest(self):
        """
        Finds the non-hero card(s) with the highest current strength from the list of cards stored in the class instance variable 'cards',
        and updates the instance variables 'highest_value_non_hero' and 'highest_value_non_hero_list' accordingly..
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
                number of cards and combined strangth of each card
        """
        state = np.vstack((self.cards_list_count, self.cards_list_current_strength))
        return state
