from Game.Row import Row
import numpy as np


class Graveyard:
    """
    This class represents a graveyard of cards. It provides methods to add and insert cards, as well as
    to retrieve cards from the graveyard.

    Attributes:
    -----------
        cards: dict
            A dictionary containing lists of cards, where the keys are card IDs.
    """

    def __init__(self):
        """
        Constructor for Graveyard class. Initializes an empty dictionary to store the cards.
        """
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
                    card_list = []
            cards_to_revive.extend([self.cards[card_id].pop()])
            self.cards_count[card_id] -= 1
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

    def get_state(self):
        """
        Gets state of graveyard

        Returns:
            ndarray[int]:
                Number of each card in graveyard
        """
        return self.cards_count
