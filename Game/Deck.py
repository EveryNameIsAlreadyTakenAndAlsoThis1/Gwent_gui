import random
import numpy as np


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

    def __init__(self, id, game_state_matrix):
        """
        Initializes an empty deck.
        """
        self.game_state_matrix = game_state_matrix
        self.id = id
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
