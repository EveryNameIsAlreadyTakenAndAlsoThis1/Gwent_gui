import numpy as np


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

    def __init__(self, id, deck, game_state_matrix):
        """
        Initializes a player object with a deck of cards.

        Args:
            deck (Deck): 
                The deck of cards to draw from.
        """
        self.game_state_matrix = game_state_matrix
        self.id = id
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
