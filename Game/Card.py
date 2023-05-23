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
            Atribute used for medics and decoys to determined who to ressurect.
    """

    def __init__(self, ability, id, strength, type, placement, strength_modifier=1, name=None):
        self.name = name
        self.ability = ability
        self.id = id
        self.strength = strength
        self.type = type
        self.placement = placement
        self.strength_modifier = strength_modifier
        self.special_argument = -1
        self.current_strength = strength
