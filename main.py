import copy
import json
import random

import numpy as np
import pygame

from Game.Game import Game


def load_file(file_path):
    """
    Loads card data from a CSV file and organizes it into a dictionary along with related images.

    Parameters:
    ----------
    file_path : str
        The path to the CSV file to be read.

    Returns:
    -------
    dict
        A dictionary containing card details. Each key is a card's ID, and the value is another dictionary
        containing details and loaded images of the card. The inner dictionary has the following keys:
            - 'Name': str
            - 'Id': int
            - 'Strength': int
            - 'Ability': str
            - 'Type': str
            - 'Placement': int
            - 'Count': int
            - 'Faction': str
            - 'Image': str
            - 'Image_sm': pygame.Surface
            - 'Image_lg': pygame.Surface
            - 'Type_icon': pygame.Surface or None
            - 'Ability_icon': pygame.Surface or None

    Behavior:
    -----------
    This function reads card data from a CSV file, loading images and icon details related to each card.
    It processes each line, excluding lines that are empty or contain certain faction names or the string 'Name'.
    Each card's data, including its images and icons, are stored in a dictionary, with the card's ID as the key.
    Images and icons are loaded into pygame surfaces and included in each card's dictionary.
    The resulting dictionary is returned, providing a comprehensive data structure for each card.

    Notes:
    -----
    The CSV file should be formatted correctly. Images and icons should exist at the specified paths,
    and the CSV data should align with the expected keys and data types.
    """
    with open(file_path, 'r') as f:
        data_read = f.read().splitlines()

    result = {}
    current_group = None

    for line in data_read:
        if line == '':
            continue

        if 'Northern Realms' in line or 'Scoiatael' in line or 'Neutral' in line or 'Nilfgaard' in line or 'Monsters' \
                in line or 'Name' in line:
            continue

        name, _id, strength, ability, card_type, placement, count, image, empty = line.split(',')

        type_icon = None
        if card_type == "Hero":
            type_icon = pygame.image.load('img/icons/power_hero2.png')
        elif card_type == "Unit":
            type_icon = pygame.image.load('img/icons/power_normal3.png')
        elif card_type == "Weather":
            weather_icons = ['img/icons/power_frost.png', 'img/icons/power_fog.png', 'img/icons/power_rain.png',
                             '', 'img/icons/power_clear.png']
            type_icon = pygame.image.load(weather_icons[int(placement)])
        elif card_type == "Decoy":
            type_icon = pygame.image.load('img/icons/power_decoy.png')
        elif card_type == "Morale":
            type_icon = pygame.image.load('img/icons/power_horn.png')
        elif card_type == "Scorch":
            type_icon = pygame.image.load('img/icons/power_scorch.png')

        ability_icon = None
        if ability != '0' and card_type in ['Unit', 'Hero']:
            ability_icon = pygame.image.load(f'img/icons/card_ability_{ability.lower()}.png')

        result[int(_id)] = ({
            'Name': name,
            'Id': int(_id),
            'Strength': int(strength),
            'Ability': ability,
            'Type': card_type,
            'Placement': int(placement),
            'Count': int(count),
            'Faction': current_group,
            'Image': image,
            'Image_sm': pygame.image.load(f'img/sm/{image}'),
            'Image_lg': pygame.image.load(f'img/lg/{image}'),
            'Type_icon': type_icon,
            'Ability_icon': ability_icon
        })

    return result


def load_file_game(file_path):
    """
    Load game data from a file and organizes it into a structured dictionary.

    Parameters:
    ----------
    file_path : str
        The path to the file containing the game data.

    Returns:
    -------
    dict
        A dictionary containing the organized game data, grouped by factions.

    Behavior:
    -----------
    - Opens the file located at `file_path` for reading.
    - Reads the data line-by-line, splitting it into different components, such as
      faction, name, id, strength, ability, card type, placement, and count.
    - Organizes the data into a dictionary, where each key represents a faction
      (e.g., Northern Realms, Scoiatael, Neutral, Nilfgaard, Monsters), and the
      corresponding value is a list of dictionaries containing the detailed information
      of each card associated with that faction.
    - Each card’s information dictionary includes keys like 'Name', 'Id', 'Strength',
      'Ability', 'Type', 'Placement', and 'Count', along with their respective values
      parsed from the file.
    - Empty lines and lines with column headers in the file are ignored.

    Example:
    -------
    The resulting dictionary might look something like this:
    {
        'Northern Realms': [
            {
                'Name': 'Card1',
                'Id': 1,
                'Strength': 5,
                'Ability': 'Some_Ability',
                'Type': 'Some_Type',
                'Placement': 1,
                'Count': 2,
                'Faction': 'Northern Realms'
            },
            ... (More cards)
        ],
        ... (More factions)
    }
    """

    with open(file_path, 'r') as f:
        data_read = f.read().splitlines()

    result = {}
    current_group = None

    for line in data_read:
        if line == '':
            continue

        if 'Northern Realms' in line or 'Scoiatael' in line or 'Neutral' in line or 'Nilfgaard' in line or 'Monsters' \
                in line:
            current_group = line.strip(',')
            result[current_group] = []
            continue

        name, _id, strength, ability, card_type, placement, count, image, empty = line.split(',')

        if name == 'Name':
            continue

        result[current_group].append({
            'Name': name,
            'Id': int(_id),
            'Strength': int(strength),
            'Ability': ability,
            'Type': card_type,
            'Placement': int(placement),
            'Count': int(count),
            'Faction': current_group
        })

    return result


def scale_surface(surface, target_size):
    """
    Scales a Pygame surface proportionally, ensuring that the aspect ratio is maintained,
    so it fits within the dimensions defined by the target size without distortion.

    Parameters:
    ----------
    surface : pygame.Surface
        The original surface that needs to be scaled. It contains the image or content
        that will be resized to fit within the specified target size.

    target_size : tuple of int
        A tuple containing two integers representing the width and height
        (respectively) of the target size the surface should be scaled to.

    Returns:
    -------
    pygame.Surface
        A new surface object representing the scaled content of the original surface.
        The scaling is done proportionally to maintain the aspect ratio of the original
        content, and the scaled content will fit within the dimensions specified by the
        target size.

    Behavior:
    -----------
    - The function calculates a scale factor based on the ratio of the target width to
      the original width and the target height to the original height, choosing the
      smaller of the two to maintain the aspect ratio.
    - A new size is then calculated using this scale factor, applied to both the width
      and height of the original surface.
    - Pygame’s smoothscale function is then used to scale the surface to this new size,
      which performs the resizing with antialiasing for a smoother appearance.
    - The resulting scaled surface is then returned.
    """
    target_width, target_height = target_size
    width, height = surface.get_size()
    scale_factor = min(target_width / width, target_height / height)
    new_size = (round(width * scale_factor), round(height * scale_factor))
    return pygame.transform.smoothscale(surface, new_size)


def fit_text_in_rect(text, font, color, rect):
    """
    Dynamically adjusts the font size and renders text to fit within a specified rectangle.
    The function increases the font size incrementally until the rendered text exceeds the
    dimensions of the rectangle, then decreases the size by one step to ensure it fits.

    Parameters:
    ----------
    text : str
        The string of text to be rendered and resized.
    font : ResizableFont
        An instance of a resizable font, used to render and resize the text.
    color : tuple of int
        An RGB tuple specifying the color of the text to be rendered.
    rect : pygame.Rect
        A rectangle within which the rendered text must fit.

    Returns:
    -------
    pygame.Surface
        A surface containing the rendered text adjusted to a size that fits within
        the specified rectangle.

    Behavior:
    --------
    - The function starts with a minimal font size and iteratively increases it, rendering
      the text at each step to check whether it still fits within the given rectangle.
    - When the text size exceeds either the width or height of the rectangle, the function
      decreases the font size by one step and renders the text one final time to ensure it fits.
    - The final rendered text, guaranteed to fit within the rectangle, is returned as a surface.
    """
    size = 1  # Start with a minimal font size
    font.resize(size)  # Adjust the font to the initial size
    new_text = font.font.render(text, True, color)  # Render the text

    # Incrementally increase the font size, rendering and checking the text at each step
    while new_text.get_width() <= rect.width and new_text.get_height() <= rect.height:
        size += 1
        font.resize(size)
        new_text = font.font.render(text, True, color)

    # Correct the font size if it was incremented past the point where the text fits
    if new_text.get_width() > rect.width or new_text.get_height() > rect.height:
        size -= 1
        font.resize(size)
        new_text = font.font.render(text, True, color)

    return new_text  # Return the rendered text that fits within the rectangle


def draw_centered_text(screen, text, rect):
    """
    Draws the given text centered in the given rectangle.

    Parameters:
    ----------
    screen : pygame.Surface
        The screen onto which the text should be drawn.
    text : pygame.Surface
        The text to be drawn.
    rect : pygame.Rect
        The rectangle within which the text should be centered.
    """
    # Get the width and height of the text
    text_width, text_height = text.get_size()

    # Calculate the position to center the text
    pos_x = rect.x + (rect.width - text_width) // 2
    pos_y = rect.y + (rect.height - text_height) // 2

    # Draw the text on the screen at the calculated position
    screen.blit(text, (pos_x, pos_y))


def draw_text_with_outline(screen, text, font, color, outline_color, position, thickness=1):
    """
    Draws text on the screen with a specified outline. The function first renders the outline
    by offsetting the text position, and then renders the main text at the given position.
    This creates a visual effect where the text appears to have an outline around it.

    Parameters:
    ----------
    screen : pygame.Surface
        The surface onto which the text will be drawn, usually the main display screen.
    text : str
        The text string to be rendered and drawn.
    font : pygame.font.Font
        The font in which the text will be rendered.
    color : tuple
        The RGB color tuple for the main text.
    outline_color : tuple
        The RGB color tuple for the outline of the text.
    position : tuple
        A tuple (x, y) representing the position where the main text will be drawn on the screen.
    thickness : int, optional
        The thickness of the outline in pixels. Default is 1 pixel.

    Behavior:
    --------
    - The function starts by rendering the outline text. For each pixel (up to the specified thickness)
      around the main text, the outline text is drawn, offset by a certain x and y value.
    - The main text is then rendered and drawn at the specified position, overlaying the outline.
      This process creates a text that stands out due to the contrast between the text color and the outline color.

    Note:
    ----
    - Increasing the thickness value will create a thicker outline around the text, but may also make
      the text harder to read if the thickness is too high relative to the font size.
    """
    # Render the outline text
    outline = font.render(text, True, outline_color)

    # Draw the outline by offsetting the text position based on the thickness
    for x_offset in range(-thickness, thickness + 1):
        for y_offset in range(-thickness, thickness + 1):
            if x_offset == 0 and y_offset == 0:
                continue
            screen.blit(outline, (position[0] + x_offset, position[1] + y_offset))

    # Render and draw the main text
    main_text = font.render(text, True, color)
    screen.blit(main_text, position)


def card_strength_text(screen, card, card_x, start_y, image):
    """
    Draws the strength text on a card's image based on various conditions such as
    the type of the card and the current strength relative to the original strength.
    This text visually represents the strength of a card during gameplay.

    Parameters:
    ----------
    screen : pygame.Surface
        The screen onto which the strength text should be drawn.
    card : Card
        The card object whose strength text will be rendered and drawn.
    card_x : int
        The x-coordinate where the text should start being drawn.
    start_y : int
        The y-coordinate where the text should start being drawn.
    image : pygame.Surface
        The surface of the card image where the text is drawn onto.

    Behavior:
    ---------
    - The function first checks if there's any strength text to draw.
    - The font size of the text is determined based on the width of the card image.
    - Text color is determined by the type of the card and its current strength relative to the original strength.
    - It then creates a rectangle area where the text will be centrally placed.
    - Finally, the text is rendered and drawn on the specified screen at the determined location and style.

    Notes:
    ------
    - Different colors are used to distinguish between different states of a card’s strength:
      black for normal units, white for heroes, green for units that have been buffed, and red for units that have
      been debuffed.
    - The text is drawn at a position relative to the card’s image, and its style may change dynamically
      based on the card's current state and type.
    """
    if card.strength_text is None:
        return

    font_size = 24

    # Adjusting font size based on the card image width
    if image.get_width() / 3.1 > 30:
        font_size = 31

    font_small = ResizableFont('Arial Narrow.ttf', font_size)

    # Determining text color based on card type and strength
    text_color = determine_text_color(card)

    # Creating a rectangle where the text will be drawn
    text_rect = pygame.Rect(card_x, start_y, image.get_width() / 2.7, image.get_height() / 4)

    # Rendering and drawing the strength text on the screen
    text = font_small.font.render(str(card.strength_text), True, text_color)
    draw_centered_text(screen, text, text_rect)


def determine_text_color(card):
    """
    Helper function to determine the color of the strength text based on the card type and strength.

    Parameters
    ----------
    card : Card
        The card object to determine the text color for.

    Returns
    -------
    tuple
        A tuple representing the RGB color of the text.
    """
    text_color = (0, 0, 0)  # Default color (black)

    if card.type == 'Hero':
        text_color = (255, 255, 255)  # White
    elif card.type == 'Unit':
        if card.strength == card.strength_text:
            text_color = (0, 0, 0)  # Black
        elif card.strength < card.strength_text:
            text_color = (0, 100, 0)  # Green
        elif card.strength > card.strength_text:
            text_color = (106, 28, 15)  # Red

    return text_color


def check_valid_action(card_board, card_dragged, game_state):
    """
    Checks whether an action performed during the game is valid. This function is involved in
    validating the action of dragging one card towards another. If the action is valid, it
    records the action parameters within the game state for further processing or reference.

    Parameters:
    ----------
    card_board : Card
        The card object which is targeted on the board, towards which another card is being dragged.

    card_dragged : Card
        The card object which is currently being dragged by the user.

    game_state : GameState
        The current state of the game, which holds various game parameters and states, and
        is used to record actions in the game.

    Behavior:
    ---------
    - The function first ensures that neither of the card parameters are None.
    - If both cards are valid, it records the action by appending the unique identifiers and
      the parent container row ID of the cards involved to the game_state's parameter_actions list.

    Note:
    -----
    The recorded action is stored as a string in the format: "dragged_card_id,target_row_id,target_card_id"
    """
    if card_board is None or card_dragged is None:
        pass
    else:
        game_state.parameter_actions.append(
            str(card_dragged.id) + ',' + str(card_board.parent_container.row_id) + ',' + str(card_board.id))


def load_and_scale_image(image_path, width, height):
    """
    Loads and scales an image from a given path.

    Parameters:
    ----------
    image_path : str
        The file path of the image to be loaded and scaled.

    Returns
    -------
    pygame.Surface
        The loaded and scaled image.
    """
    image = pygame.image.load(image_path)
    return pygame.transform.scale(image, (width, height))


data = load_file('Gwent.csv')


class Observer:
    """
    Represents an observer in the observer design pattern. This abstract base class
    is intended to be subclassed to implement a concrete observer. Observers
    are updated in response to changes in a subject they are attached to.

    Methods:
    -------
    update(self, subject)
        An abstract method that should be overridden in subclass to define
        the update behavior of the observer based on changes in the subject.
    """

    def update(self, subject):
        """
        Abstract method representing the update functionality which is triggered
        when changes occur in the subject this observer is attached to.

        Parameters:
        ----------
        subject : Subject
            The subject instance that has undergone changes. This parameter
            provides the necessary context for the observer to update its state
            or behavior based on changes in the subject.

        Raises:
        ------
        NotImplementedError
            This method is intended to be overridden in subclass.
        """
        raise NotImplementedError


class Subject:
    """
    Represents a subject in the observer design pattern. The Subject class
    maintains a list of observers and notifies them of changes, allowing for a
    decoupling of components where changes in the subject are automatically
    communicated to dependent observers.

    Attributes:
    ----------
    _observers : list
        A private list that holds the observers which are registered to
        the subject and will be notified upon changes.

    Methods:
    -------
    __init__(self)
        Initializes a new Subject instance, preparing an empty observer list.

    register(self, observer)
        Adds an observer to the subject's list of observers making the observer
        get notifications upon changes.

    unregister(self, observer)
        Removes an observer from the subject's list of observers stopping the
        observer from getting notifications upon changes.

    notify(self)
        Calls the update method on all registered observers, signaling a change
        in the subject's state.
    """

    def __init__(self):
        """
        Initializes a new Subject instance with an empty list of observers.
        """
        self._observers = []

    def register(self, observer):
        """
        Adds an observer to be notified of changes in the subject.

        Parameters:
        ----------
        observer : Observer
            An object that wishes to be notified when the state of the subject changes.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer):
        """
        Removes an observer, stopping them from being notified of changes in the subject.

        Parameters:
        ----------
        observer : Observer
            The object that will be removed from the list of observers.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self):
        """
        Notifies all registered observers of a change in the subject.
        Each observer has its update method called.
        """
        for observer in self._observers:
            observer.update(self)


class GameState(Subject):
    """
    Represents the current state of a game and manages notifications to observers
    when state changes occur. Inherits from the Subject class.

    Attributes:
    ----------
    state : str
        The current state of the game.
    previous_state : str
        The previous state of the game.
    parameter : various types
        Holds additional parameters or data relevant to the current state.
    parameter_actions : list
        Stores actions or methods associated with the current parameter.
    game_state_matrix : various types
        Possibly holds a matrix representing the game's state for the player.
    game_state_matrix_opponent : various types
        Possibly holds a matrix representing the game's state for the opponent.
    hovering_card : various types
        Stores a reference to a card object that is currently being hovered over.
    pause_menu_option : various types
        Holds the user-selected option from the pause menu.
    main_menu_option : various types
        Holds the user-selected option from the main menu.
    end_game_option : various types
        Holds the user-selected option from the end game menu.
    end_state : various types
        Contains information related to the end state of the game.
    ai : bool
        Indicates whether AI is currently active in the game.
    developer_tools : bool
        Enables or disables developer tools within the game.
    stepper : Stepper
        An instance of the Stepper class, managing game steps or turns.
    stepper_on : bool
        Indicates whether the stepper is currently active.
    game : Game
        Holds a reference to the main game object or instance.
    results_player : list of str
        Stores the results or scores for the player.
    results_opponent : list of str
        Stores the results or scores for the opponent.

    Methods:
    -------
    __init__(self)
        Initializes a new GameState object, setting up the initial state and other attributes.

    set_state(self, new_state)
        Updates the game's state and notifies all observers of the change.

    clear(self)
        Resets the GameState object attributes to prepare for a new game or round.
    """

    def __init__(self):
        """
        Initialize a new GameState.

        A GameState is a specific type of subject that represents the state of a game.
        """
        super().__init__()
        self.state = 'normal'
        self.previous_state = None
        self.parameter = None
        self.parameter_actions = []
        self.game_state_matrix = None
        self.game_state_matrix_opponent = None
        self.hovering_card = None
        self.pause_menu_option = None
        self.main_menu_option = None
        self.end_game_option = None
        self.end_state = None
        self.ai = True
        self.developer_tools = True
        self.stepper = Stepper(self)
        self.stepper_on = False
        self.game = None
        self.results_player = ['0', '0', '0']
        self.results_opponent = ['0', '0', '0']

    def set_state(self, new_state):
        """
        Updates the game's state and notifies all observers of the change.

        Parameters:
        ----------
        new_state : str
            The new state to set the game to.
        """
        self.state = new_state
        self.hovering_card = None
        self.notify()

    def clear(self):
        """
        Resets the GameState object attributes, clearing the current game state and
        preparing the object for a new game or round.
        """
        self.state = 'normal'
        self.parameter = None
        self.parameter_actions = []
        self.game_state_matrix = None
        self.game_state_matrix_opponent = None
        self.hovering_card = None
        self.pause_menu_option = None
        self.main_menu_option = None
        self.end_game_option = None
        self.end_state = None
        self.results_player = ['0', '0', '0']
        self.results_opponent = ['0', '0', '0']


class Card:
    """
    A class representing a Card in the game, complete with all relevant attributes
    and methods to manage the card's state and visual representation.

    Attributes:
    ----------
    id : int
        A unique identifier of the card.
    data : dict
        Dictionary containing all relevant information about the card.
    name : str
        Name of the card.
    strength : int
        Strength value of the card.
    ability : str
        The specific ability of the card.
    type : str
        The type/category of the card.
    placement : int
        The placement of the card.
    count : int
        The count/number of such cards.
    faction : str
        The faction to which the card belongs.
    image : str
        Filename of the card's image.
    hovering : bool
        A flag indicating whether the mouse cursor is hovering over the card.
    rect : pygame.Rect or None
        The rectangular area representing the card's position and size on the screen.
    is_dragging : bool
        A flag indicating whether the card is currently being dragged.
    mouse_offset : tuple
        The position of the mouse click relative to the top-left corner of the card.
    game_state : GameState
        A GameState object that represents the current state of the game.
    hand : list or None
        The list representing the hand of cards that this card is a part of.
    position_hand : int
        The position of the card within the hand list.
    is_placed : bool
        A flag indicating whether the card is placed on the board.
    large_image : pygame.Surface
        A pygame Surface object representing the large version of the card's image.
    small_image : pygame.Surface
        A pygame Surface object representing the small version of the card's image.
    image_scaled : pygame.Surface or None
        The card's image scaled according to the card's current state.
    strength_text : str or None
        The strength of the card in text form.

    Methods:
    --------
    __init__(self, _id, data, game_state):
        Initializes the Card object with the given ID, data dictionary, and game state.
    render(self, screen):
        Draws a rectangular border around the card.
    draw(self, screen):
        Draws the card on the screen.
    handle_event(self, event):
        Handles mouse events related to the card, including starting and stopping dragging,
        and updating the card's position while dragging.
    """

    def __init__(self, _id, data_input, game_state):
        """
        Initializes the Card object with the given ID, data dictionary, and game state.

        Parameters:
        ----------
        _id : int
            The unique identifier of the card.
        data : dict
            A dictionary containing all relevant information about the card.
        game_state : GameState
            The current state of the game.
        """
        self.id = _id
        self.data = data_input[_id]
        self.name = self.data['Name']
        self.strength = self.data['Strength']
        self.ability = self.data['Ability']
        self.type = self.data['Type']
        self.placement = self.data['Placement']
        self.count = self.data['Count']
        self.faction = self.data['Faction']
        self.image = self.data['Image']
        self.hovering = False
        self.rect = None
        self.is_dragging = False  # Track whether the component is currently being dragged
        self.mouse_offset = (0, 0)  # Track where the mouse was clicked relative to the top left corner of the component
        self.game_state = game_state
        self.hand = None
        self.position_hand = -1
        self.is_placed = False
        self.parent_container = None
        self.hovering_x = None
        self.hovering_y = None
        self.hovering_image = None
        self.hovering_text = False

        # Initialize the large and small images
        self.large_image = self.data['Image_lg']
        self.small_image = self.data['Image_sm']

        # Create the image attribute by adding smaller images to the small image
        self.image = self.small_image.copy()
        self.image_scaled = None
        self.strength_text = None

        # Add the appropriate icon to the top left corner of the image
        type_icon = self.data['Type_icon']

        if type_icon is not None:
            self.image.blit(type_icon, (0, 0))  # top left corner

        # If card type is Hero or Unit, add another icon to the bottom right of the image
        if self.type in ["Hero", "Unit"]:
            self.strength_text = self.strength
            placement_icons = ['img/icons/card_row_close.png', 'img/icons/card_row_ranged.png',
                               'img/icons/card_row_siege.png']
            placement_icon = pygame.image.load(placement_icons[self.placement])
            self.image.blit(placement_icon, (self.small_image.get_width() - placement_icon.get_width(),
                                             self.small_image.get_height() - placement_icon.get_height()))  # bottom
            # right corner

            # If card type is Hero or Unit, add ability icon to the bottom right, left to previous icon
            if self.type in ["Hero", "Unit"] and self.ability in ["Spy", "Bond", "Morale", "Medic", "Muster"]:
                ability_icon = self.data['Ability_icon']
                self.image.blit(ability_icon, (
                    self.small_image.get_width() - placement_icon.get_width() - ability_icon.get_width(),
                    self.small_image.get_height() - ability_icon.get_height()))  # left to the previous icon

    def render(self, screen):
        """
        Draws a rectangular border around the card.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen onto which the card should be drawn.
        """
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def draw(self, screen):
        """
        Draws the card on the screen with its image and strength text.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen onto which the card should be drawn.
        """
        screen.blit(scale_surface(self.image, (self.rect.width, self.rect.height)), (self.rect.x, self.rect.y))
        card_strength_text(screen, self, self.rect.x, self.rect.y, self.image_scaled)

    def handle_event(self, event):
        """
        Handles mouse events such as clicking and dragging related to the card. This method
        is responsible for determining the behavior of the card when it interacts with mouse
        events like MOUSEBUTTONDOWN, MOUSEBUTTONUP, and MOUSEMOTION. It updates the card's
        state and position based on the user's interaction.

        Parameters:
        ----------
        event : pygame.Event
            An event object that contains information about the mouse event,
            like the type of mouse event and the position of the mouse.

        Behavior:
        ---------
        1. MOUSEBUTTONDOWN:
            - If the mouse is clicked over the card, and the current game state is 'normal',
            and the card is not already placed in a row:
                - The game state is changed to 'dragging'.
                - The card’s dragging state is set to True.
                - The position of the mouse click relative to the card’s position is recorded.

        2. MOUSEBUTTONUP:
            - If the mouse button is released and the game state is 'normal':
                - It checks if an action is valid and performs the action if it is.
            - If the mouse button is released and the game state is 'dragging':
                - The game state is reverted to 'normal'.
                - The card’s dragging state is set to False.

        3. MOUSEMOTION:
            - If the mouse is moved while the card’s dragging state is True:
                - The card’s position is updated based on the current mouse position and the
                recorded mouse offset.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(
                event.pos) and self.game_state.state == 'normal' and (
                self.parent_container is not None and self.parent_container.row_id == -1):
            self.game_state.parameter = self
            self.game_state.set_state('dragging')
            self.is_dragging = True
            self.mouse_offset = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)

        elif event.type == pygame.MOUSEBUTTONUP and self.game_state.state == 'normal':
            if self.rect.collidepoint(event.pos) and self.game_state.parameter != self:
                check_valid_action(self, self.game_state.parameter, self.game_state)
        elif event.type == pygame.MOUSEBUTTONUP and self.game_state.state == 'dragging':
            self.game_state.set_state('normal')
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.rect.x = event.pos[0] - self.mouse_offset[0]
                self.rect.y = event.pos[1] - self.mouse_offset[1]


class Component(Observer):
    """
    A Component represents a graphical element in a Pygame application and is
    an Observer to changes in GameState objects.

    Attributes:
    ----------
    game_state : GameState
        The current state of the game.
    rect : pygame.Rect
        The rectangular area in which the component is drawn.
    width : int
        Width of the component in pixels.
    height : int
        Height of the component in pixels.
    x : int
        x-coordinate of the top left corner of the component.
    y : int
        y-coordinate of the top left corner of the component.
    font_small : pygame.font.Font
        A resizable font to be used within the component.

    Methods:
    -------
    __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio=0, y_ratio=0)
        Initializes the component with the specified ratios and subscribes it to game_state.
    render(screen)
        Draws the component on the given screen.
    update(subject)
        Handles updates from the observed subject (GameState).
    handle_event(event)
        Handles Pygame events.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio=0.0, y_ratio=0.0):
        """
        Initializes the Component with relative dimensions and positions based on
        the given ratios. The Component also gets registered to observe game_state.

        Parameters:
        ----------
        game_state : GameState
            The current state of the game to observe.
        parent_rect : pygame.Rect
            Rectangle of the parent component.
        width_ratio : float
            Ratio of the component’s width to the parent's width.
        height_ratio : float
            Ratio of the component’s height to the parent's height.
        x_ratio : float, optional
            Horizontal position ratio relative to the parent component (default is 0).
        y_ratio : float, optional
            Vertical position ratio relative to the parent component (default is 0).
        """
        self.width = int(parent_rect.width * width_ratio)
        self.height = int(parent_rect.height * height_ratio)
        self.x = parent_rect.x + int(parent_rect.width * x_ratio)
        self.y = parent_rect.y + int(parent_rect.height * y_ratio)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.game_state = game_state
        self.game_state.register(self)
        self.font_small = ResizableFont('Gwent.ttf', 50)

    def render(self, screen):
        """
        Draws a red rectangle on the screen representing the component.

        Parameters:
        -----------
        screen : pygame.Surface
            The surface on which the component is to be drawn.
        """
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)

    def update(self, subject):
        """
        Responds to change in the GameState object. By default, this method does nothing.
        Subclasses can override this method to take action when the game state changes.

        Parameters:
        -----------
        subject : Subject
            The Subject object (typically a GameState object) that has just changed.
        """
        # By default, do nothing when the game state changes.
        # Specific subclasses can override this method to take action when the game state changes.
        pass

    def handle_event(self, event):
        """
        Responds to a Pygame event. By default, this method does nothing.
        Subclasses can override this method to take action when the event occurs.

        Parameters:
        -----------
        event : pygame.Event
            The event that occurred.
        """
        # By default, do nothing when the event occurs.
        # Specific subclasses can override this method to take action when the event occurs.
        pass


class PanelLeft(Component):
    """
    A class that represents a Panel on the left side of the screen in Pygame.

    This class is a subclass of the Component class and is responsible for handling the rendering
    of various components like the Weather, LeaderBox, LeaderContainer, LeaderActive, and Stats.

    Attributes:
    ----------
    weather : Weather
        The Weather component of the panel.
    leader_box_op : LeaderBox
        The LeaderBox component for the opponent.
    leader_container_op : LeaderContainer
        The LeaderContainer component for the opponent.
    leader_active_op : LeaderActive
        The LeaderActive component for the opponent.
    stats_op : Stats
        The Stats component for the opponent.
    leader_box_me : LeaderBox
        The LeaderBox component for the player.
    leader_container_me : LeaderContainer
        The LeaderContainer component for the player.
    leader_active_me : LeaderActive
        The LeaderActive component for the player.
    stats_me : Stats
        The Stats component for the player.

    Methods:
    --------
    __init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the PanelLeft by setting up its attributes, such as the weather,
        leader boxes, leader containers, active leaders, and stats.

    setup_leader_stats(game_state, y_ratio_lb, y_ratio_stats, is_opponent)
        Sets up the leader and stats components, configuring their positions and sizes
        based on the given ratios and whether they belong to the opponent or the player.

    draw(screen)
        Draws the stats and weather components, as well as the leader boxes, containers,
        and active leaders, on the specified screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the PanelLeft by setting up its components with the appropriate sizes
        and positions based on the given ratios.

        Parameters:
        ----------
        game_state : object
            The state of the game.
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The ratio of the panel's width to its parent's width.
        height_ratio : float
            The ratio of the panel's height to its parent's height.
        x_ratio : float
            The ratio of the panel's x-coordinate to its parent's width.
        y_ratio : float
            The ratio of the panel's y-coordinate to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)

        self.leader_box_op = None
        self.leader_container_op = None
        self.leader_active_op = None
        self.stats_op = None
        self.leader_box_me = None
        self.leader_container_me = None
        self.leader_active_me = None
        self.stats_me = None
        self.weather = Weather(game_state, self, 0.549, 0.1275, 0.279, 0.416)
        self.setup_leader_stats(game_state, 0.0755, 0.2425, True)
        self.setup_leader_stats(game_state, 0.7755, 0.6175, False)

    def setup_leader_stats(self, game_state, y_ratio_lb, y_ratio_stats, is_opponent):
        """
        Sets up the leader and stats components.

        Parameters:
        ----------
        game_state : object
            The state of the game.
        y_ratio_lb : float
            The ratio of the leader box's y-coordinate to the parent's height.
        y_ratio_stats : float
            The ratio of the stats' y-coordinate to the parent's height.
        is_opponent : bool
            A flag indicating whether the stats are for the opponent or the player.
        """
        leader_box = LeaderBox(game_state, self.rect, 0.314, 0.125, 0.275, y_ratio_lb)
        leader_container = LeaderContainer(game_state, self.rect, 0.63, 1)
        leader_active = LeaderActive(game_state, self.rect, 0.24, 0.28, 0.75, 0.33)
        stats = Stats(game_state, self.rect, 0.89, 0.125, 0, y_ratio_stats, is_opponent)

        if is_opponent:
            self.leader_box_op = leader_box
            self.leader_container_op = leader_container
            self.leader_active_op = leader_active
            self.stats_op = stats
        else:
            self.leader_box_me = leader_box
            self.leader_container_me = leader_container
            self.leader_active_me = leader_active
            self.stats_me = stats

    def draw(self, screen):
        """
        Draws the components on the screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The surface on which the components are to be drawn.
        """
        self.stats_op.draw(screen)
        self.weather.draw(screen)
        self.stats_me.draw(screen)


class LeaderBox(Component):
    """
    A class that represents a LeaderBox, a UI component in Pygame.

    This class is a subclass of the Component class and represents a graphical
    component that usually contains an image or text representing a "leader"
    in a game.

    Attributes:
    ----------
    game_state : object
        The state of the game, it contains various information about the game's current state.
    parent_rect : pygame.Rect
        The rectangle representing the area of the parent component.
    rect : pygame.Rect
        The rectangle representing the area of this component.

    Methods:
    --------
    __init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the LeaderBox with the specified attributes including its position and size relative to its parent.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the LeaderBox with relative position and size based on the parent component.

        Parameters:
        -----------
        game_state : object
            An object representing various states of the game.
        parent_rect : pygame.Rect
            The rectangle object that represents the parent component's area.
        width_ratio : float
            The ratio of the LeaderBox's width to its parent's width, determining the width of the LeaderBox.
        height_ratio : float
            The ratio of the LeaderBox's height to its parent's height, determining the height of the LeaderBox.
        x_ratio : float
            The ratio of the LeaderBox's x-coordinate (left edge) to its parent's width, determining the horizontal
            position of the LeaderBox within the parent.
        y_ratio : float
            The ratio of the LeaderBox's y-coordinate (top edge) to its parent's height, determining the vertical
            position of the LeaderBox within the parent.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)


class LeaderContainer(Component):
    """
    A class that represents a LeaderContainer, a specific UI component in Pygame.

    This class is a subclass of the Component class and is used to contain a
    "leader" representation, usually an image or text. It is designed to be always
    centered within its parent component, typically a LeaderBox.

    Attributes:
    ----------
    game_state : object
        An object representing various states of the game.
    parent_rect : pygame.Rect
        The rectangle representing the area of the parent component.
    rect : pygame.Rect
        The rectangle representing the area of this component.
    x : int
        The x-coordinate of the top-left corner of the LeaderContainer.
    y : int
        The y-coordinate of the top-left corner of the LeaderContainer.
    width : int
        The width of the LeaderContainer.
    height : int
        The height of the LeaderContainer.

    Methods:
    --------
    __init__(game_state, parent_rect, width_ratio, height_ratio)
        Initializes the LeaderContainer with specified attributes and ensures it is centered within the parent
        component.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio):
        """
        Initializes the LeaderContainer.

        The LeaderContainer is always centered within its parent component, which is
        typically a LeaderBox. After initialization, the LeaderContainer's x and y
        coordinates are updated to ensure it's centered within the parent component.
        Consequently, its 'rect' attribute is updated to reflect the new position.

        Parameters:
        -----------
        game_state : object
            An object representing various states of the game.
        parent_rect : pygame.Rect
            The rectangle object that represents the parent component's area.
        width_ratio : float
            The ratio of the LeaderContainer's width to its parent's width. Determines the width of the LeaderContainer.
        height_ratio : float
            The ratio of the LeaderContainer's height to its parent's height. Determines the height of the
            LeaderContainer.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio)
        # Center the LeaderContainer within its parent component.
        self.x = parent_rect.x + (parent_rect.width - self.width) // 2
        self.y = parent_rect.y + (parent_rect.height - self.height) // 2
        # Update the rect with the new x, y coordinates
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


class LeaderActive(Component):
    """
    A class that represents a LeaderActive, a specific UI component in Pygame.

    This class is a subclass of the Component class and is used to indicate the active "leader".
    Its size and position are relative to its parent, which is typically a LeaderBox.

    Attributes:
    ----------
    game_state : object
        An object representing various states of the game.
    parent_rect : pygame.Rect
        The rectangle representing the area of the parent component.
    rect : pygame.Rect
        The rectangle representing the area of this component.
    x : int
        The x-coordinate of the top-left corner of the LeaderActive.
    y : int
        The y-coordinate of the top-left corner of the LeaderActive.
    width : int
        The width of the LeaderActive.
    height : int
        The height of the LeaderActive.

    Methods:
    --------
    __init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the LeaderActive with specified attributes, positioning it within the parent component.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the LeaderActive.

        The LeaderActive is positioned within its parent component, which is typically a LeaderBox,
        with its size and position being relative to its parent.

        Parameters:
        -----------
        game_state : object
            An object representing various states of the game.
        parent_rect : pygame.Rect
            The rectangle object that represents the parent component's area.
        width_ratio : float
            The ratio of the LeaderActive's width to its parent's width. Determines the width of the LeaderActive.
        height_ratio : float
            The ratio of the LeaderActive's height to its parent's height. Determines the height of the LeaderActive.
        x_ratio : float
            The ratio of the LeaderActive's x position to its parent's width. Determines the horizontal position of
            the LeaderActive within the parent.
        y_ratio : float
            The ratio of the LeaderActive's y position to its parent's height. Determines the vertical position of
            the LeaderActive within the parent.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)  # 24% of the leader_box width, 28% of the leader_box height, positioned within the
        # leader_box


class Stats(Component):
    """
    A class that represents Stats, a specific UI component in Pygame.

    This class is a subclass of the Component class and is used to display various statistical information
    about the game state, such as player names, deck names, hand count, and total score.

    Attributes:
    ----------
    game_state : object
        An object representing various states of the game.
    parent_rect : pygame.Rect
        The rectangle representing the area of the parent component.
    rect : pygame.Rect
        The rectangle representing the area of this component.
    font_small : ResizableFont
        A font object used for rendering text.
    surface : pygame.Surface
        A pygame Surface object where the stats components are drawn.
    is_opponent : bool
        A flag indicating whether the stats are for the opponent or not.
    profile_image : ProfileImage
        An object representing the profile image.
    name : PlayerName
        An object representing the player's name.
    deck_name : DeckName
        An object representing the deck name.
    hand_count : HandCount
        An object representing the hand count.
    gem1 : Gem
        An object representing the first gem.
    gem2 : Gem
        An object representing the second gem.
    score_total : ScoreTotal
        An object representing the score total.
    passed : Passed
        An object indicating whether a player has passed.

    Methods:
    --------
    __init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent)
        Initializes the Stats component with the necessary attributes and UI elements.
    create_profile_image(is_opponent: bool) -> ProfileImage
        Creates and returns a ProfileImage instance for the current Stats instance.
    create_name(is_opponent: bool) -> PlayerName
        Creates and returns a PlayerName instance for the current Stats instance.
    create_deck_name(deck_name: str, is_opponent: bool) -> DeckName
        Creates and returns a DeckName instance for the current Stats instance.
    create_hand_count(is_opponent: bool) -> HandCount
        Creates and returns a HandCount instance for the current Stats instance.
    create_gem(x_ratio: float, is_opponent: bool) -> Gem
        Creates and returns a Gem instance for the current Stats instance.
    create_score_total(is_opponent: bool) -> ScoreTotal
        Creates and returns a ScoreTotal instance for the current Stats instance.
    draw(screen: pygame.Surface)
        Draws the stats components on the provided pygame.Surface.
    update(subject)
        Updates the stats based on the game state.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes the Stats component.

        Parameters:
        -----------
        game_state : object
            The current state of the game.
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The ratio of the Stats' width to its parent's width.
        height_ratio : float
            The ratio of the Stats' height to its parent's height.
        x_ratio : float
            The ratio of the Stats' x position to its parent's width.
        y_ratio : float
            The ratio of the Stats' y position to its parent's height.
        is_opponent : bool
            A flag that represents whether the Stats are for the opponent or the player.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.font_small = ResizableFont('Gwent.ttf', 24)
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((20, 20, 20))
        self.surface.set_alpha(128)
        self.is_opponent = is_opponent
        self.profile_image = self.create_profile_image(is_opponent)
        self.name = self.create_name(is_opponent)
        self.deck_name = self.create_deck_name("Monsters", is_opponent)
        self.hand_count = self.create_hand_count(is_opponent)
        self.gem1 = self.create_gem(0.8, is_opponent)
        self.gem2 = self.create_gem(0.7075, is_opponent)
        self.score_total = self.create_score_total(is_opponent)
        self.passed = Passed(game_state, self, 0.25, 0.25, 0.9, 0.87)

    def create_profile_image(self, is_opponent):
        """
        Creates a profile image for the stats instance.

        Parameters:
        -----------
        is_opponent : bool
            A flag indicating whether the image is for the opponent.

        Returns:
        --------
        ProfileImage
            The created profile image.
        """
        y_ratio = 0.096 if is_opponent else 0.096
        return ProfileImage(self.game_state, self, 0.219, 0.8, 0.284, y_ratio, 'monsters', is_opponent)

    def create_name(self, is_opponent):
        """
        Creates a player name for the stats instance.

        Parameters:
        -----------
        is_opponent : bool
            A flag indicating whether the name is for the opponent.

        Returns:
        --------
        PlayerName
            The created player name.
        """
        y_ratio = 0 if is_opponent else 0.56
        return PlayerName(self.game_state, self, 0.47, 0.2, 0.53, y_ratio, is_opponent)

    def create_deck_name(self, deck_name, is_opponent):
        """
        Creates a deck name for the stats instance.

        Parameters:
        -----------
        deck_name : str
            The name of the deck.
        is_opponent : bool
            A flag indicating whether the deck name is for the opponent.

        Returns:
        --------
        DeckName
            The created deck name.
        """
        y_ratio = 0.25 if is_opponent else 0.80
        return DeckName(self.game_state, self.rect, 0.47, 0.125, 0.53, y_ratio, deck_name)

    def create_hand_count(self, is_opponent):
        """
        Creates a hand count for the stats instance.

        Parameters:
        -----------
        is_opponent : bool
            A flag indicating whether the hand count is for the opponent.

        Returns:
        --------
        HandCount
            The created hand count.
        """
        y_ratio = 0.585 if is_opponent else 0.185
        return HandCount(self.game_state, self.rect, 0.17, 0.295, 0.5325, y_ratio)

    def create_gem(self, x_ratio, is_opponent):
        """
        Creates a gem for the stats instance.

        Parameters:
        -----------
        x_ratio : float
            The ratio of the gem's x position to its parent's width.
        is_opponent : bool
            A flag indicating whether the gem is for the opponent.

        Returns:
        --------
        Gem
            The created gem.
        """
        y_ratio = 0.56 if is_opponent else 0.145
        return Gem(self.game_state, self, 0.09, 0.31, x_ratio, y_ratio)

    def create_score_total(self, is_opponent):
        """
        Creates a score total for the stats instance.

        Parameters:
        -----------
        is_opponent : bool
            A flag indicating whether the score total is for the opponent.

        Returns:
        --------
        ScoreTotal
            The created score total.
        """
        x_ratio = 0.94 if is_opponent else 0.944
        score_total = ScoreTotal(self.game_state, self, 0.12, 0.4, x_ratio, 0.32, is_opponent)
        score_total.set_score(300, True)
        return score_total

    def draw(self, screen):
        """
        Draws all the elements of the stats instance onto the provided Pygame surface.

        Parameters:
        -----------
        screen : pygame.Surface
            The surface onto which the elements should be drawn.
        """
        screen.blit(self.surface, (self.x, self.y))
        self.profile_image.draw(screen)
        self.name.draw(screen)
        self.deck_name.draw(screen)
        self.hand_count.draw(screen)
        self.gem1.draw(screen)
        self.gem2.draw(screen)
        self.score_total.draw(screen)
        self.passed.draw(screen)

    def update(self, subject):
        """
        Updates the display components based on the game state.

        Parameters:
        -----------
        subject : object
            The subject that potentially has changes that the Stats instance
            should be aware of, mainly the game state.

        """
        if subject is self.game_state and self.game_state.state == 'normal':
            # The game has returned to the 'normal' state, so enable card hovering.
            if self.is_opponent:
                if self.game_state.game_state_matrix[0][147] > 0:
                    self.passed.passed_bool = True
                else:
                    self.passed.passed_bool = False
                self.score_total.set_score(int(self.game_state.game_state_matrix[0][146]), False)
                if self.game_state.game_state_matrix[0][146] > self.game_state.game_state_matrix[0][145]:
                    self.score_total.set_score(int(self.game_state.game_state_matrix[0][146]), True)
                self.hand_count.text = int(self.game_state.game_state_matrix[0][126])
                if self.game_state.game_state_matrix[0][124] < 2:
                    self.gem2.on = False
                    if self.game_state.game_state_matrix[0][124] < 1:
                        self.gem1.on = False
                    else:
                        self.gem1.on = True
                else:
                    self.gem2.on = True
            else:
                self.score_total.set_score(int(self.game_state.game_state_matrix[0][145]), False)
                if self.game_state.game_state_matrix[0][145] > self.game_state.game_state_matrix[0][146]:
                    self.score_total.set_score(int(self.game_state.game_state_matrix[0][145]), True)
                self.hand_count.text = int(self.game_state.game_state_matrix[0][125])
                if self.game_state.game_state_matrix[0][123] < 2:
                    self.gem2.on = False
                    if self.game_state.game_state_matrix[0][123] < 1:
                        self.gem1.on = False
                    else:
                        self.gem1.on = True
                else:
                    self.gem2.on = True


class ProfileImage(Component):
    """
    This class represents a player's profile image in a game. It handles the initialization,
    scaling, and drawing of the profile image, background, and faction images on the game screen.

    Attributes:
    ----------
    game_state : GameState
        An object representing the state of the game.
    opponent : bool
        Flag indicating if the profile image belongs to the opponent.
    profile_img_pic : pygame.Surface
        Surface containing the scaled player's profile image.
    background_image : pygame.Surface
        Surface containing the scaled background image of the profile.
    faction_img_pic : pygame.Surface
        Surface containing the scaled faction image of the player.

    Methods
    -------
    draw(screen: pygame.Surface)
        Draw the profile image, its background, and the faction image onto the given screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, faction, opponent):
        """
        Initializes a new instance of ProfileImage with the specified attributes and scaled images.

        Parameters:
        ----------
        game_state : GameState
            An object representing the current state of the game.
        parent_rect : pygame.Rect
            Rectangle of the parent container.
        width_ratio : float
            The ratio of this component's width to its parent's width.
        height_ratio : float
            The ratio of this component's height to its parent's height.
        x_ratio : float
            The ratio of this component's x position to its parent's width.
        y_ratio : float
            The ratio of this component's y position to its parent's height.
        faction : str
            Faction to which the player belongs, used to load the respective faction image.
        opponent : bool
            Flag indicating whether this profile image is for the opponent.
        """
        super().__init__(game_state,
                         parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)
        self.opponent = opponent
        self.profile_img_pic = pygame.image.load('img/icons/profile.png')
        self.profile_img_pic = pygame.transform.scale(self.profile_img_pic, (self.width, self.height))
        self.background_image = pygame.image.load('img/icons/icon_player_border.png')
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (int(self.width * 1.18), int(self.height * 1.18)))
        self.faction_img_pic = pygame.image.load(f'img/icons/deck_shield_{faction}.png')
        self.faction_img_pic = pygame.transform.scale(self.faction_img_pic,
                                                      (int(self.background_image.get_width() * 0.43),
                                                       int(self.background_image.get_height() * 0.43)))

    def draw(self, screen):
        """
        Draws the profile image, its background, and the faction image onto the given screen.
        The method handles the positioning and blitting of images on the screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen onto which the images should be drawn.
        """
        screen.blit(self.profile_img_pic, (self.x, self.y))
        screen.blit(self.background_image, (self.x - int(self.width * 0.1), self.y - int(self.height * 0.06)))
        if self.opponent:
            screen.blit(self.faction_img_pic,
                        (self.x - int(self.width * 0.1) - int(self.background_image.get_width() * 0.105),
                         self.y - int(self.background_image.get_height() * 0.05)))
        else:
            screen.blit(self.faction_img_pic,
                        (self.x - int(self.width * 0.1) - int(self.background_image.get_width() * 0.105),
                         self.y + int(self.background_image.get_height() * 0.58)))


class PlayerName(Component):
    """
    This class represents a player's name displayed on the game screen. It handles
    the initialization, rendering, and drawing of the player's name text.

    Attributes:
    ----------
    font_size : int
        The font size for rendering the player's name, calculated based on parent rectangle's height and height_ratio.
    font : pygame.font.Font
        The font to be used for rendering the player's name, loaded and resized according to the font size.
    text : pygame.Surface
        Surface containing the rendered player's name in the specified font and size.

    Methods:
    -------
    draw(screen: pygame.Surface)
        Draw the player's rendered name onto the given screen at the specified position.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes a new instance of PlayerName with the specified configurations,
        rendering the name as 'Player' or 'Opponent' based on the is_opponent flag.

        Parameters:
        ----------
        game_state : object
            An object representing the current state of the game.
        parent_rect : pygame.Rect
            Rectangle of the parent container.
        width_ratio : float
            The ratio of this component's width to its parent's width.
        height_ratio : float
            The ratio of this component's height to its parent's height.
        x_ratio : float
            The ratio of this component's x position to its parent's width.
        y_ratio : float
            The ratio of this component's y position to its parent's height.
        is_opponent : bool
            Flag indicating whether this name is for the opponent, affecting the rendered text.
        """
        super().__init__(game_state,
                         parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)
        self.font_size = int(parent_rect.height * height_ratio)  # 20% of the stats_op height
        self.font = ResizableFont('Arial Narrow.ttf', self.font_size)
        if is_opponent:
            self.text = self.font.font.render('Opponent', True, (218, 165, 32))  # RGB white color
        else:
            self.text = self.font.font.render('Player', True, (218, 165, 32))  # RGB white color

    def draw(self, screen):
        """
        Draws the rendered player's name onto the given screen, positioning it based on x and y coordinates.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the rendered name should be drawn.
        """
        screen.blit(self.text, (self.x, self.y))


class DeckName(Component):
    """
    This class represents a deck's name displayed on the game screen. It handles the
    initialization, rendering, and drawing of the deck's name text on the screen.

    Attributes:
    ----------
    font_size : int
        The font size for rendering the deck's name. It is calculated as a percentage of the parent rectangle's height.
    font : pygame.font.Font
        The font to be used for rendering the deck's name. A font object initialized with the specified font size.
    text : pygame.Surface
        Surface containing the rendered deck's name in the specified font, size, and color.

    Methods:
    -------
    draw(screen: pygame.Surface)
        Draws the rendered deck's name onto the given screen at the specified position.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, deck_name):
        """
        Initializes a new instance of DeckName by setting the visual configurations like
        font size, style, and rendered text based on the specified deck's name.

        Parameters:
        ----------
        game_state : object
            An object representing the current state of the game.
        parent_rect : pygame.Rect
            Rectangle of the parent container defining where the deck name should be drawn.
        width_ratio : float
            The ratio of this component's width to its parent's width.
        height_ratio : float
            The ratio of this component's height to its parent's height.
        x_ratio : float
            The ratio of this component's x position to its parent's width.
        y_ratio : float
            The ratio of this component's y position to its parent's height.
        deck_name : str
            The actual name of the deck to be displayed.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)
        self.font_size = int(parent_rect.height * height_ratio)  # 16% of the stats_op height
        self.font = ResizableFont('Arial Narrow.ttf', self.font_size)
        self.text = self.font.font.render(deck_name, True, (210, 180, 140))  # RGB for tan color

    def draw(self, screen):
        """
        Draws the rendered deck's name onto the specified screen, using the pre-calculated x and y positions.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen onto which the rendered deck's name should be drawn.
        """
        screen.blit(self.text, (self.x, self.y))


class Gem(Component):
    """
    This class represents a Gem component which is part of the game screen,
    handling its visual representation, and state changes.

    Attributes:
    ----------
    gem_on_image : pygame.Surface
        Surface containing the scaled image of the gem in its default state.
    gem_on_image_off : pygame.Surface
        Surface containing the scaled image of the gem in its "off" state.
    gem_on_image_on : pygame.Surface
        Surface containing the scaled image of the gem in its "on" state.
    on : bool
        A flag indicating the current state of the gem (True for on, False for off).

    Methods:
    -------
    draw(screen: pygame.Surface)
        Draws the gem onto the given screen based on its current state.
    change_gem(on: bool)
        Changes the state of the gem and updates its visual representation.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes a new instance of Gem, loading and scaling the necessary images,
        and setting the initial state.

        Parameters:
        ----------
        game_state : object
            An object representing the current state of the game.
        parent_rect : pygame.Rect
            Rectangle of the parent container defining where the gem should be drawn.
        width_ratio : float
            The ratio of this component's width relative to its parent's width.
        height_ratio : float
            The ratio of this component's height relative to its parent's height.
        x_ratio : float
            The ratio of this component's x position relative to its parent's width.
        y_ratio : float
            The ratio of this component's y position relative to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.gem_on_image = load_and_scale_image('img/icons/icon_gem_on.png', self.width, self.height)
        self.gem_on_image_off = load_and_scale_image('img/icons/icon_gem_off.png', self.width, self.height)
        self.gem_on_image_on = load_and_scale_image('img/icons/icon_gem_on.png', self.width, self.height)
        self.on = True

    def draw(self, screen):
        """
        Draws the gem onto the given screen.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the gem should be drawn.
        """
        if self.on:
            screen.blit(self.gem_on_image, (self.x, self.y))
        else:
            screen.blit(self.gem_on_image_off, (self.x, self.y))


class HandCount(Component):
    """
    This class represents a HandCount component which displays the number of cards in a player's hand
    on the game screen, including both the count text and an associated icon.

    Attributes:
    ----------
    font_small : ResizableFont
        A resizable font for rendering the hand count text.
    hand_count_image : pygame.Surface
        A surface containing the scaled hand count icon.
    hand_count_op_text_rect : pygame.Rect
        A rectangle defining the area where the hand count text is displayed.
    hand_count_op_text : pygame.Surface
        A surface containing the rendered hand count text.
    text : int
        The number of cards in hand to display.

    Methods:
    -------
    draw(screen: pygame.Surface)
        Draws the hand count icon and updated text onto the given screen.
    change_count(count: int)
        Updates the displayed hand count to a new value.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes a new instance of HandCount.

        Parameters
        ----------
        parent_rect : pygame.Rect
            Rectangle of the parent container.
        width_ratio : float
            The ratio of this component's width to its parent's width.
        height_ratio : float
            The ratio of this component's height to its parent's height.
        x_ratio : float
            The ratio of this component's x position to its parent's width.
        y_ratio : float
            The ratio of this component's y position to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)
        self.text = 0
        self.font_small = ResizableFont('Gwent.ttf', 24)
        self.hand_count_image = pygame.image.load('img/icons/icon_card_count.png')
        self.hand_count_image = scale_surface(self.hand_count_image, (self.width, self.height))
        self.hand_count_op_text_rect = pygame.Rect(self.x + self.hand_count_image.get_width(), self.y,
                                                   self.width - self.hand_count_image.get_width(), self.height)
        self.hand_count_op_text = fit_text_in_rect(str(self.text), self.font_small, (218, 165, 32),
                                                   self.hand_count_op_text_rect)

    def draw(self, screen):
        """
        Draws the hand count icon and text onto the given screen.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the hand count should be drawn.
        """
        self.hand_count_op_text = fit_text_in_rect(str(self.text), self.font_small, (218, 165, 32),
                                                   self.hand_count_op_text_rect)
        screen.blit(self.hand_count_image, (self.x, self.y))
        draw_centered_text(screen, self.hand_count_op_text, self.hand_count_op_text_rect)

    def change_count(self, count):
        """
        Changes the hand count displayed.

        Parameters
        ----------
        count : int
            The new hand count.
        """
        self.hand_count_op_text = fit_text_in_rect(str(count), self.font_small, (218, 165, 32),
                                                   self.hand_count_op_text_rect)


class ScoreTotal(Component):
    """
    Represents the total score of a player or opponent in the game. The score display includes
    an icon, numerical score, and a high-score indicator.

    Attributes:
    ----------
    is_opponent : bool
        Specifies whether this score is for the opponent.
    image : pygame.Surface
        The image representing the score total icon.
    font_small : ResizableFont
        The font used for displaying the score.
    text_color : tuple
        The RGB color of the score text.
    text_rect : pygame.Rect
        The area in which the score text will be displayed.
    text : pygame.Surface
        The rendered text surface of the score.
    high_score_image : pygame.Surface
        The image indicating a high score.
    high_score_rect : pygame.Rect
        The area in which the high score indicator will be displayed.
    high : bool
        A flag indicating whether the current score is a high score.
    score : str
        The current score as a string.

    Methods:
    -------
    set_score(score: int, high: bool)
        Update the displayed score and high-score status.
    draw(screen: pygame.Surface)
        Render the score, score icon, and high-score indicator on the screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes a new instance of ScoreTotal.

        Parameters:
        ----------
        parent_rect : pygame.Rect
            Rectangle of the parent container.
        width_ratio : float
            The ratio of this component's width to its parent's width.
        height_ratio : float
            The ratio of this component's height to its parent's height.
        x_ratio : float
            The ratio of this component's x position to its parent's width.
        y_ratio : float
            The ratio of this component's y position to its parent's height.
        is_opponent : bool
            Indicates whether this score total is for the opponent.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)  # 12% of the parent width, 40% of the parent height,
        # positioned at 94.5% of the parent width, 25% of the parent height
        self.is_opponent = is_opponent

        if self.is_opponent:
            self.image = pygame.image.load('img/icons/score_total_op.png')
        else:
            self.image = pygame.image.load('img/icons/score_total_me.png')

        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        self.font_small = ResizableFont('Gwent.ttf', 24)
        self.text_color = (0, 0, 0)
        self.text_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.text = None
        self.high_score_image = pygame.image.load('img/icons/icon_high_score.png')
        self.high_score_image = pygame.transform.scale(self.high_score_image,
                                                       (int(self.width * 1.95), int(self.height * 1.7)))
        self.high_score_rect = self.high_score_image.get_rect(
            topleft=(self.x + int(self.width * -0.46), self.y + int(self.height * -0.32)))
        self.high = False
        self.score = '0'

    def set_score(self, score, high):
        """
        Sets the score displayed and whether it is the high score.

        Parameters:
        ----------
        score : int
            The score to be displayed.
        high : bool
            Indicates whether this score is the high score.
        """
        self.text = fit_text_in_rect(str(score), self.font_small, self.text_color, self.text_rect)
        self.high = high
        self.score = str(score)

    def draw(self, screen):
        """
        Draws the score total icon and text, and the high score icon if this score is the high score, onto the given
        screen.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the score total and high score should be drawn.
        """
        screen.blit(self.image, (self.x, self.y))
        if self.high:
            screen.blit(self.high_score_image, self.high_score_rect)
        if self.text:
            # Determine the position to center the text
            pos_x = self.text_rect.x + (self.text_rect.width - self.text.get_width()) // 2
            pos_y = self.text_rect.y + (self.text_rect.height - self.text.get_height()) // 2

            # Draw the outlined text at the calculated position
            draw_text_with_outline(screen, self.score, self.font_small.font, self.text_color, (255, 255, 255),
                                   (pos_x, pos_y), thickness=2)


class Passed(Component):
    """
    This class represents a Passed component, which displays the text 'Passed' on the screen.

    Attributes:
    ----------
    font_size : int
        The size of the font used for the 'Passed' text.
    font : ResizableFont
        The font used for the 'Passed' text.
    text : pygame.Surface
        Surface containing the 'Passed' text.

    Methods
    -------
    draw(screen: pygame.Surface)
        Draw the 'Passed' text onto the given screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes a new instance of Passed.

        Parameters:
        ----------
        parent_rect : pygame.Rect
            Rectangle of the parent container.
        width_ratio : float
            The ratio of this component's width to its parent's width.
        height_ratio : float
            The ratio of this component's height to its parent's height.
        x_ratio : float
            The ratio of this component's x position to its parent's width.
        y_ratio : float
            The ratio of this component's y position to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)  # 0% height, 0% width, positioned at 90% of the parent width, 87% of the parent
        # height
        self.font_size = int(parent_rect.height * height_ratio)  # 16% of the stats_op height
        self.font = ResizableFont('Gwent.ttf', self.font_size)
        self.passed_bool = False
        self.text = self.font.font.render('Passed', True, (210, 180, 140))  # RGB white color

    def draw(self, screen):
        """
        Draws the 'Passed' text onto the given screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen onto which the 'Passed' text should be drawn.
        """
        if self.passed_bool:
            screen.blit(self.text, (self.x, self.y))


class Weather(Component):
    """
    This class represents a Weather component, responsible for displaying various weather conditions on the screen as
    card images.
    Inherits attributes and methods from the Component class.

    Attributes:
    ----------
    frost : Card
        A Card instance representing the 'frost' weather type.
    fog : Card
        A Card instance representing the 'fog' weather type.
    rain : Card
        A Card instance representing the 'rain' weather type.
    clear : Card
        A Card instance representing the 'clear' weather type.
    cards : list of Card
        A list containing Card instances representing the current weather conditions to be displayed.
    allow_hovering : bool
        A boolean that enables or disables the hover effect on weather cards.

    Methods:
    -------
    __init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes a new instance of the Weather class, setting up its visual representation and interactive
        properties.
    draw(screen: pygame.Surface)
        Draws the weather condition cards on the screen with hover effects and scaling.
    update(subject)
        Updates the state of the weather component based on changes in the game state, modifying its behavior and
        appearance.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes a new instance of Weather, setting up its position, size and weather cards.

        Parameters:
        ----------
        game_state
            The current state of the game.
        parent_rect : pygame.Rect
            The rectangle of the parent container where the Weather component will be displayed.
        width_ratio : float
            The ratio of the Weather component’s width to its parent's width.
        height_ratio : float
            The ratio of the Weather component’s height to its parent's height.
        x_ratio : float
            The ratio of the Weather component’s x position to its parent's width.
        y_ratio : float
            The ratio of the Weather component’s y position to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)  # 54.9% of the parent width, 12.75% of the parent height, positioned at 27.9% of
        # the parent width, 41.25% of the parent height
        self.cards = []
        self.frost = Card(60, data, game_state)
        self.fog = Card(61, data, game_state)
        self.rain = Card(62, data, game_state)
        self.clear = Card(63, data, game_state)
        self.allow_hovering = True

    def draw(self, screen):
        """
        Draws the weather condition cards onto the given screen. Handles the appearance, scaling, and hover effects
        of the weather cards.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen onto which the weather cards should be drawn.
        """
        # First, we scale down the card images to fit within the container
        if len(self.cards) > 0:
            for card in self.cards:
                card.image_scaled = scale_surface(card.image, (self.width, self.height))

            # Calculate the total width of the cards
            total_card_width = len(self.cards) * self.cards[0].image_scaled.get_width()
            overlap = 0
            if total_card_width > self.width:
                # If cards don't fit side by side, calculate the necessary overlap
                overlap = (total_card_width - self.width) / (len(self.cards) - 1)

            # Calculate the starting x position for the cards to center them
            start_x = self.x + (self.width - total_card_width + overlap * (len(self.cards) - 1)) / 2

            # Calculate the y position to center the cards vertically
            card_height = self.cards[0].image_scaled.get_height()
            start_y = self.y + (self.height - card_height) / 2

            # Get the mouse cursor position
            mouse_pos = pygame.mouse.get_pos()

            for i, card in enumerate(self.cards):
                card_x = start_x + i * (card.image_scaled.get_width() - overlap)
                card_rect = pygame.Rect(card_x, start_y, card.image_scaled.get_width(), card.image_scaled.get_height())
                # Check if the mouse is over the card
                card.hovering = False
                if card_rect.collidepoint(mouse_pos):
                    card.hovering = True
                    for j, card_2 in enumerate(self.cards):
                        if card is not card_2:
                            card_2.hovering = False

            for i, card in enumerate(self.cards):
                card_x = start_x + i * (card.image_scaled.get_width() - overlap)
                screen.blit(card.image_scaled, (card_x, start_y))

            # Draw hovered card
            for i, card in enumerate(self.cards):
                if card.hovering and self.allow_hovering:
                    hovering_image = card.image.copy()
                    hovering_image = scale_surface(hovering_image, (self.width * 1.2, self.height * 1.2))
                    card_x = start_x + i * (card.image_scaled.get_width() - overlap)
                    card.hovering_x = card_x
                    card.hovering_y = start_y
                    card.hovering_image = hovering_image
                    self.game_state.hovering_card = card
                    # screen.blit(hovering_image, (card_x, start_y))
                    # card_preview = CardPreview(self.game_state, screen.get_rect(), card)
                    # card_preview.draw(screen)
                    # if card.ability != '0':
                    #    card_description = CardDescription(self.game_state, screen.get_rect(), card)
                    #    card_description.draw(screen)

    def update(self, subject):
        """
        Handles updates to the Weather component based on changes in the game state. Modifies the behavior of weather
        cards, such as enabling or disabling hover effects, and updates the displayed weather conditions.

        Parameters:
        ----------
        subject
            The object that the Weather component observes for changes, usually represents the game state.
        """
        if subject is self.game_state and self.game_state.state == 'carousel':
            # The game has entered the 'carousel' state, so disable card hovering.
            self.allow_hovering = False
        elif subject is self.game_state and self.game_state.state == 'normal':
            # The game has returned to the 'normal' state, so enable card hovering.
            self.allow_hovering = True
            self.cards.clear()
            if self.game_state.game_state_matrix[0][120] > 0:
                self.cards.append(self.frost)
            if self.game_state.game_state_matrix[0][121] > 0:
                self.cards.append(self.fog)
            if self.game_state.game_state_matrix[0][122] > 0:
                self.cards.append(self.rain)
        elif subject is self.game_state and self.game_state.state == 'dragging':
            # The game has returned to the 'normal' state, so enable card hovering.
            self.allow_hovering = False


class RowScore(Component):
    """
    Represents a Score for a particular Row in a Pygame display, inheriting from the Component class.
    It manages and displays scores within a specified area in the game interface.

    Attributes:
    ----------
    font_small : ResizableFont
        A ResizableFont object used for rendering the score text with adjustable sizes.
    text_color : tuple
        A tuple (R, G, B) representing the RGB color of the score text.
    text_rect : pygame.Rect
        A Rect object defining the area where the score text will be displayed.
    text : pygame.Surface or None
        A Surface object of the rendered text to be displayed, representing the score. None if no score is set.
    score : str
        A string representing the current score to be displayed.

    Methods:
    -------
    __init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the RowScore with positioning and sizing relative to a parent Rect, and initial visual
        configurations.
    set_score(score: int)
        Sets and updates the score to be displayed, also updates the text representation.
    draw(screen: pygame.Surface)
        Renders the score text, if available, onto the specified screen at the defined position with specified styles.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the RowScore object with positioning and sizing relative to the parent Rect.
        It also configures initial visual styles like font and text color.

        Parameters:
        ----------
        game_state : GameState
            The current state of the game.
        parent_rect : pygame.Rect
            The Rect of the parent component determining the positioning and sizing.
        width_ratio : float
            The width of RowScore as a ratio of parent's width.
        height_ratio : float
            The height of RowScore as a ratio of parent's height.
        x_ratio : float
            The x-coordinate of RowScore as a ratio of parent's width.
        y_ratio : float
            The y-coordinate of RowScore as a ratio of parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.font_small = ResizableFont('Gwent.ttf', 24)
        self.text_color = (0, 0, 0)
        self.text_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.text = None
        self.score = '0'

    def set_score(self, score):
        """
        Sets and prepares the score for display, converting it into a text Surface object.

        Parameters:
        ----------
        score : int
            The numerical score to be displayed.
        """
        self.text = fit_text_in_rect(str(score), self.font_small, self.text_color, self.text_rect)
        self.score = str(score)

    def draw(self, screen):
        """
        Draws the score text onto the given screen Surface. The text is positioned
        within the defined text_rect, and visual styles like outline are applied.

        Parameters:
        ----------
        screen : pygame.Surface
            The Surface where the score text will be rendered.
        """
        if self.text:
            pos_x = self.text_rect.x + (self.text_rect.width - self.text.get_width()) // 2
            pos_y = self.text_rect.y + (self.text_rect.height - self.text.get_height()) // 2

            # Draw the outlined text at the calculated position
            draw_text_with_outline(screen, self.score, self.font_small.font, self.text_color, (255, 255, 255),
                                   (pos_x, pos_y), thickness=2)


class FieldRow(Component):
    """
    Represents a Field Row in a Pygame display, inheriting from the Component class.
    It manages and displays elements such as scores, special conditions, and cards within a row.

    Attributes:
    ----------
    row_id : int
        An identifier for the row.
    row_score : RowScore
        An object managing and displaying the score within the row.
    row_special : RowSpecial
        An object managing and displaying special conditions in the row.
    row_cards : RowCards
        An object managing and displaying the cards placed within the row.
    is_opponent : bool
        A flag indicating if the row belongs to the opponent.
    weather_active : bool
        A flag indicating if weather effects are active in the row.
    weather_image : pygame.Surface
        An image representing the active weather effect.

    Methods:
    -------
    __init__(game_state, row_id, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent)
        Initializes the FieldRow object with positioning, sizing, and initial configurations.
    draw(screen)
        Renders the row, including scores, special conditions, and cards, onto the specified screen.
    handle_event(event)
        Delegates event handling to the row's cards.
    update(subject)
        Updates the state of the row based on changes in the game state.
    """

    def __init__(self, game_state, row_id, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes the FieldRow with positioning, sizing, and initial configurations like score,
        special conditions, and cards.

        Parameters
        ----------
        game_state : GameState
            The current state of the game.
        row_id : int
            An identifier for the row.
        parent_rect : pygame.Rect
            The Rect of the parent component determining positioning and sizing.
        width_ratio : float
            The width of FieldRow as a ratio of the parent's width.
        height_ratio : float
            The height of FieldRow as a ratio of the parent's height.
        x_ratio : float
            The x-coordinate of FieldRow as a ratio of parent's width.
        y_ratio : float
            The y-coordinate of FieldRow as a ratio of parent's height.
        is_opponent : bool
            A flag indicating if the row belongs to the opponent.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.row_id = row_id
        self.row_score = RowScore(game_state, self, 0.051, 0.4, 0.002, 0.31)
        self.row_special = RowSpecial(game_state, self, 0.1425, 1, 0.055, 0)
        self.row_cards = RowCards(self.row_id, game_state, self, 0.797, 1, 0.2, 0, is_opponent)
        self.is_opponent = is_opponent
        self.weather_active = False
        self.weather_image = None
        if self.row_id == 0:
            self.weather_image = pygame.image.load('img/icons/overlay_frost.png')
        elif self.row_id == 1:
            self.weather_image = pygame.image.load('img/icons/overlay_fog.png')
        else:
            self.weather_image = pygame.image.load('img/icons/overlay_rain.png')

    def draw(self, screen):
        """
        Draws the row’s elements like scores, special conditions, and cards on the given screen.
        It also manages the visual representation of weather effects.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen where the row and its elements will be rendered.
        """
        self.row_score.draw(screen)
        # self.row_score.render(screen)
        self.row_special.draw(screen)
        self.row_cards.draw(screen)
        if self.weather_active:
            weather_img = pygame.transform.smoothscale(self.weather_image,
                                                       (self.width - self.row_score.width, self.height))
            screen.blit(weather_img, (self.row_special.x, self.row_special.y))

    def handle_event(self, event):
        """
        Handles events by delegating them to the row's cards for processing.

        Parameters:
        ----------
        event : pygame.event.Event
            An event object representing various events like mouse clicks.
        """
        self.row_cards.handle_event(event)

    def update(self, subject):
        """
        Updates the state of the row, including scores, special conditions, and weather effects
        based on changes in the game state.

        Parameters
        ----------
        subject
            An object representing the part of the game state that has changed.
        """
        if subject is self.game_state and self.game_state.state == 'normal':
            if self.is_opponent:
                start_value = 7
                self.row_score.set_score(int(self.game_state.game_state_matrix[0][142 + self.row_id]))
                if self.game_state.game_state_matrix[0][136 + self.row_id] > 1 and \
                        self.game_state.game_state_matrix[start_value + self.row_id * 2][58] >= 1:
                    self.row_special.active = True
                else:
                    self.row_special.active = False
            else:
                start_value = 1
                self.row_score.set_score(int(self.game_state.game_state_matrix[0][139 + self.row_id]))
                if self.game_state.game_state_matrix[0][133 + self.row_id] > 1 and \
                        self.game_state.game_state_matrix[start_value + self.row_id * 2][58] >= 1:
                    self.row_special.active = True
                else:
                    self.row_special.active = False
            if self.game_state.game_state_matrix[0][120 + self.row_id] > 0:
                self.weather_active = True
            else:
                self.weather_active = False


class RowSpecial(Component):
    """
    Represents a special row in a Pygame display, inheriting from the Component class.
    Manages the rendering of a special row in the game interface, including the display
    of a special card and its effects.

    Attributes:
    ----------
    card : Card
        A special Card object to be displayed in this row.
    special_img : pygame.Surface
        A scaled image of the special card.
    active : bool
        Indicates whether the special row is active and the card should be displayed.
    allow_hovering : bool
        A flag that controls whether the hovering effect on the card is enabled.

    Methods:
    -------
    __init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the RowSpecial object with size, position, and other related configurations.
    draw(screen)
        Renders the special card and its hover effects on the given screen if the row is active.
    update(subject)
        Updates the state of the row, controlling hover-ability based on game state changes.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the RowSpecial with size, position, and other configurations like the special card.

        Parameters:
        ----------
        game_state
            The current state of the game.
        parent_rect : pygame.Rect
            The Rect of the parent component for positioning.
        width_ratio : float
            Ratio of RowSpecial’s width to its parent's width.
        height_ratio : float
            Ratio of RowSpecial’s height to its parent's height.
        x_ratio : float
            X-coordinate ratio of RowSpecial relative to the parent.
        y_ratio : float
            Y-coordinate ratio of RowSpecial relative to the parent.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.card = Card(58, data, game_state)
        self.special_img = scale_surface(self.card.image, (self.width, self.height * 0.9))
        self.active = True
        self.allow_hovering = True

    def draw(self, screen):
        """
        Renders the special card and its hover effects on the screen, considering its active state.
        Calculates the position to ensure the card is centered in the row.

        Parameters:
        ----------
        screen : pygame.Surface
            The display surface to draw the special card on.
        """
        if self.active:
            img_width, img_height = self.special_img.get_size()
            img_x = self.x + (self.width - img_width) // 2  # Calculate the centered x-coordinate
            img_y = self.y + (self.height - img_height) // 2  # Calculate the centered y-coordinate
            screen.blit(self.special_img, (img_x, img_y))

            # Get the mouse cursor position
            mouse_pos = pygame.mouse.get_pos()
            self.card.hovering = False
            card_rect = pygame.Rect(img_x, img_y, img_width, img_height)
            if card_rect.collidepoint(mouse_pos):
                self.card.hovering = True
            if self.card.hovering and self.allow_hovering:
                hovering_image = self.card.image.copy()
                self.card.hovering_image = scale_surface(hovering_image, (self.width * 1.2, self.height * 1.2))
                self.card.hovering_x = img_x
                self.card.hovering_y = img_y
                self.game_state.hovering_card = self.card

    def update(self, subject):
        """
        Updates the hover-ability of the card based on the game state changes,
        like entering and exiting the 'carousel' or 'dragging' states.

        Parameters:
        ----------
        subject
            An object representing the part of the game state being observed for changes.
        """
        if subject is self.game_state and self.game_state.state == 'carousel':
            # The game has entered the 'carousel' state, so disable card hovering.
            self.allow_hovering = False
        elif subject is self.game_state and self.game_state.state == 'normal':
            # The game has returned to the 'normal' state, so enable card hovering.
            self.allow_hovering = True
        elif subject is self.game_state and self.game_state.state == 'dragging':
            # The game has returned to the 'normal' state, so enable card hovering.
            self.allow_hovering = False


class RowCards(Component):
    """
    Represents a row of cards in a Pygame display, inheriting from the Component class.
    Manages and renders a container of Card objects within the game interface, allowing
    for the handling of user interactions and rendering of visual elements related to the cards.

    Attributes:
    ----------
    row_id
        Identifier for this row within the game’s context.
    card_container : CardContainer
        Manages a collection of cards and their interactions within this row.

    Methods:
    -------
    __init__(row_id, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent)
        Initializes the RowCards object with identifiers, spatial configurations and game state contexts.
    draw(screen)
        Renders the contained cards and their relevant visual components onto the game’s display.
    handle_event(event)
        Passes user interaction events to the card container for appropriate response or action.
    """

    def __init__(self, row_id, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Constructs and initializes a RowCards object with spatial, structural, and game state configurations.

        Parameters:
        ----------
        row_id
            A specific identifier for categorizing or referencing this row within the game.
        game_state
            Current operational state of the game, utilized for contextual behavior.
        parent_rect : pygame.Rect
            Reference rectangle, typically representing the spatial context of a parent graphical element.
        width_ratio : float
            Proportional width of the row relative to certain contextual or parent dimensions.
        height_ratio : float
            Proportional height of the row relative to certain contextual or parent dimensions.
        x_ratio : float
            Horizontal positional adjustment as a proportion of some contextual width.
        y_ratio : float
            Vertical positional adjustment as a proportion of some contextual height.
        is_opponent : bool
            Indicates whether the row is associated with an opponent player in the game.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.row_id = row_id
        self.card_container = CardContainer(row_id, game_state, self, 1, 1, 0, 0, is_opponent)

    def draw(self, screen):
        """
        Invokes the drawing functionalities of the card container, contributing to the game’s visual output.

        Parameters:
        ----------
        screen : pygame.Surface
            Target surface where the card container and its contents will be visually rendered.
        """
        self.card_container.draw(screen)

    def handle_event(self, event):
        """
        Entrusts the card container with handling received user interaction events, facilitating responsive behavior.

        Parameters:
        ----------
        event
            Encapsulates details and context regarding a specific user interaction or system event.
        """
        self.card_container.handle_event(event)


class CardPreview(Component):
    """
    Represents a preview display of a Card object within a Pygame interface,
    extending functionalities from the Component class. This class is responsible
    for managing and rendering a zoomed or detailed visual presentation of a specified
    Card object within the gaming interface.

    Attributes:
    ----------
    card : Card
        The specified Card object that is intended to be previewed or highlighted
        within the game interface.

    Methods:
    -------
    __init__(game_state, parent_rect, card)
        Constructs and initializes the CardPreview object with the necessary
        attributes and configurations.
    draw(screen)
        Handles the rendering process, drawing the detailed preview of the specified
        Card object onto the gaming interface.
    """

    def __init__(self, game_state, parent_rect, card):
        """
        Initializes the CardPreview object with necessary configurations and the
        specific Card object to be previewed.

        Parameters:
        ----------
        game_state
            The current state of the game, providing context for various functionalities.
        parent_rect : pygame.Rect
            The parent rectangular area within which the card preview will be displayed.
        card : Card
            The specific Card object which the preview will visually represent and detail.
        """
        super().__init__(game_state, parent_rect, 0.16, 0.55, 0.805, 0.205)
        self.card = card

    def draw(self, screen):
        """
        Draws the preview of the card on the screen.

        Parameters:
        -----------
        screen : pygame.Surface
            The surface on which the preview is to be drawn.
        """
        # Scale the large image of the card to fit within the preview area
        preview_image = scale_surface(self.card.large_image, (self.width, self.height))

        # Draw the preview
        screen.blit(preview_image, (self.x, self.y))


class CardDescription(Component):
    """
    Represents a detailed description display of a Card object within a Pygame interface,
    inheriting functionalities from the Component class. The class is dedicated to managing,
    rendering, and showcasing an elaborate and insightful description of a specified Card
    object’s abilities within the game interface, aiding in user comprehension and interaction.

    Attributes:
    ----------
    card : Card
        The specific Card object whose detailed abilities and attributes are intended to be
        described and showcased.
    image_text : str
        A textual representation of the card's ability, utilized in graphical representation.
    ability_icon : pygame.Surface
        A graphical icon symbolizing the particular ability of the Card object.
    name_font : pygame.font.Font
        The font style used for rendering the name of the ability.
    desc_font : pygame.font.Font
        The font style used for rendering the detailed description of the ability.

    Methods:
    -------
    __init__(self, game_state, parent_rect, card)
        Constructor responsible for initializing the CardDescription object with necessary attributes
        and configurations, preparing it for rendering.
    draw(self, screen)
        Handles the rendering process of the CardDescription object, managing the display of detailed
        information concerning the Card object’s abilities.
    """

    def __init__(self, game_state, parent_rect, card):
        """
        Constructs the CardDescription object, initializing it with essential configurations,
        attributes, and the specific Card object to be detailed.

        Parameters:
        ----------
        game_state
            Current state of the game, providing necessary context.
        parent_rect : pygame.Rect
            The rectangular area within which the card description will be positioned and displayed.
        card : Card
            The specific Card object whose details are meant to be showcased.
        """
        super().__init__(game_state, parent_rect, 29.12 / 100, 0.15, 67.95 / 100, 0.76)
        self.card = card

        self.image_text = self.card.ability.lower()
        if not self.card.type == 'Unit' and self.card.ability == 'Morale':
            self.image_text = 'horn'
        if self.card.ability == 'Weather':
            if self.card.placement == 0:
                self.image_text = 'frost'
            elif self.card.placement == 1:
                self.image_text = 'fog'
            elif self.card.placement == 2:
                self.image_text = 'rain'
            elif self.card.placement == 4:
                self.image_text = 'clear'

        # Load the ability icon and scale it down
        self.ability_icon = pygame.image.load(f'img/icons/card_ability_{self.image_text}.png')
        self.ability_icon = scale_surface(self.ability_icon,
                                          (self.width // 8, self.height // 4))  # adjust as necessary

        # Initialize fonts
        self.name_font = pygame.font.Font('Gwent.ttf', 48)  # adjust size as necessary
        self.desc_font = pygame.font.Font('Gwent.ttf', 24)  # adjust size as necessary

    def draw(self, screen):
        """
        Draws the description of the card on the screen.

        Parameters:
        -----------
        screen : pygame.Surface
            The surface on which the description is to be drawn.
        """
        # Draw the background
        background = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        background.fill((20, 20, 20, 250))  # adjust color and transparency as necessary
        screen.blit(background, (self.x, self.y))

        # Draw the ability icon
        screen.blit(self.ability_icon, (self.x, self.y))  # adjust position as necessary

        # Draw the name of the ability
        name_surface = self.name_font.render(self.card.ability, True, (255, 255, 255))  # adjust color as necessary
        name_rect = name_surface.get_rect(
            center=(self.x + self.width // 2, self.y + self.height // 4))  # adjust position as necessary
        screen.blit(name_surface, name_rect)

        # Draw the description of the ability
        # Use a placeholder text here. Replace it with the actual description.
        description = "This is a placeholder description for the ability."
        desc_surface = self.desc_font.render(description, True, (255, 255, 255))  # adjust color as necessary
        desc_rect = desc_surface.get_rect(
            center=(self.x + self.width // 2, self.y + self.height // 2))  # adjust position as necessary
        screen.blit(desc_surface, desc_rect)


class CardContainer(Component):
    """
    A class to create a container for Card objects in a Pygame display.

    This class is a subclass of the Component class. It manages and renders
    multiple Card objects on the game interface in a container layout.

    Attributes:
    ----------
    row_id : int
        Identifier for the row in the game.
    is_opponent : bool
        A flag indicating if the container belongs to the opponent.
    cards : list
        The list of Card objects to be displayed in the container.
    allow_hovering : bool
        A flag to allow or disallow hovering effects on the cards.

    Methods:
    --------
    __init__(self, row_id, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent)
        Initializes the CardContainer object with specified parameters.
    draw(self, screen)
        Draws the Card objects in the container onto the provided screen.
    create_card_rect()
        Creates rectangles for the cards for collision detection.
    update(self, subject)
        Updates the container based on the changes in the game state.
    handle_event(self, event)
        Handles the user input event, mainly mouse button up event.
    """

    def __init__(self, row_id, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes the CardContainer.

        Parameters:
        -----------
        row_id : int
            Identifier for the row in the game.
        game_state : GameState
            The current state of the game.
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The width ratio for sizing.
        height_ratio : float
            The height ratio for sizing.
        x_ratio : float
            The x-coordinate ratio for positioning.
        y_ratio : float
            The y-coordinate ratio for positioning.
        is_opponent : bool
            A flag indicating if the container belongs to the opponent.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.is_opponent = is_opponent
        self.row_id = row_id
        self.cards = []
        self.allow_hovering = True

    def draw(self, screen):
        """
        Draws the Card objects in the container on the screen.

        Parameters:
        -----------
        screen : pygame.Surface
            The surface on which the Card objects are to be drawn.
        """
        if len(self.cards) > 0:
            # First, we scale down the card images to fit within the container
            card_width = None
            for card in self.cards:
                card.image_scaled = scale_surface(card.image, (self.width, self.height * 0.95))
                card_width = card.image_scaled.get_width()

            # Calculate the total width of the cards
            total_card_width = len(self.cards) * card_width
            overlap = 0
            if total_card_width > self.width:
                # If cards don't fit side by side, calculate the necessary overlap
                overlap = (total_card_width - self.width) / (len(self.cards) - 1)

            # Calculate the starting x position for the cards to center them
            start_x = self.x + (self.width - total_card_width + overlap * (len(self.cards) - 1)) / 2

            # Calculate the y position to center the cards vertically
            card_height = self.cards[0].image_scaled.get_height()
            start_y = self.y + (self.height * 0.95 - card_height) / 2

            # Get the mouse cursor position
            mouse_pos = pygame.mouse.get_pos()

            for i, card in enumerate(self.cards):
                card_x = start_x + i * (card.image_scaled.get_width() - overlap)
                card_rect = pygame.Rect(card_x, start_y, card.image_scaled.get_width(), card.image_scaled.get_height())
                card.rect = card_rect
                # Check if the mouse is over the card
                card.hovering = False
                if card_rect.collidepoint(mouse_pos):
                    card.hovering = True
                    for j, card_2 in enumerate(self.cards):
                        if card is not card_2:
                            card_2.hovering = False

            # Draw each card
            for i, card in enumerate(self.cards):
                card_x = start_x + i * (card.image_scaled.get_width() - overlap)
                screen.blit(card.image_scaled, (card_x, start_y))
                card_strength_text(screen, card, card_x, start_y, card.image_scaled)

            # Draw hovered card
            for i, card in enumerate(self.cards):
                if card.hovering and self.allow_hovering:
                    hovering_image = card.image.copy()
                    hovering_image = scale_surface(hovering_image, (self.width * 1.2, self.height * 1.2))
                    card_x = start_x + i * (card.image_scaled.get_width() - overlap)
                    card.hovering_x = card_x
                    card.hovering_y = start_y
                    card.hovering_image = hovering_image
                    self.game_state.hovering_card = card
                    card.hovering_text = True

    def create_card_rect(self):
        """
        Creates rectangles for the cards for collision detection.
        """
        if len(self.cards) > 0:
            # First, we scale down the card images to fit within the container
            card_width = None
            for card in self.cards:
                card.image_scaled = scale_surface(card.image, (self.width, self.height * 0.95))
                card_width = card.image_scaled.get_width()

            # Calculate the total width of the cards
            total_card_width = len(self.cards) * card_width
            overlap = 0
            if total_card_width > self.width:
                # If cards don't fit side by side, calculate the necessary overlap
                overlap = (total_card_width - self.width) / (len(self.cards) - 1)

            # Calculate the starting x position for the cards to center them
            start_x = self.x + (self.width - total_card_width + overlap * (len(self.cards) - 1)) / 2

            # Calculate the y position to center the cards vertically
            card_height = self.cards[0].image_scaled.get_height()
            start_y = self.y + (self.height * 0.95 - card_height) / 2

            for i, card in enumerate(self.cards):
                card_x = start_x + i * (card.image_scaled.get_width() - overlap)
                card_rect = pygame.Rect(card_x, start_y, card.image_scaled.get_width(), card.image_scaled.get_height())
                card.rect = card_rect

    def update(self, subject):
        """
        Updates the container based on the changes in the game state.

        Parameters:
        -----------
        subject : GameState
            The current state of the game that is observed.
        """
        if subject is self.game_state and self.game_state.state == 'carousel':
            # The game has entered the 'carousel' state, so disable card hovering.
            self.allow_hovering = False
        elif subject is self.game_state and self.game_state.state == 'normal':
            # The game has returned to the 'normal' state, so enable card hovering.
            self.allow_hovering = True
            self.cards.clear()
            opponent = 6
            if self.row_id == -1:
                for j, element in enumerate(self.game_state.game_state_matrix[0][:120]):
                    if element > 0:
                        for i in range(int(element)):
                            card = Card(j, data, self.game_state)
                            self.cards.append(card)
            elif self.row_id == 0:
                index = 1
                if self.is_opponent:
                    index += opponent
                for j, element in enumerate(self.game_state.game_state_matrix[index][:120]):
                    if element > 0:
                        for i in range(int(element)):
                            card = Card(j, data, self.game_state)
                            if card.type in ['Unit', 'Hero']:
                                card.strength_text = int(
                                    self.game_state.game_state_matrix[index + 1][j] // int(element))
                                self.cards.append(card)
            elif self.row_id == 1:
                index = 3
                if self.is_opponent:
                    index += opponent
                for j, element in enumerate(self.game_state.game_state_matrix[index][:120]):
                    if element > 0:
                        for i in range(int(element)):
                            card = Card(j, data, self.game_state)
                            if card.type in ['Unit', 'Hero']:
                                card.strength_text = int(
                                    self.game_state.game_state_matrix[index + 1][j] // int(element))
                                self.cards.append(card)
            elif self.row_id == 2:
                index = 5
                if self.is_opponent:
                    index += opponent
                for j, element in enumerate(self.game_state.game_state_matrix[index][:120]):
                    if element > 0:
                        for i in range(int(element)):
                            card = Card(j, data, self.game_state)
                            if card.type in ['Unit', 'Hero']:
                                card.strength_text = int(
                                    self.game_state.game_state_matrix[index + 1][j] // int(element))
                                self.cards.append(card)
            self.create_card_rect()

        elif subject is self.game_state and self.game_state.state == 'dragging':
            # The game has returned to the 'normal' state, so enable card hovering.
            self.allow_hovering = False
            if self.game_state.parameter in self.cards:
                card_index = self.cards.index(self.game_state.parameter)
                card = self.cards.pop(card_index)
                card.position_hand = card_index
                card.hand = self.cards

    def handle_event(self, event):
        """
        Handles the user input event, mainly mouse button up event.

        Parameters:
        -----------
        event : pygame.event.Event
            The event to handle.
        """
        if event.type == pygame.MOUSEBUTTONUP and self.game_state.state == 'dragging':
            if self.rect.collidepoint(event.pos):
                self.game_state.parameter_actions.append(
                    str(self.game_state.parameter.id) + ',' + str(self.row_id) + ',-1')
                self.game_state.parameter_actions.append(
                    str(self.game_state.parameter.id) + ',' + '4' + ',-1')
        for card in self.cards:
            card.parent_container = self
            card.handle_event(event)


class Field(Component):
    """
    A class to represent a Field on a Pygame display, which is a specific type of Component.

    This Field class manages and renders either FieldRow objects or a CardContainer,
    depending on whether the field represents a hand or not.

    Attributes:
    ----------
    is_hand : bool
        A flag indicating whether this field is a hand or not.
    is_opponent : bool
        A flag indicating whether this field belongs to an opponent or not.
    field_list : list
        A list containing FieldRow objects or a CardContainer object to be displayed in the field.
    card_container : CardContainer, optional
        A CardContainer object, present only if the field represents a hand.
    field_row_siege : FieldRow, optional
        A FieldRow object representing the siege row in the field.
    field_row_ranged : FieldRow, optional
        A FieldRow object representing the ranged row in the field.
    field_row_melee : FieldRow, optional
        A FieldRow object representing the melee row in the field.

    Methods:
    --------
    __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent, is_hand)
        Initializes the Field object with various attributes including dimensions and flags.
    draw(self, screen)
        Draws the FieldRows or CardContainer on the provided Pygame screen.
    handle_event(self, event)
        Handles events such as mouse button clicks, tailored for various game states.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent, is_hand):
        """
        Initializes the Field object with the necessary parameters and sets up the FieldRows or CardContainer.

        Parameters:
        -----------
        game_state : object
            The state of the game.
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The width ratio for sizing the field.
        height_ratio : float
            The height ratio for sizing the field.
        x_ratio : float
            The x-coordinate ratio for positioning the field.
        y_ratio : float
            The y-coordinate ratio for positioning the field.
        is_opponent : bool
            A flag indicating whether this field belongs to an opponent.
        is_hand : bool
            A flag indicating whether this field represents a hand.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.is_hand = is_hand
        self.is_opponent = is_opponent
        self.field_list = []
        if is_hand:
            self.card_container = CardContainer(-1, game_state, self, 1, 1, 0, 0, is_opponent)
            self.field_list.append(self.card_container)
        else:
            if is_opponent:
                self.field_row_siege = FieldRow(game_state, 2, self.rect, 1, 0.32, 0, 0.021, is_opponent)
                self.field_row_ranged = FieldRow(game_state, 1, self.rect, 1, 0.32, 0, 0.335, is_opponent)
                self.field_row_melee = FieldRow(game_state, 0, self.rect, 1, 0.32, 0, 0.67, is_opponent)
                self.field_list.append(self.field_row_ranged)
                self.field_list.append(self.field_row_siege)
                self.field_list.append(self.field_row_melee)
            else:
                self.field_row_melee = FieldRow(game_state, 0, self.rect, 1, 0.32, 0, 0.021, is_opponent)
                self.field_row_ranged = FieldRow(game_state, 1, self.rect, 1, 0.32, 0, 0.335, is_opponent)
                self.field_row_siege = FieldRow(game_state, 2, self.rect, 1, 0.32, 0, 0.67, is_opponent)
                self.field_list.append(self.field_row_melee)
                self.field_list.append(self.field_row_ranged)
                self.field_list.append(self.field_row_siege)

    def draw(self, screen):
        """
        Draws the FieldRows or CardContainer onto the specified Pygame screen.

        Parameters:
        -----------
        screen : pygame.Surface
            The surface on which the FieldRows or CardContainer are to be drawn.
        """
        # Get the mouse cursor position
        mouse_pos = pygame.mouse.get_pos()
        for field in self.field_list:
            if not field.rect.collidepoint(mouse_pos):
                field.draw(screen)
        for field in self.field_list:
            if field.rect.collidepoint(mouse_pos):
                field.draw(screen)

    def handle_event(self, event):
        """
        Handles various events such as mouse button clicks, particularly focusing on interactions
        within the FieldRows or CardContainer based on the current game state.

        Parameters:
        -----------
        event : pygame.event.Event
            The event to be handled.
        """
        if self.game_state.state == 'normal':
            if self.is_hand:
                self.field_list[0].handle_event(event)
        if self.game_state.state != 'carousel':
            for fieldRow in self.field_list:
                if event.type == pygame.MOUSEBUTTONUP and fieldRow.rect.collidepoint(event.pos):
                    if self.game_state.parameter is not None \
                            and isinstance(self.game_state.parameter, Card) \
                            and self.game_state.parameter.ability == 'Medic':
                        self.game_state.parameter_actions.append(
                            str(self.game_state.parameter.id) + ',' + str(fieldRow.row_id) + ',' + '-1')
                        self.game_state.parameter = None
                        self.game_state.set_state('carousel')
                    else:
                        fieldRow.handle_event(event)


class PanelMiddle(Component):
    """
    Represents the middle panel in the game application's GUI, inheriting from the Component class.
    Manages and displays the graphical components such as fields (opponent's, player's, and hand) and
    developer tools on the game interface.

    Attributes:
    ----------
    field_list : list of Field
        A list containing instances of all Field objects managed by the PanelMiddle for easier iteration.
    field_op : Field
        An instance of Field class representing the opponent's field in the game.
    field_me : Field
        An instance of Field class representing the player's field in the game.
    field_hand : Field
        An instance of Field class representing the hand field in the game.
    developer_tools : PanelDeveloperTools
        An instance of PanelDeveloperTools class representing the developer tools panel in the game.

    Methods:
    -------
    __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes a PanelMiddle object, setting up the fields and developer tools as components.
    draw(self, screen)
        Renders the Fields and the developer tools on the game's display screen.
    handle_event(self, event)
        Handles user inputs/events such as mouse clicks and key presses for the components managed by PanelMiddle.

    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the PanelMiddle with essential configurations and components like fields and developer tools.

        Parameters:
        ----------
        game_state : GameState
            The current state of the game, used to determine how to handle user inputs/events.
        parent_rect : pygame.Rect
            The rectangle representing the dimensions of the parent component.
        width_ratio : float
            The relative width of the PanelMiddle compared to its parent.
        height_ratio : float
            The relative height of the PanelMiddle compared to its parent.
        x_ratio : float
            The relative x-coordinate of the PanelMiddle compared to its parent.
        y_ratio : float
            The relative y-coordinate of the PanelMiddle compared to its parent.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.field_list = []
        self.field_op = Field(game_state, self, 1, 0.385, 0, 0, True, False)
        self.field_me = Field(game_state, self, 1, 0.385, 0, 0.388, False, False)
        self.field_hand = Field(game_state, self, 0.938, 0.13, 0.062, 0.775, False, True)
        self.developer_tools = PanelDeveloperTools(game_state, self, 1, 0.1, 0, 0.9)
        self.field_list.append(self.field_op)
        self.field_list.append(self.field_me)
        self.field_list.append(self.field_hand)

    def draw(self, screen):
        """
        Renders the Fields and developer tools onto the game's display screen.
        It takes into consideration the current game state and whether developer tools are enabled.

        Parameters:
        ----------
        screen : pygame.Surface
            The pygame Surface object representing the game's display screen where the components will be rendered.
        """
        # Get the mouse cursor position
        mouse_pos = pygame.mouse.get_pos()

        for field in self.field_list:
            if not field.rect.collidepoint(mouse_pos):
                field.draw(screen)
        for field in self.field_list:
            if field.rect.collidepoint(mouse_pos):
                field.draw(screen)

        if self.game_state.developer_tools:
            self.developer_tools.draw(screen)

    def handle_event(self, event):
        """
        Handles user inputs/events by delegating them to each managed component to handle according to their
        implementation. It considers the current state of the game and the enabled status of developer tools.

        Parameters:
        ----------
        event : pygame.event.Event
            The pygame Event object representing a user input/event like a mouse click or key press.
        """
        if self.game_state.state != 'carousel':
            for field in self.field_list:
                field.handle_event(event)
            if self.game_state.developer_tools:
                self.developer_tools.handle_event(event)


class PanelDeveloperTools(Component):
    """
    Represents the developer tools panel in the game application's GUI, inheriting functionalities from the Component
    class.
    It manages and displays a set of buttons allowing users to interact with developer functionalities like switching
    views,
    stepping back, and stepping forward within the game states.

    Attributes:
    ----------
    buttons : list of tuple
        A list containing tuples where each tuple consists of a pygame.Rect representing the button’s position and size,
        and a string representing the button’s functionality name.
    font : pygame.font.Font
        A pygame font object used to render text on the developer tools panel.

    Methods:
    -------
    __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the PanelDeveloperTools object with essential configurations and button functionalities.
    draw(self, screen)
        Renders the buttons on the game's display screen.
    handle_event(self, event)
        Handles user inputs/events such as mouse clicks for the buttons in the developer tools panel.

    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the PanelDeveloperTools with configurations, buttons and their corresponding functionalities.

        Parameters:
        ----------
        game_state : GameState
            The current state of the game used for switching views and stepping through game states.
        parent_rect : pygame.Rect
            The rectangle representing the dimensions of the parent component.
        width_ratio : float
            The relative width of the PanelDeveloperTools compared to its parent.
        height_ratio : float
            The relative height of the PanelDeveloperTools compared to its parent.
        x_ratio : float
            The relative x-coordinate of the PanelDeveloperTools compared to its parent.
        y_ratio : float
            The relative y-coordinate of the PanelDeveloperTools compared to its parent.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)

        self.buttons = []
        self.font = pygame.font.Font(None, 36)  # Adjust font size as needed

        functionalities = ["Switch view", "Step back", "Step forward"]

        rect_height = self.rect.height // len(functionalities)
        for i, func in enumerate(functionalities):
            rect = pygame.Rect(self.rect.x, self.rect.y + i * rect_height, self.rect.width, rect_height)
            self.buttons.append((rect, func))

    def draw(self, screen):
        """
        Renders the buttons, including rectangles and text, on the game's display screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The pygame Surface object representing the game's display screen where the buttons will be rendered.
        """
        for rect, func_name in self.buttons:
            # Draw rectangle
            # pygame.draw.rect(screen, (200, 200, 200), rect)

            # Draw text
            text_surface = self.font.render(func_name, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """
        Handles mouse button click events. It identifies which button was clicked and performs the corresponding
        functionality like switching views or stepping through game states.

        Parameters:
        ----------
        event : pygame.event.Event
            The pygame Event object representing a mouse button click event.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            pos = event.pos
            for rect, func_name in self.buttons:
                if rect.collidepoint(pos):
                    print(f"{func_name} was clicked!")
                    if func_name == 'Switch view':
                        temp = self.game_state.game_state_matrix
                        self.game_state.game_state_matrix = self.game_state.game_state_matrix_opponent
                        self.game_state.game_state_matrix_opponent = temp
                        self.game_state.set_state('normal')
                    elif func_name == 'Step back':
                        self.game_state.stepper.back()
                        self.game_state.set_state('normal')
                    elif func_name == 'Step forward':
                        self.game_state.stepper.forward()
                        self.game_state.set_state('normal')


class Stepper:
    """
    Represents the Stepper class, which is responsible for managing, saving, and loading game states.
    It facilitates navigating through different game states to perform actions like step forward, and step back.

    Attributes:
    ----------
    game_state : GameState
        The current state of the game.
    matrix_player : list of numpy.ndarray
        A list holding the matrices representing the player's game state at different steps.
    actions_player : list
        A list holding the actions taken by the player at different steps.
    matrix_opponent : list of numpy.ndarray
        A list holding the matrices representing the opponent's game state at different steps.
    actions_opponent : list
        A list holding the actions taken by the opponent at different steps.
    current_index : int
        An index pointing to the current state in the saved matrices.
    save_state : numpy.ndarray or None
        A saved matrix representing a specific game state of the player.
    save_state_opponent : numpy.ndarray or None
        A saved matrix representing a specific game state of the opponent.

    Methods:
    -------
    __init__(self, game_state)
        Initializes the Stepper object with the given game state.
    step(self, turn, action)
        Saves the current state and the performed action.
    forward(self)
        Moves the game state one step forward.
    back(self)
        Moves the game state one step backward.
    save(self, filename)
        Saves the game states and actions into a file.
    load(self, filename)
        Loads the game states and actions from a file.
    """

    def __init__(self, game_state):
        """
        Initializes the Stepper object with the given game state.

        Parameters:
        ----------
        game_state : GameState
            The current state of the game.
        """
        self.game_state = game_state

        self.matrix_player = []
        self.actions_player = []
        self.matrix_opponent = []
        self.actions_opponent = []
        self.current_index = 0

        self.save_state = None
        self.save_state_opponent = None

    def step(self, turn, action):
        """
        Saves the current state of the game and the action performed during a turn.

        Parameters:
        ----------
        turn : int
            The current turn of the game (0 for player, 1 for opponent).
        action : various possible types
            The action performed during the current turn.
        """
        self.matrix_player.append(copy.copy(self.game_state.game_state_matrix))
        self.matrix_opponent.append(copy.copy(self.game_state.game_state_matrix_opponent))
        if turn == 0:
            self.actions_player.append(action)
        elif turn == 1:
            self.actions_opponent.append(action)

    def forward(self):
        """
        Advances the game state by one step, updating the game state matrices accordingly.
        """
        if self.save_state is not None and self.current_index + 1 < len(self.matrix_player):
            self.current_index += 1
            self.game_state.game_state_matrix = self.matrix_player[self.current_index]
            self.game_state.game_state_matrix_opponent = self.matrix_opponent[self.current_index]
        elif self.save_state is not None and self.current_index + 1 == len(self.matrix_player):
            self.game_state.game_state_matrix = self.save_state
            self.game_state.game_state_matrix_opponent = self.save_state_opponent
            self.save_state = None
            self.save_state_opponent = None

    def back(self):
        """
        Moves the game state one step backward, updating the game state matrices accordingly.
        """
        if self.save_state is None and len(self.matrix_player) > 0:
            self.save_state = self.game_state.game_state_matrix
            self.save_state_opponent = self.game_state.game_state_matrix_opponent
            self.current_index = len(self.matrix_player) - 1
            self.game_state.game_state_matrix = self.matrix_player[self.current_index]
        elif self.save_state is not None and self.current_index > 0:
            self.current_index -= 1
            self.game_state.game_state_matrix = self.matrix_player[self.current_index]
            self.game_state.game_state_matrix_opponent = self.matrix_opponent[self.current_index]

    def save(self, filename):
        """
        Saves the game states and actions into a JSON file.

        Parameters:
        ----------
        filename : str
            The name of the file where the game states and actions will be saved.
        """
        with open(filename, 'w') as file:
            data_file = {
                'matrix_player': [arr.tolist() for arr in self.matrix_player],
                'actions_player': self.actions_player,
                'matrix_opponent': [arr.tolist() for arr in self.matrix_opponent],
                'actions_opponent': self.actions_opponent,
                'current_index': self.current_index
            }
            json.dump(data_file, file)

    def load(self, filename):
        """
        Loads the game states and actions from a JSON file and updates the current game state.

        Parameters:
        ----------
        filename : str
            The name of the file from which the game states and actions will be loaded.
        """
        with open(filename, 'r') as file:
            data_file = json.load(file)
            self.matrix_player = [np.array(arr) for arr in data_file['matrix_player']]
            self.actions_player = data_file['actions_player']
            self.matrix_opponent = [np.array(arr) for arr in data_file['matrix_opponent']]
            self.actions_opponent = data_file['actions_opponent']
            self.current_index = data_file['current_index']
            self.game_state.game_state_matrix = self.matrix_player[self.current_index] if self.matrix_player else None
            self.game_state.game_state_matrix_opponent = self.matrix_opponent[
                self.current_index] if self.matrix_opponent else None


class PanelRight(Component):
    """
    Represents the right panel in a game application's GUI, inheriting functionalities from the Component class.
    It manages and displays graphical components such as the grave and deck for both the player and the opponent.

    Attributes:
    ----------
    component_list : list
        A collection of all components (Grave, Deck) managed by this panel, facilitating iteration.
    grave_op : Grave
        An instance of the Grave class representing the opponent's grave.
    deck_op : Deck
        An instance of the Deck class representing the opponent's deck.
    grave_me : Grave
        An instance of the Grave class representing the player's grave.
    deck_me : Deck
        An instance of the Deck class representing the player's deck.

    Methods:
    -------
    __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes a PanelRight object by setting up its attributes and components.
    draw(self, screen)
        Draws the Grave and Deck components on the screen for both the player and the opponent.
    handle_event(self, event)
        Manages user inputs/events, such as mouse clicks and key presses, delegating them to each component.

    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Constructor of the PanelRight class, initializing its attributes and creating instances
        of Grave and Deck for both the player and the opponent.

        Parameters:
        ----------
        game_state : GameState
            The current state of the game.
        parent_rect : pygame.Rect
            The rectangle representing the dimensions of the parent screen.
        width_ratio : float
            The width of PanelRight as a fraction of the parent rectangle's width.
        height_ratio : float
            The height of PanelRight as a fraction of the parent rectangle's height.
        x_ratio : float
            The x-coordinate of PanelRight as a fraction of the parent rectangle's width.
        y_ratio : float
            The y-coordinate of PanelRight as a fraction of the parent rectangle's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.component_list = []
        self.grave_op = Grave(game_state, self, 0.28, 0.14, 0.065, 0.065, True)
        self.deck_op = Deck(game_state, self, 0.28, 0.14, 0.51, 0.065, 'monsters', True)
        self.grave_me = Grave(game_state, self, 0.28, 0.14, 0.065, 0.765, False)
        self.deck_me = Deck(game_state, self, 0.28, 0.14, 0.51, 0.765, 'monsters', False)
        self.component_list.append(self.grave_op)
        self.component_list.append(self.deck_op)
        self.component_list.append(self.grave_me)
        self.component_list.append(self.deck_me)

    def draw(self, screen):
        """
        Renders the Grave and Deck components for both the player and the opponent on the provided screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The surface on which the components are rendered.
        """
        for component in self.component_list:
            component.draw(screen)

    def handle_event(self, event):
        """
        Handles user interaction events, delegating them to each individual component for further handling.

        Parameters:
        ----------
        event : pygame.event.Event
            An object representing the captured user interaction event.
        """
        for component in self.component_list:
            component.handle_event(event)


class PanelGame(Component):
    """
    Represents the game panel in a GUI application which manages the left, middle,
    and right panels of the game. Inherits from the Component class.

    Attributes:
    ----------
    parent_rect : pygame.Rect
        The rectangle representing the parent screen's dimensions.
    game_state : GameState
        An instance representing the current state of the game.
    panel_left : PanelLeft
        An instance of PanelLeft representing the left panel of the game.
    panel_middle : PanelMiddle
        An instance of PanelMiddle representing the middle panel of the game.
    panel_right : PanelRight
        An instance of PanelRight representing the right panel of the game.
    panel_list : list
        A list containing instances of all panels for iteration.
    carousal_active : bool
        A flag used to check whether the carousel feature is active or not.
    panel_carousel : Carousel
        An instance of Carousel class used when carousel feature is active.
    background_image : pygame.Surface
        The surface object representing the background image of the panel.

    Methods:
    -------
    __init__(self, game_state, parent_rect)
        Initializes the PanelGame with essential attributes and components.
    draw(self, screen)
        Draws the left, middle, and right panels, carousel, and other UI components on the screen.
    handle_event(self, event)
        Handles user inputs/events and updates the state of UI components and game panels accordingly.
    update(self, subject)
        Updates the state based on changes in the observed subject, usually the game state.

    """

    def __init__(self, game_state, parent_rect):
        """
        Initializes the PanelGame with necessary attributes and components including
        background image and panels.

        Parameters:
        ----------
        game_state : GameState
            An instance representing the current state of the game.
        parent_rect : pygame.Rect
            The rectangle representing the parent screen's dimensions.
        """
        super().__init__(game_state, parent_rect, 1, 1, 0, 0)
        # Load the background image
        self.background_image = pygame.image.load('img/board.jpg')  # Replace with your image path
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.width, self.height))  # Scale the image to fit the screen
        self.panel_list = []
        self.game_state = game_state
        # Initialize the left panel
        width_ratio = 0.265  # takes up 26.5% of the parent's width
        height_ratio = 1
        x_ratio = 0  # starts at the left edge of the parent
        y_ratio = 0  # starts at the top edge of the parent
        self.panel_left = PanelLeft(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)

        # Initialize the middle panel
        width_ratio = 0.525  # takes up 52.5% of the parent's width
        x_ratio = 0.265  # starts at 26.5% of the width of the parent
        self.panel_middle = PanelMiddle(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)

        # Initialize the right panel
        width_ratio = 0.21  # takes up 21% of the parent's width
        x_ratio = 0.79  # starts at 79% of the width of the parent
        self.panel_right = PanelRight(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.panel_list.append(self.panel_left)
        self.panel_list.append(self.panel_middle)
        self.panel_list.append(self.panel_right)

        self.carousal_active = False
        self.panel_carousel = Carousel(game_state, parent_rect, 1, 1, 0, 0)

    def draw(self, screen):
        """
        Draws the game panels, carousel, and other UI components on the screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The surface on which panels and UI components are drawn.
        """
        # Get the mouse cursor position
        screen.blit(self.background_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        for panel in self.panel_list:
            if not panel.rect.collidepoint(mouse_pos):
                panel.draw(screen)
        for panel in self.panel_list:
            if panel.rect.collidepoint(mouse_pos):
                panel.draw(screen)
            if self.game_state.state == 'dragging':
                self.game_state.parameter.draw(screen)

        if self.game_state.state == 'normal' and self.game_state.hovering_card is not None and \
                self.game_state.hovering_card.hovering:
            hovering_image = self.game_state.hovering_card.hovering_image
            screen.blit(hovering_image,
                        (self.game_state.hovering_card.hovering_x, self.game_state.hovering_card.hovering_y))
            card_preview = CardPreview(self.game_state, screen.get_rect(), self.game_state.hovering_card)
            card_preview.draw(screen)
            if self.game_state.hovering_card.hovering_text:
                card_strength_text(screen, self.game_state.hovering_card, self.game_state.hovering_card.hovering_x,
                                   self.game_state.hovering_card.hovering_y, hovering_image)
            if self.game_state.hovering_card.ability != '0':
                card_description = CardDescription(self.game_state, screen.get_rect(), self.game_state.hovering_card)
                card_description.draw(screen)
        if self.carousal_active:
            if self.game_state.parameter is None:
                self.panel_carousel.cards = self.panel_right.grave_me.cards
            else:
                self.panel_carousel.cards = self.game_state.parameter
            self.panel_carousel.draw(screen)

    def handle_event(self, event):
        """
        Handles user inputs/events such as mouse clicks and key presses,
        and updates the UI components and game panels accordingly.

        Parameters:
        ----------
        event : pygame.event.Event
            The event object representing user inputs/events.
        """
        if self.carousal_active:
            self.panel_carousel.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.game_state.state == 'carousel':
                    self.game_state.set_state('normal')
        else:
            for panel in self.panel_list:
                panel.handle_event(event)
        if self.game_state.state == 'dragging':
            self.game_state.parameter.handle_event(event)

    def update(self, subject):
        """
        Updates the state of the PanelGame based on changes in the observed subject,
        controlling the activation and deactivation of the carousel feature.

        Parameters:
        ----------
        subject : Subject
            The observed subject notifying about the changes.
        """
        if subject is self.game_state and self.game_state.state == 'carousel':
            # The game has entered the 'carousel' state, so disable card hovering.
            self.carousal_active = True
        elif subject is self.game_state and self.game_state.state == 'normal':
            # The game has returned to the 'normal' state, so enable card hovering.
            self.carousal_active = False


class Grave(Component):
    """
    Represents a Grave component within a game, storing discarded or destroyed game cards.
    Inherits from the Component class.

    Attributes:
    ----------
    cards : list
        A list containing the discarded or destroyed game cards (instances of the Card class).
    is_opponent : bool
        A boolean that indicates whether the grave belongs to the opponent or not.

    Methods:
    -------
    __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent)
        Initializes a new instance of the Grave class.
    draw(screen: pygame.Surface)
        Draws the Grave and its cards onto the given screen.
    handle_event(event)
        Handles user inputs like mouse clicks, updates the state of the Grave component accordingly.
    update(subject)
        Updates the state of the Grave based on changes in the observed subject.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes a new instance of Grave with a set of attributes.

        Parameters:
        ----------
        game_state : object
            The current state of the game.
        parent_rect : pygame.Rect
            Rectangle representing the parent container.
        width_ratio : float
            Ratio of the Grave's width to its parent's width.
        height_ratio : float
            Ratio of the Grave's height to its parent's height.
        x_ratio : float
            Ratio of the Grave's x position to its parent's width.
        y_ratio : float
            Ratio of the Grave's y position to its parent's height.
        is_opponent : bool
            Boolean indicating whether the grave belongs to the opponent or not.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)
        self.cards = []
        self.is_opponent = is_opponent

    def draw(self, screen):
        """
        Draws the Grave and its cards onto the given screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen where the Grave and its cards will be drawn.
        """
        if len(self.cards) > 0:
            for i, card in enumerate(self.cards):
                card_image = scale_surface(card.image, (self.width, self.height))

                if i % 2 == 0 and i != 0:
                    x_position = self.x + 5 - i / 2
                    y_position = self.y - i / 2
                else:
                    x_position = self.x + 5 - (i - 1) / 2
                    y_position = self.y - (i - 1) / 2

                # Ensuring the card does not go beyond the container's dimensions
                x_position = max(x_position, 0)
                y_position = max(y_position, 0)

                screen.blit(card_image, (x_position, y_position))
                if i == len(self.cards) - 1:
                    card_strength_text(screen, card, x_position, y_position, card_image)

    def handle_event(self, event):
        """
        Handles user inputs like mouse clicks, and updates the state of the Grave component accordingly.

        Parameters:
        ----------
        event : pygame.event.Event
            Event object representing a user event.
        """
        # Get the mouse cursor position
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
            self.game_state.set_state('carousel')
            self.game_state.parameter = self.cards

    def update(self, subject):
        """
        Updates the state of the Grave based on changes in the observed subject.
        Primarily, it updates the cards in the Grave based on changes in the game state.

        Parameters
        ----------
        subject : Subject
            The observed subject that notifies about the changes (typically game_state).
        """
        index = 13
        if self.is_opponent:
            index = 14
        if subject is self.game_state and self.game_state.state == 'normal':
            self.cards.clear()
            for j, element in enumerate(self.game_state.game_state_matrix[index][:120]):
                if element > 0:
                    for i in range(int(element)):
                        card = Card(j, data, self.game_state)
                        self.cards.append(card)


class Deck(Component):
    """
    Represents a Deck component within a game, managing and displaying a deck of cards.
    Inherits from the Component class.

    Attributes:
    ----------
    cards : list
        A list containing instances of the Card class, representing the cards in the deck.
    is_opponent : bool
        A boolean indicating whether the deck belongs to the opponent.
    deck_back_image : pygame.Surface
        The surface representing the back image of the cards in the deck.

    Methods:
    -------
    __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, deck, is_opponent)
        Initializes a new instance of the Deck class.
    draw(screen: pygame.Surface)
        Draws the deck of cards and the card count onto the given screen.
    handle_event(event)
        Handles user inputs like mouse clicks, updates the state of the Deck component accordingly.
    update(subject)
        Updates the state of the Deck based on changes in the observed subject.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, deck, is_opponent):
        """
        Initializes a new instance of Deck with a set of attributes.

        Parameters:
        ----------
        game_state : object
            The current state of the game.
        parent_rect : pygame.Rect
            Rectangle representing the parent container.
        width_ratio : float
            Ratio of the Deck's width to its parent's width.
        height_ratio : float
            Ratio of the Deck's height to its parent's height.
        x_ratio : float
            Ratio of the Deck's x position to its parent's width.
        y_ratio : float
            Ratio of the Deck's y position to its parent's height.
        deck : str
            String representing the deck type, determining the back image of the deck.
        is_opponent : bool
            Boolean indicating whether the deck belongs to the opponent.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.cards = []
        self.is_opponent = is_opponent
        self.deck_back_image = pygame.image.load(f'img/icons/deck_back_{deck}.jpg')
        self.deck_back_image = scale_surface(self.deck_back_image, (self.width, self.height))

    def draw(self, screen):
        """
        Draws the deck of cards and the card count onto the given screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen where the Deck and its cards will be drawn.
        """
        if not self.cards:
            return

        card_image_scaled = self.deck_back_image
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        if len(self.cards) > 0:
            for i, card in enumerate(self.cards):
                card_image = scale_surface(card.image, (self.width, self.height))
                if i % 2 == 0 and i != 0:
                    x_position = self.x + 5 - i / 2
                    y_position = self.y - i / 2
                else:
                    x_position = self.x + 5 - (i - 1) / 2
                    y_position = self.y - (i - 1) / 2
                center_x = x_position + card_image.get_width() / 2
                center_y = y_position + card_image.get_height() / 2

                # Ensuring the card does not go beyond the container's dimensions
                x_position = max(x_position, 0)
                y_position = max(y_position, 0)

                screen.blit(card_image_scaled, (x_position, y_position))

        # Draw card count rectangle
        card_count_rect = pygame.Rect(center_x - 25, center_y - 10, 50, 20)
        s = pygame.Surface((50, 20))  # the size of your rect
        s.set_alpha(200)  # alpha level
        s.fill((20, 20, 20))  # this fills the entire surface
        screen.blit(s, (center_x - 25, center_y - 10))  # (0,0) are the top-left coordinates

        # Draw card count text
        font = ResizableFont('Gwent.ttf', 20)
        text_color = (218, 165, 32)
        text = font.font.render(str(len(self.cards)), True, text_color)
        draw_centered_text(screen, text, card_count_rect)

    def handle_event(self, event):
        """
        Handles user inputs like mouse clicks, and updates the state of the Deck component accordingly.

        Parameters:
        ----------
        event : pygame.event.Event
            Event object representing a user event.
        """
        # Get the mouse cursor position
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos) and not self.is_opponent:
            self.game_state.set_state('carousel')
            self.game_state.parameter = self.cards

    def update(self, subject):
        """
        Updates the state of the Deck based on changes in the observed subject.
        Primarily, it updates the cards in the Deck based on changes in the game state.

        Parameters
        ----------
        subject : Subject
            The observed subject that notifies about the changes (typically game_state).
        """
        index = 15
        matrix = self.game_state.game_state_matrix
        if self.is_opponent:
            matrix = self.game_state.game_state_matrix_opponent
        if subject is self.game_state and self.game_state.state == 'normal' and matrix is not None:
            self.cards.clear()
            for j, element in enumerate(matrix[index][:120]):
                if element > 0:
                    for i in range(int(element)):
                        card = Card(j, data, self.game_state)
                        self.cards.append(card)


class Carousel(Component):
    """
    Represents a Carousel component within a game, managing and displaying a carousel of card images.
    Inherits from the Component class.

    Attributes:
    ----------
    cards : list of Card
        A list containing instances of the Card class, representing the cards in the carousel.
    current_index : int
        An index pointing to the current card in the cards list.

    Methods:
    -------
    __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes a new instance of the Carousel class.
    draw(screen: pygame.Surface)
        Draws the carousel and its cards onto the given screen.
    next_card()
        Increments the current_index to move to the next card in the carousel.
    previous_card()
        Decrements the current_index to move to the previous card in the carousel.
    handle_event(event: pygame.event.Event)
        Handles user inputs like mouse clicks and key presses, updating the state of the Carousel component accordingly.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes a new instance of Carousel with a set of attributes and an empty list of cards.

        Parameters
        ----------
        game_state : object
            The current state of the game.
        parent_rect : pygame.Rect
            Rectangle representing the parent container.
        width_ratio : float
            Ratio of the Carousel's width to its parent's width.
        height_ratio : float
            Ratio of the Carousel's height to its parent's height.
        x_ratio : float
            Ratio of the Carousel's x position to its parent's width.
        y_ratio : float
            Ratio of the Carousel's y position to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.cards = []
        self.current_index = 0

    def draw(self, screen):
        """
        Draws the carousel and its cards onto the given screen.
        The current card is displayed at the center, and other cards are positioned on the sides.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen where the Carousel and its cards will be drawn.
        """
        if self.current_index > len(self.cards) - 1:
            self.current_index = 0
        if len(self.cards) > 0:
            # Calculate positions for all cards
            center_x = self.width / 2
            center_y = self.height / 2

            # Define the spacing between the cards
            spacing = 10

            # First calculate and store the position of the enlarged card
            enlarged_card = self.cards[self.current_index]
            enlarged_card.image_scaled = scale_surface(enlarged_card.large_image,
                                                       (self.width / 6 * 1.2, self.height * 1.2))  # Bigger card
            enlarged_card_x = center_x - enlarged_card.image_scaled.get_width() / 2
            enlarged_card_y = center_y - enlarged_card.image_scaled.get_height() / 2

            for i, card in enumerate(self.cards):
                if i == self.current_index:
                    # Draw the enlarged card at the stored position
                    screen.blit(enlarged_card.image_scaled, (enlarged_card_x, enlarged_card_y))
                else:
                    card.image_scaled = scale_surface(card.large_image,
                                                      (self.width / 6, self.height))  # Regular size card
                    multiplier = abs(i - self.current_index)
                    if i < self.current_index:  # Card is to the left of the current card
                        # Calculate position based on the enlarged card's position
                        x = enlarged_card_x - multiplier * (card.image_scaled.get_width() + spacing)
                        y = center_y - card.image_scaled.get_height() / 2
                        screen.blit(card.image_scaled, (x, y))
                    else:  # Card is to the right of the current card
                        # Calculate position based on the enlarged card's position and add a space width
                        x = enlarged_card_x + enlarged_card.image_scaled.get_width() + spacing + (multiplier - 1) * (
                                card.image_scaled.get_width() + spacing)
                        y = center_y - card.image_scaled.get_height() / 2
                        screen.blit(card.image_scaled, (x, y))
        else:
            self.game_state.set_state('normal')

    def next_card(self):
        """
        Increments the current_index, moving the carousel to the next card if it's not already at the last card.
        """
        if self.current_index < len(self.cards) - 1:
            self.current_index += 1

    def previous_card(self):
        """
        Decrements the current_index, moving the carousel to the previous card if it's not already at the first card.
        """
        if self.current_index > 0:
            self.current_index -= 1

    def handle_event(self, event):
        """
        Handles user inputs like mouse clicks and key presses, and updates the state of the Carousel component.
        For example, it changes the current card based on the user's input.

        Parameters:
        ----------
        event : pygame.event.Event
            The event object containing details about the user's action.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the click was on the right side of the current card, move to the next card
            if event.pos[0] > self.x + self.width / 2:
                self.next_card()
            # If the click was on the left side of the current card, move to the previous card
            elif event.pos[0] < self.x + self.width / 2:
                self.previous_card()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # enter
                last_action = self.game_state.parameter_actions[-1]
                split = last_action.split(',')
                new_action = ','.join(split[:2])
                new_action += ',' + str(self.cards[self.current_index].id)
                self.game_state.parameter_actions.append(new_action)
                self.game_state.set_state('normal')


class Notify(Component):
    """
    Represents a notification component within a game, inheriting from the Component class.
    This class handles the display of various notifications to the user, updating the visuals based on the
    notification type.

    Attributes:
    ----------
    notify_component_image : NotifyComponent
        An instance of NotifyComponent for handling and displaying notification images.
    notify_component_text : NotifyComponent
        An instance of NotifyComponent for handling and displaying notification text messages.

    Methods:
    -------
    __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the Notify instance and its components.
    draw(self, screen)
        Draws the notification components (text and images) on the screen.
    set_notification(self, notification)
        Sets the notification text and image based on the notification type provided.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes a new instance of the Notify class along with its text and image components.

        Parameters:
        ----------
        game_state : GameState
            The current state of the game.
        parent_rect : pygame.Rect
            The rectangle representing the parent container.
        width_ratio : float
            Ratio of Notify's width to its parent's width.
        height_ratio : float
            Ratio of Notify's height to its parent's height.
        x_ratio : float
            Ratio of Notify's x position to its parent's width.
        y_ratio : float
            Ratio of Notify's y position to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)

        self.notify_component_image = NotifyComponent(self.game_state, self.rect, 0.221, 2.07, 0.2255, -0.666)
        self.notify_component_text = NotifyComponent(self.game_state, self.notify_component_image.rect, 2.05, 0.4725,
                                                     1.005, 0.321)
        self.set_notification('op-coin')

    def draw(self, screen):
        """
        Draws the background, notify_component_image, and notify_component_text on the screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen where the notification components will be drawn.
        """
        background = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        background.fill((10, 10, 10, 240))
        screen.blit(background, (self.x, self.y))
        self.notify_component_image.draw(screen)
        self.notify_component_text.draw(screen)

    def set_notification(self, notification):
        """
        Sets the notification text and image based on the notification type. Different pre-defined notifications
        have unique text messages and associated images that are loaded and set in this method.

        Parameters:
        ----------
        notification : str
            A string identifier for the type of notification to be displayed.
        """
        if notification == 'me-first':
            self.notify_component_text.text_to_draw = "You will go first"
            self.notify_component_image.image_to_draw = None
        elif notification == 'op-first':
            self.notify_component_text.text_to_draw = "Your opponent will go first"
            self.notify_component_image.image_to_draw = None
        elif notification == 'op-coin':
            self.notify_component_text.text_to_draw = "Your opponent will go first"
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_op_coin.png')
        elif notification == 'me-coin':
            self.notify_component_text.text_to_draw = "You will go first"
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_me_coin.png')
        elif notification == 'round-start':
            self.notify_component_text.text_to_draw = 'Round Start'
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_round_start.png')
        elif notification == 'me-pass':
            self.notify_component_text.text_to_draw = "Round passed"
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_round_passed.png')
        elif notification == 'op-pass':
            self.notify_component_text.text_to_draw = "Your opponent has passed"
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_round_passed.png')
        elif notification == 'win-round':
            self.notify_component_text.text_to_draw = "You won the round!"
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_win_round.png')
        elif notification == 'lose-round':
            self.notify_component_text.text_to_draw = "Your opponent won the round!"
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_lose_round.png')
        elif notification == 'draw-round':
            self.notify_component_text.text_to_draw = "The round ended in a draw!"
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_draw_round.png')
        elif notification == 'me-turn':
            self.notify_component_text.text_to_draw = "Your turn!"
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_me_turn.png')
        elif notification == 'op-turn':
            self.notify_component_text.text_to_draw = "Opponent's turn!"
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_op_turn.png')
        elif notification == 'north':
            self.notify_component_text.text_to_draw = "Northern Realms faction ability triggered - North draws an " \
                                                      "additional card."
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_north.png')
        elif notification == 'monsters':
            self.notify_component_text.text_to_draw = "Monsters faction ability triggered - one randomly-chosen " \
                                                      "Monster Unit Card stays on the board."
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_monsters.png')
        elif notification == 'scoiatael':
            self.notify_component_text.text_to_draw = "Opponent used the Scoia'tael faction perk to go first."
            self.notify_component_image.image_to_draw = pygame.image.load('img/icons/notif_scoiatael.png')


class NotifyComponent(Component):
    """
    A NotifyComponent is a specialized type of Component used specifically for notifications in a game.
    This class handles the display of images or text messages within the notification.

    Attributes:
    ----------
    image_to_draw : pygame.Surface
        The image to be displayed in the notification. If no image is set, this is None.
    text_to_draw : str
        The text message to be displayed in the notification. If no text is set, this is None.
    font_small : ResizableFont
        A font object used for rendering text within the notification.

    Methods:
    -------
    __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the NotifyComponent, setting up its geometrical attributes and font.
    draw(self, screen)
        Draws the image or text message onto the screen based on what is currently set to display.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the NotifyComponent with geometrical attributes and font.

        Parameters:
        ----------
        game_state : GameState
            The current state of the game.
        parent_rect : pygame.Rect
            The rectangle representing the parent container.
        width_ratio : float
            Ratio of NotifyComponent's width to its parent's width.
        height_ratio : float
            Ratio of NotifyComponent's height to its parent's height.
        x_ratio : float
            Ratio of NotifyComponent's x position to its parent's width.
        y_ratio : float
            Ratio of NotifyComponent's y position to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.image_to_draw = None
        self.text_to_draw = None
        self.font_small = ResizableFont('Gwent.ttf', 50)

    def draw(self, screen):
        """
        Draws either an image or a text message to the screen. If both are set, the image is prioritized.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen on which the image or text of the NotifyComponent will be drawn.
        """
        if self.image_to_draw is not None:
            screen.blit(self.image_to_draw, (self.x, self.y))
        elif self.text_to_draw is not None:
            text = fit_text_in_rect(self.text_to_draw, self.font_small, (218, 165, 32), self.rect)
            # Get the rectangle of the text
            text_rect = text.get_rect()
            # Position the center of the rectangle at the center of the NotifyComponent
            text_rect.x = self.x
            text_rect.centery = self.y + self.height / 2
            screen.blit(text, text_rect)


class NotifyAction:
    """
    NotifyAction represents a notification event within a game.
    It contains details about the type of notification, the start time, and the elapsed time of the notification.

    Attributes:
    ----------
    notification_name : str
        A string identifier specifying the type or category of the notification.
    start_time : float
        The time at which the notification event started. It could be a timestamp or any relevant metric of time.
    elapsed_time : float
        The time duration for which the notification event has been active or displayed.

    Methods:
    -------
    __init__(self, notification_name, start_time, elapsed_time)
        Initializes the NotifyAction object with specified attributes values.
    """

    def __init__(self, notification_name, start_time, elapsed_time):
        """
        Creates a new NotifyAction object with specified values for the notification name, start time, and elapsed time.

        Parameters:
        ----------
        notification_name : str
            Specifies the type or category of the notification. It acts as an identifier for the notification action.
        start_time : float
            Sets the initial time or starting point of the notification action.
        elapsed_time : float
            Sets the duration for which the notification action has been active or in operation.
        """
        self.notification_name = notification_name
        self.start_time = start_time
        self.elapsed_time = elapsed_time


class ResizableFont:
    """
    A class that represents a font in pygame that can be resized.

    The ResizableFont allows changing its size, getting its name, and its height dynamically.

    Attributes:
    ----------
    path : str
        The file path to the TTF font file.
    size : int
        The current size of the font.
    font : pygame.font.Font
        The internal pygame Font object.

    Methods:
    -------
    __init__(self, path: str, size: int)
        Initializes the ResizableFont with a specific font file and size.
    resize(new_size: int)
        Changes the font size to new_size.
    get_name() -> str
        Returns the file path of the font.
    get_height() -> int
        Returns the current size of the font.
    """

    def __init__(self, path, size):
        """
        Instantiates a ResizableFont object.

        Parameters:
        ----------
        path : str
            The file path to the TTF font file.
        size : int
            The initial size of the font.
        """
        self.path = path
        self.size = size
        self.font = pygame.font.Font(self.path, self.size)

    def resize(self, new_size):
        """
        Resizes the font to the new specified size.

        Parameters:
        ----------
        new_size : int
            The new size for the font.
        """
        self.size = new_size
        self.font = pygame.font.Font(self.path, self.size)

    def get_name(self):
        """
        Retrieves the file path of the font.

        Returns:
        -------
        str
            The file path of the font.
        """
        return self.path

    def get_height(self):
        """
        Retrieves the current size of the font.

        Returns:
        -------
        int
            The current size of the font.
        """
        return self.size


class PauseMenu(Component):
    """
    A class representing a pause menu in a game, extending the Component class.

    The PauseMenu is a GUI element that presents different options like 'Resume Game',
    'Restart Game', 'Main Menu', and 'Exit Game' to the user when the game is paused.

    Attributes:
    ----------
    game_state : GameState
        The current state of the game.
    parent_rect : pygame.Rect
        The rectangle object where the PauseMenu will be drawn.
    options : list of str
        A list of options that will be displayed in the pause menu.
    option_rects : list of Component
        A list of Component objects representing the positions of options.
    current_option_index : int
        The index of the currently selected option.
    surface : pygame.Surface
        The surface on which the PauseMenu is drawn.

    Methods:
    -------
    __init__(self, game_state, parent_rect)
        Initializes the PauseMenu with the game state and the parent rectangle.
    draw(self, screen)
        Draws the pause menu on the screen.
    handle_event(self, event)
        Handles the user input events, like mouse motion and mouse button down.
    """

    def __init__(self, game_state, parent_rect):
        """
        Initializes the PauseMenu object with specified game state and parent rectangle.

        Parameters:
        ----------
        game_state : GameState
            The current state of the game.
        parent_rect : pygame.Rect
            The rectangle object where the PauseMenu will be drawn.
        """
        super().__init__(game_state, parent_rect, 0.25, 0.25, 0.375, 0.375)
        self.options = ["Resume Game", "Restart Game", "Main Menu", "Exit Game"]
        self.option_rects = []
        self.current_option_index = None

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 240))

        for i, option in enumerate(self.options):
            option_rect = Component(game_state, self.rect, 1, 1 / len(self.options), 0, i / len(self.options))
            self.option_rects.append(option_rect)

    def draw(self, screen):
        """
        Draws the pause menu on the specified screen.

        Parameters
        ----------
        screen : pygame.Surface
            The screen on which the pause menu will be drawn.
        """
        screen.blit(self.surface, (self.x, self.y))
        for i, (option_rect, option) in enumerate(zip(self.option_rects, self.options)):
            if i == self.current_option_index:
                pygame.draw.rect(screen, (218, 165, 32), option_rect.rect, 3)  # draw border

            text = option_rect.font_small.font.render(option, True, (218, 165, 32))
            draw_centered_text(screen, text, option_rect)

    def handle_event(self, event):
        """
        Handles the user input events.

        Parameters
        ----------
        event : pygame.event.Event
            The event object that has been triggered.
        """
        if event.type == pygame.MOUSEMOTION:
            self.current_option_index = None
            for i, option_rect in enumerate(self.option_rects):
                if option_rect.rect.collidepoint(event.pos):
                    self.current_option_index = i
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.current_option_index is not None:
                self.game_state.pause_menu_option = self.current_option_index


class MainMenu(Component):
    """
    A class representing the main menu of a game, extending the Component class.

    Attributes:
    ----------
    game_state : GameState
        The current state of the game.
    parent_rect : pygame.Rect
        The rectangle object where the MainMenu will be drawn.
    background_image : pygame.Surface
        The background image of the main menu.
    hover_border : pygame.Surface
        The image used as the border when an option is hovered over.
    options : list of str
        A list of options available in the main menu.
    menu_items : list of Component
        Components representing menu items.
    hovered_item : Component or None
        The menu item currently being hovered over.

    Methods:
    -------
    __init__(self, game_state, parent_rect)
        Initializes the MainMenu object.
    create_menu_items(self)
        Creates the menu items as Component objects and stores them in self.menu_items.
    draw(self, screen)
        Draws the main menu on the specified screen.
    handle_event(self, event)
        Handles the user input events, like mouse motion and mouse button down.
    """

    def __init__(self, game_state, parent_rect):
        """
        Initializes the MainMenu with the game state, parent rectangle, and necessary images.

        Parameters:
        ----------
        game_state : GameState
            The current state of the game.
        parent_rect : pygame.Rect
            The rectangle object where the MainMenu will be drawn.
        """
        super().__init__(game_state, parent_rect, 1, 1, 0, 0)
        self.background_image = pygame.image.load('img/main_menu.jpeg')
        self.hover_border = pygame.image.load('img/icons/borderBtn.png')
        self.options = ['Start Game', 'Options', 'Statistics', 'Quit Game']
        self.menu_items = []
        self.hovered_item = None
        self.create_menu_items()

    def create_menu_items(self):
        """
        Creates Component objects for each menu item and stores them in self.menu_items.
        """
        option_height_ratio = 0.08
        option_width_ratio = 0.25
        option_y_start_ratio = 0.55
        for index, option in enumerate(self.options):
            option_y_ratio = option_y_start_ratio + index * (option_height_ratio + 0.01)
            option_component = Component(self.game_state, self.rect, option_width_ratio, option_height_ratio,
                                         0.5 - option_width_ratio / 2, option_y_ratio)
            option_component.text = option  # store text, not the rendered Surface
            self.menu_items.append(option_component)

    def draw(self, screen):
        """
        Draws the MainMenu and its items on the specified screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The screen on which the main menu will be drawn.
        """
        screen.blit(pygame.transform.scale(self.background_image, (self.width, self.height)), (self.x, self.y))
        for item in self.menu_items:
            text = self.font_small.font.render(item.text, True, (218, 165, 32))
            text_pos = text.get_rect(center=item.rect.center)
            if item == self.hovered_item:
                border_size = (text.get_width() + 20, text.get_height() + 100)
                scaled_hover_border = scale_surface(self.hover_border, border_size)
                border_pos = scaled_hover_border.get_rect(center=text_pos.center)
                screen.blit(scaled_hover_border, border_pos.topleft)
                draw_text_with_outline(screen, item.text, self.font_small.font, (218, 165, 32), (0, 0, 0),
                                       text_pos.topleft, 2)
            else:
                draw_text_with_outline(screen, item.text, self.font_small.font, (218, 165, 32), (0, 0, 0),
                                       text_pos.topleft, 2)

    def handle_event(self, event):
        """
        Handles user input events such as mouse motion and mouse button clicks.

        Parameters:
        ----------
        event : pygame.event.Event
            The event object that has been triggered.
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered_item = None
            for item in self.menu_items:
                if item.rect.collidepoint(event.pos):
                    self.hovered_item = item
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered_item is not None:
                self.game_state.main_menu_option = self.menu_items.index(self.hovered_item)


class PanelEnd(Component):
    """
    A class representing the end panel of a game, extending the Component class.

    Attributes:
    ----------
    game_state : GameState
        The current state of the game.
    parent_rect : pygame.Rect
        The rectangle object where the PanelEnd will be drawn.
    background_win : pygame.Surface
        The background image displayed when the player wins.
    background_lose : pygame.Surface
        The background image displayed when the player loses.
    background_draw : pygame.Surface
        The background image displayed when the game is a draw.
    background : pygame.Surface or None
        The current background image.
    hover_border : pygame.Surface
        The image used as the border when an option is hovered over.
    options : list of str
        A list of options available in the end panel.
    menu_items : list of Component
        Components representing menu items.
    hovered_item : Component or None
        The menu item currently being hovered over.

    Methods:
    -------
    __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the PanelEnd object.
    draw(self, screen)
        Draws the panel, including background, table contents, and menu items, on the screen.
    create_menu_items(self)
        Creates and initializes the menu items to be displayed on the end panel.
    draw_table_contents(self)
        Draws the content within the table showing the game's round results.
    handle_event(self, event)
        Handles mouse events to interact with the menu items.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the PanelEnd object with the necessary attributes such as game state,
        parent rectangle, and other properties to manage the appearance of the end panel.

        Parameters:
        ----------
        game_state : GameState
            The current state of the game.
        parent_rect : pygame.Rect
            The rectangle object where the PanelEnd will be drawn.
        width_ratio : float
            The ratio to determine the width of the PanelEnd relative to its parent.
        height_ratio : float
            The ratio to determine the height of the PanelEnd relative to its parent.
        x_ratio : float
            The horizontal ratio to determine the position of the PanelEnd.
        y_ratio : float
            The vertical ratio to determine the position of the PanelEnd.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)

        # Load the background images
        self.background_win = pygame.image.load(f'img/icons/end_win.png')
        self.background_lose = pygame.image.load(f'img/icons/end_lose.png')
        self.background_draw = pygame.image.load(f'img/icons/end_draw.png')
        self.background = None
        self.hover_border = pygame.image.load('img/icons/borderBtn.png')

        # Initialize the button attributes
        self.options = ['Restart Game', 'Main Menu']
        self.menu_items = []
        self.hovered_item = None
        self.create_menu_items()

        self.table = None
        self.table_rect = None

    def draw(self, screen):
        """
        Draws the PanelEnd on the screen, managing the background based on the game's end state,
        and handling the visualization of table contents and menu items.

        Parameters:
        ----------
        screen : pygame.Surface
            The surface of the screen where the PanelEnd will be drawn.
        """
        if self.background is None:
            if self.game_state.end_state == 'win':
                self.background = self.background_win
            elif self.game_state.end_state == 'lose':
                self.background = self.background_lose
            elif self.game_state.end_state == 'draw':
                self.background = self.background_draw
            else:
                return
        screen.fill((0, 0, 0))
        # Scale the background image to be as wide as the screen and centered
        background_scaled = scale_surface(self.background, (self.width, self.height * 0.5))

        # Initialize the table with the same size as the background image
        self.table = pygame.Surface((background_scaled.get_width() / 2, background_scaled.get_height() / 3))

        # Compute the table position such that it's horizontally centered and right below the background image
        table_top = self.y + background_scaled.get_height()
        table_left = (self.width - background_scaled.get_width()) / 2 + background_scaled.get_width() / 4
        self.table_rect = pygame.Rect(table_left, table_top, background_scaled.get_width() / 2,
                                      background_scaled.get_height() / 3)

        # Draw the background and the table
        screen.blit(background_scaled, ((self.width - background_scaled.get_width()) / 2, self.y))
        # Draw the table contents
        self.draw_table_contents()
        screen.blit(self.table, self.table_rect.topleft)

        # Draw buttons
        for item in self.menu_items:
            text = self.font_small.font.render(item.text, True, (218, 165, 32))
            text_pos = text.get_rect(center=item.rect.center)
            if item == self.hovered_item:
                border_size = (text.get_width() + 20, text.get_height() + 100)
                scaled_hover_border = scale_surface(self.hover_border, border_size)
                border_pos = scaled_hover_border.get_rect(center=text_pos.center)
                screen.blit(scaled_hover_border, border_pos.topleft)
                draw_text_with_outline(screen, item.text, self.font_small.font, (218, 165, 32), (0, 0, 0),
                                       text_pos.topleft, 2)
            else:
                draw_text_with_outline(screen, item.text, self.font_small.font, (218, 165, 32), (0, 0, 0),
                                       text_pos.topleft, 2)

    def create_menu_items(self):
        """
        Creates and initializes the menu items to be displayed on the end panel, setting up their
        positions, sizes, and textual contents.
        """
        option_height_ratio = 0.08
        option_width_ratio = 0.25
        option_y_start_ratio = 0.75  # Adjust this ratio to move the buttons vertically
        for index, option in enumerate(self.options):
            option_y_ratio = option_y_start_ratio + index * (option_height_ratio + 0.01)
            option_component = Component(self.game_state, self.rect, option_width_ratio, option_height_ratio,
                                         0.5 - option_width_ratio / 2, option_y_ratio)
            option_component.text = option  # store text, not the rendered Surface
            self.menu_items.append(option_component)

    def draw_table_contents(self):
        """
        Manages and draws the contents of the table that showcases the results of the game rounds,
        aligning texts and results in an organized manner.
        """
        font = ResizableFont('Gwent.ttf', 20)
        text_color = (218, 165, 32)

        cell_width = self.table.get_width() / 4
        cell_height = self.table.get_height() / 3

        headers = ["", "Round 1", "Round 2", "Round 3"]
        results_player = self.game_state.results_player
        results_opponent = self.game_state.results_opponent

        # Draw the headers
        for col in range(4):
            x = col * cell_width
            text = font.font.render(headers[col], True, text_color)
            text_rect = text.get_rect(center=(x + cell_width / 2, cell_height / 2))
            self.table.blit(text, text_rect)

        # Draw the player results
        text = font.font.render("Player", True, text_color)
        text_rect = text.get_rect(center=(cell_width / 2, 1.5 * cell_height))
        self.table.blit(text, text_rect)
        for col in range(1, 4):
            x = col * cell_width
            y = cell_height
            text = font.font.render(str(results_player[col - 1]), True, text_color)
            text_rect = text.get_rect(center=(x + cell_width / 2, y + cell_height / 2))
            self.table.blit(text, text_rect)

        # Draw the opponent results
        text = font.font.render("Opponent", True, text_color)
        text_rect = text.get_rect(center=(cell_width / 2, 2.5 * cell_height))
        self.table.blit(text, text_rect)
        for col in range(1, 4):
            x = col * cell_width
            y = 2 * cell_height
            text = font.font.render(str(results_opponent[col - 1]), True, text_color)
            text_rect = text.get_rect(center=(x + cell_width / 2, y + cell_height / 2))
            self.table.blit(text, text_rect)

    def handle_event(self, event):
        """
        Handles mouse events, managing hover effects and button clicks, to interact with the menu
        items, triggering corresponding game actions based on user inputs.

        Parameters:
        ----------
        event : pygame.event.Event
            An event caught by pygame's event handling, such as mouse motions or mouse button presses.
        """

        if event.type == pygame.MOUSEMOTION:
            self.hovered_item = None
            for item in self.menu_items:
                if item.rect.collidepoint(event.pos):
                    self.hovered_item = item
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered_item is not None:
                self.game_state.end_game_option = self.menu_items.index(self.hovered_item)


class PanelStart(Component):
    """
    A PanelStart object represents the start panel in the game.
    It inherits attributes and methods from the Component class.

    Attributes:
    ----------
    background : pygame.Surface
        The background image of the start panel.
    side_panel : pygame.Surface
        The side panel image which includes the scrollable deck list.
    background_scaled : pygame.Surface
        The scaled version of the background to fit the current window size.
    scroll_image : pygame.Surface
        The image representing the scrollable part of the deck list.
    scroll_image_scaled : pygame.Surface
        The scaled version of the scroll_image.
    hover_border : pygame.Surface
        The border image used for hovered items in the deck list.
    items : list of str
        A list containing the names of items (decks) to be displayed.
    item_height : int
        The height of each item (deck) in the deck list.
    scroll_speed : int
        The speed at which the deck list scrolls.
    font : ResizableFont
        The font used for rendering text within the panel.
    scrollable_surface : pygame.Surface
        The surface on which the scrollable items (decks) are drawn.
    visible_area : pygame.Rect
        The rectangle defining the visible area of the scrollable_surface.
    hovered_item : str or None
        The item currently being hovered by the mouse pointer.
    selected_item : str or None
        The item currently selected by the user.
    scroll_x : int
        The x-coordinate where the scrollable_surface is drawn.
    scroll_y : int
        The y-coordinate where the scrollable_surface is drawn.

    Methods:
    -------
    draw(screen)
        Draws the start panel on the screen, managing background, side panel, and scrollable items.
    handle_event(event)
        Handles mouse events for interaction with the scrollable items, managing selection and scrolling.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the PanelStart object with necessary attributes such as game state,
        parent rectangle, images, and other visual properties.

        Parameters:
        ----------
        game_state : object
            The current state of the game.
        parent_rect : pygame.Rect
            The rectangle object where the PanelStart will be drawn.
        width_ratio : float
            The ratio to determine the width of the PanelStart relative to its parent.
        height_ratio : float
            The ratio to determine the height of the PanelStart relative to its parent.
        x_ratio : float
            The horizontal ratio to determine the position of the PanelStart.
        y_ratio : float
            The vertical ratio to determine the position of the PanelStart.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.background = pygame.image.load(f'img/start_menu_background.jpeg')
        self.side_panel = pygame.image.load(f'img/side_panel.png')
        self.background_scaled = pygame.transform.scale(self.background, (self.width, self.height))
        self.scroll_image = pygame.image.load(f'img/panel_inside.png')
        self.scroll_image_scaled = scale_surface(self.scroll_image,
                                                 (self.side_panel.get_width() / 2, self.side_panel.get_height()))
        self.hover_border = pygame.image.load(f'img/icons/borderBtn.png')
        self.items = ['Deck {}'.format(i) for i in range(1, 21)]
        self.item_height = 80  # Replace this with your desired item height
        self.scroll_speed = 10  # Replace this with your desired scroll speed
        self.font = ResizableFont('Gwent.ttf', 35)

        self.scrollable_surface = pygame.Surface(
            (self.scroll_image_scaled.get_width(), len(self.items) * self.item_height), pygame.SRCALPHA)
        self.visible_area = pygame.Rect(0, 0, self.scroll_image_scaled.get_width(),
                                        self.scroll_image_scaled.get_height())
        self.hovered_item = None
        self.selected_item = None
        self.scroll_x = self.x + self.side_panel.get_width() / 4
        self.scroll_y = self.y + self.side_panel.get_height() / 2

    def draw(self, screen):
        """
        Draws the start panel, including the background, side panel, and scrollable items (decks),
        and manages their visual appearance and positions.

        Parameters:
        ----------
        screen : pygame.Surface
            The surface of the screen where the PanelStart will be drawn.
        """
        screen.blit(self.background_scaled, (self.x, self.y))
        screen.blit(self.side_panel, (self.x, self.y))

        self.scrollable_surface.fill((0, 0, 0, 0))  # Clear the surface with a transparent color
        for i, item in enumerate(self.items):
            item_rect = pygame.Rect(0, i * self.item_height, self.scrollable_surface.get_width(), self.item_height)
            if item == self.hovered_item or item == self.selected_item:
                pygame.draw.rect(self.scrollable_surface, (20, 20, 20, 100), item_rect)  # Highlight hovered item
                border_size = (item_rect.width + 20, item_rect.height + 20)
                scaled_hover_border = scale_surface(self.hover_border, border_size)
                border_pos = scaled_hover_border.get_rect(center=item_rect.center)
                self.scrollable_surface.blit(scaled_hover_border, border_pos.topleft)  # Add the border image
            else:
                pygame.draw.rect(self.scrollable_surface, (20, 20, 20, 100), item_rect)  # Make other items less opaque

            text_position = item_rect.center
            # Draw the text outline
            for x_offset in range(-1, 2):
                for y_offset in range(-1, 2):
                    if x_offset == 0 and y_offset == 0:
                        continue
                    outline_position = (text_position[0] + x_offset, text_position[1] + y_offset)
                    outline_surface = self.font.font.render(item, True, (0, 0, 0))
                    self.scrollable_surface.blit(outline_surface, outline_surface.get_rect(center=outline_position))

            # Draw the main text
            item_surface = self.font.font.render(item, True, (218, 165, 32))
            self.scrollable_surface.blit(item_surface, item_surface.get_rect(center=text_position))

        screen.blit(self.scroll_image_scaled, (self.scroll_x, self.scroll_y))
        screen.blit(self.scrollable_surface, (self.scroll_x, self.scroll_y), area=self.visible_area)

    def handle_event(self, event):
        """
        Handles mouse events to enable interaction with the scrollable items (decks),
        such as selection and scrolling.

        Parameters:
        ----------
        event : pygame.event.Event
            An event caught by pygame's event handling, such as mouse motions or mouse button presses.
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_pos
        mouse_y -= self.scroll_y
        self.hovered_item = None
        if self.scroll_image_scaled.get_rect(topleft=(self.scroll_x, self.scroll_y)).collidepoint(mouse_pos):
            for i in range(self.visible_area.y // self.item_height,
                           min(len(self.items),
                               (self.visible_area.y + self.visible_area.height) // self.item_height)):
                item_rect = pygame.Rect(self.scroll_x, i * self.item_height - self.visible_area.y,
                                        self.scroll_image_scaled.get_width(), self.item_height)
                if item_rect.collidepoint((mouse_x, mouse_y)):
                    self.hovered_item = self.items[i]
                    break

        if event.type == pygame.MOUSEBUTTONDOWN:
            max_scroll = max(0, self.scrollable_surface.get_height() - self.visible_area.height)
            if event.button == 4:  # Scroll up.
                self.visible_area.y = max(0, self.visible_area.y - self.scroll_speed)
            elif event.button == 5:  # Scroll down.
                self.visible_area.y = min(max_scroll, self.visible_area.y + self.scroll_speed)
            elif event.button == 1 and self.hovered_item is not None:
                self.selected_item = self.hovered_item


class ConsolePanel(Component):
    """
    A ConsolePanel object represents the console panel in the game where various commands
    can be entered for different purposes such as debugging, manipulating game state, etc.
    It inherits attributes and methods from the Component class.

    Attributes:
    ----------
    game_state : object
        The current state of the game.
    commands_history : list of str
        A list containing the history of entered commands.
    commands : dict
        A dictionary mapping command names to their corresponding functions.
    current_input : str
        The current text input entered by the user in the console.
    font : pygame.font.Font
        The font used to render text in the console.
    console_color : tuple of int
        The RGB color used for the console background.
    text_color : tuple of int
        The RGB color used for the text within the console.

    Methods:
    -------
    draw(screen)
        Draws the console panel on the screen, including the background,
        previously entered commands, and the current input.
    handle_event(event)
        Handles keyboard events to manage user input within the console.
    process_command(command_str)
        Processes and executes the entered command string.
    quit_game()
        Handles the 'quit' command to exit the game.
    clear_console()
        Handles the 'clear' command to clear the console history.
    give_card(player_id, card_id)
        Handles the 'give' command to give a specific card to a player.
    step(mode)
        Handles the 'step' command to manage step mode in the game.
    tools(mode)
        Handles the 'tools' command to manage developer tools.
    ai(mode)
        Handles the 'ai' command to manage AI functionality in the game.
    log(action, name)
        Handles the 'log' command to manage game logs.
    """

    def __init__(self, game_state, screen_rect):
        """
        Initializes the ConsolePanel object with necessary attributes such as game state,
        screen rectangle, and other visual properties.

        Parameters:
        ----------
        game_state : object
            The current state of the game.
        screen_rect : pygame.Rect
            The rectangle object where the ConsolePanel will be drawn.
        """
        super().__init__(game_state, screen_rect, 1, 1, 0,
                         0)
        self.game_state = game_state
        self.commands_history = []
        self.commands = {
            'quit': self.quit_game,
            'clear': self.clear_console,
            'give': self.give_card,
            'step': self.step,
            'tools': self.tools,
            'ai': self.ai,
            'log': self.log
        }
        self.current_input = ""
        self.font = pygame.font.Font(None, 36)
        self.console_color = (50, 50, 50)
        self.text_color = (255, 255, 255)

    def draw(self, screen):
        """
        Draws the console, including the background, previously entered commands,
        and the current input, on the screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The surface of the screen where the ConsolePanel will be drawn.
        """
        # Draw the console rectangle
        pygame.draw.rect(screen, self.console_color, self.rect)

        # Draw previously entered commands
        y_offset = 10  # Start position for text rendering
        for command in self.commands_history[
                       -self.rect.height // 40:]:  # Adjust the slicing based on font size and rect height
            text_surface = self.font.render(command, True, self.text_color)
            screen.blit(text_surface, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += 40  # Adjust based on font size and desired spacing

        # Draw the current input
        input_surface = self.font.render(self.current_input, True, self.text_color)
        screen.blit(input_surface, (self.rect.x + 10, self.rect.y + self.rect.height - 40))

    def handle_event(self, event):
        """
        Handles keyboard events to enable text entry and command execution
        within the console.

        Parameters:
        ----------
        event : pygame.event.Event
            An event caught by pygame's event handling.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Process the current input
                self.process_command(self.current_input)
                self.current_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.current_input = self.current_input[:-1]
            else:
                # Add typed character to current input
                if event.key is not pygame.K_BACKQUOTE:
                    self.current_input += event.unicode

    def process_command(self, command_str):
        """
        Processes and executes the entered command string by calling the corresponding
        command function with necessary parameters.

        Parameters:
        ----------
        command_str : str
            The string containing the command and parameters entered the console.
        """
        # Split the command string into words
        words = command_str.split()

        # The first word is the command, the rest are parameters
        command, *params = words

        # Store the command for later display
        self.commands_history.append(command_str)

        # Get the command function from the dictionary
        func = self.commands.get(command)

        # If the command is not found, print an error message
        if func is None:
            print(f"Unknown command: {command}")
            return

        # Call the command function with the parameters
        try:
            func(*params)
        except Exception as e:
            print(f"Error executing command: {str(e)}")

    @staticmethod
    def quit_game():
        """
        Handles the 'quit' command to exit the game. Terminates the pygame instance
        and any additional quitting logic should be added here.
        """
        pygame.quit()

    def clear_console(self):
        """
        Handles the 'clear' command to clear the console's command history,
        effectively cleaning the console display.
        """
        print("Clearing the console...")
        # Add your console clearing logic here
        self.commands_history.clear()

    def give_card(self, player_id, card_id):
        """
        Handles the 'give' command to give a specific card to a player.
        Updates the game state accordingly.

        Parameters:
        ----------
        player_id : str
            The ID of the player who will receive the card.
        card_id : str
            The ID of the card to be given.
        """
        print(f"Giving card {card_id} to player {player_id}...")
        self.game_state.game.give_card(int(player_id), int(card_id))
        self.game_state.set_state('normal')

    def step(self, mode):
        """
        Handles the 'step' command to manage step mode in the game, toggling
        it on or off based on the mode parameter.

        Parameters:
        ----------
        mode : str
            The desired state of step mode, 'on' or 'off'.
        """
        print(f"Setting step mode to {mode}...")
        # Add your step setting logic here
        if mode == 'on':
            self.game_state.stepper_on = True
        elif mode == 'off':
            self.game_state.stepper_on = False

    def tools(self, mode):
        """
        Handles the 'tools' command, toggling developer tools on or off
        based on the mode parameter.

        Parameters:
        ----------
        mode : str
            The desired state of developer tools, 'on' or 'off'.
        """
        print("Developer tools...")
        # Add your switching logic here
        if mode == 'on':
            self.game_state.developer_tools = True
        elif mode == 'off':
            self.game_state.developer_tools = False

    def ai(self, mode):
        """
        Handles the 'ai' command, toggling AI functionality on or off
        based on the mode parameter.

        Parameters:
        ----------
        mode : str
            The desired state of AI functionality, 'on' or 'off'.
        """
        if mode == 'on':
            self.game_state.ai = True
        elif mode == 'off':
            self.game_state.ai = False

    def log(self, action, name):
        """
        Handles the 'log' command to manage game logs. It either saves or loads logs
        based on the action parameter.

        Parameters:
        ----------
        action : str
            Specifies the action to be performed on logs, either 'save' or 'load'.
        name : str
            The name associated with the log for saving or loading purposes.
        """
        if action == 'save':
            self.game_state.stepper.save(name)
        elif action == 'load':
            self.game_state.stepper.load(name)


class MyGameGui:
    """
    This class represents the main GUI of the game, initializing the game window,
    handling game states, and managing game components such as notifications, AI previews, and game timings.

    Attributes:
    ----------
    width : int
        The width of the game window, obtained from the display info.
    height : int
        The height of the game window, obtained from the display info.
    fps : int
        Frames per second, controls the game's refresh rate.
    screen : pygame.Surface
        The main surface where game elements are drawn, set to full-screen mode.
    clock : pygame.time.Clock
        An object to help track time within the game.
    running : bool
        A flag indicating whether the game is currently running.
    cards : list
        A list of game cards loaded from a file.
    game : Game
        An instance of the Game class, managing the main game logic.
    game_state : GameState
        An instance managing the current state of the game.
    timing_data : dict
        A dictionary tracking time spent on various game operations.
    preview_start_time : int or None
        Keeps track of when a preview started.
    action_ai_draw : Various types
        Holds data related to AI actions in the game.
    index_action_ai : int or None
        Index related to the AI action currently being processed.
    notification : Notify
        An instance of the Notify class to manage notifications in the game.
    notifications : list
        A list to manage multiple notifications.
    ai_preview : bool
        A flag to control whether AI previews are currently active.
    round_index : int
        Keeps track of the current round index in the game.
    width : int
        The width of the game window, obtained from the display info.
    height : int
        The height of the game window, obtained from the display info.
    fps : int
        Frames per second, controls the game's refresh rate.
    screen : pygame.Surface
        The main surface where game elements are drawn, set to full-screen mode.
    clock : pygame.time.Clock
        An object to help track time within the game.
    running : bool
        A flag indicating whether the game is currently running.
    cards : list
        A list of game cards loaded from a file.
    game : Game
        An instance of the Game class, managing the main game logic.
    game_state : GameState
        An instance managing the current state of the game.
    timing_data : dict
        A dictionary tracking time spent on various game operations.
    preview_start_time : int or None
        Keeps track of when a preview started.
    action_ai_draw : Various types
        Holds data related to AI actions in the game.
    index_action_ai : int or None
        Index related to the AI action currently being processed.
    notification : Notify
        An instance of the Notify class to manage notifications in the game.
    notifications : list
        A list to manage multiple notifications.
    ai_preview : bool
        A flag to control whether AI previews are currently active.
    round_index : int
        Keeps track of the current round index in the game.

    Methods:
    --------
    run_game(self)
        Initiates and maintains the main game loop, handling events and updates.

    update_display(self)
        Handles the drawing and updating of game elements on the screen.

    process_events(self)
        Manages and processes various game events such as user inputs and AI actions.

    manage_game_states(self)
        Manages transitions between different game states and handles related actions.

    load_cards(self, file_path: str)
        Loads game cards from a file and initializes them in the game.
    """

    def __init__(self, fps=60):
        """
        Initialize the game's main components and set the initial game state.

        Initializes various panels such as the game panel, pause menu, main menu,
        end panel, start panel, and console panel. Sets the initial end state as 'win'
        and the game state as 'normal'.
        """
        pygame.init()
        info_object = pygame.display.Info()
        self.width = info_object.current_w
        self.height = info_object.current_h
        self.fps = fps
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True
        self.cards = load_file_game('Gwent.csv')
        self.game = Game(self.cards)
        self.game_state = GameState()
        self.game_state.game_state_matrix = self.game.game_state_matrix.state_matrix_0
        self.game_state.game_state_matrix_opponent = self.game.game_state_matrix.state_matrix_1
        self.game_state.game = self.game
        self.timing_data = {
            "handle_events": [],
            "update": [],
            "draw": [],
            "screen_blit": [],
            "panel_game_draw": [],
            "pygame_display_flip": [],
            "update action": [],
            "game state call": [],
            "step call": [],
            "set_state call": []
        }
        self.preview_start_time = None
        self.action_ai_draw = None
        self.index_action_ai = None
        self.notification = Notify(self.game_state, self.screen.get_rect(), 1, 0.14, 0, 0.43)
        self.notifications = []
        self.ai_preview = False
        self.round_index = 0
        self.panel_game = PanelGame(self.game_state, self.screen.get_rect())
        self.pause_menu = PauseMenu(self.game_state, self.screen.get_rect())
        self.main_menu = MainMenu(self.game_state, self.screen.get_rect())
        self.panel_end = PanelEnd(self.game_state, self.screen.get_rect(), 1, 1, 0, 0)
        self.panel_start = PanelStart(self.game_state, self.screen.get_rect(), 1, 1, 0, 0)
        self.panel_console = ConsolePanel(self.game_state, self.screen.get_rect())
        self.game_state.end_state = 'win'
        self.game_state.set_state('normal')

    def run(self):
        """
        Main game loop. Handles events, updates game state, and draws on the screen.

        Runs a loop until the game stops running, handling events, updating the game
        state, and drawing elements on the screen, then quitting pygame.
        """
        while self.running:
            self.clock.tick(self.fps)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def handle_events(self):
        """
        Handle user inputs and game events.

        Processes various events such as quitting, key presses, and mouse actions.
        Depending on the game state, it directs the events to be handled by the
        appropriate game panels.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.game_state.state == 'normal':
                    self.game_state.set_state('menu')
                elif event.key == pygame.K_SPACE and self.game_state.state == 'normal':
                    self.game_state.parameter_actions.append('-1')
                elif event.key == pygame.K_ESCAPE and self.game_state.state == 'menu':
                    self.game_state.set_state('normal')
                elif event.key == pygame.K_BACKQUOTE:
                    if self.game_state.state == 'console':
                        self.game_state.set_state(self.game_state.previous_state)
                        self.game_state.previous_state = 'console'
                    else:
                        self.game_state.previous_state = self.game_state.state
                        self.game_state.set_state('console')
            if self.game_state.state in ['normal', 'dragging', 'carousel']:
                self.panel_game.handle_event(event)
            elif self.game_state.state in ['menu']:
                self.pause_menu.handle_event(event)
            elif self.game_state.state in ['main menu']:
                self.main_menu.handle_event(event)
            elif self.game_state.state in ['end screen']:
                self.panel_end.handle_event(event)
            elif self.game_state.state in ['start screen']:
                self.panel_start.handle_event(event)
            elif self.game_state.state in ['console']:
                self.panel_console.handle_event(event)

    def update(self):
        """
        Update the game state based on user inputs and AI actions.

        Depending on the current game state, it updates game parameters, performs
        AI steps, and executes actions selected in the menus.
        """
        if self.game_state.state in ['normal', 'dragging', 'carousel']:
            if len(self.game_state.parameter_actions) > 0 and self.game_state.state == 'normal':
                bool_actions, actions = self.game.valid_actions()
                action = None
                action_a = None
                for a in self.game_state.parameter_actions:
                    if a in actions:
                        action = self.game.get_index_of_action(a)
                        action_a = a

                self.game_state.parameter_actions.clear()
                self.game_state.parameter = None
                if action is not None and self.game.turn == 0:
                    player_score = int(self.game_state.game_state_matrix[0][145])
                    opponent_score = int(self.game_state.game_state_matrix[0][146])

                    if self.game_state.stepper_on:
                        self.game_state.stepper.step(self.game.turn, action)
                    result = self.game.step(action)
                    self.game_state.set_state('normal')
                    if action_a == '-1':
                        self.notifications.append(NotifyAction('me-pass', 0, 0))
                    if result > 0:
                        if result == 1:
                            self.notifications.append(NotifyAction('win-round', 0, 0))
                            self.game_state.results_player[self.round_index] = str(player_score)
                            self.game_state.results_opponent[self.round_index] = str(opponent_score)
                            self.round_index += 1
                        elif result == 2:
                            self.notifications.append(NotifyAction('lose-round', 0, 0))
                            self.game_state.results_player[self.round_index] = str(player_score)
                            self.game_state.results_opponent[self.round_index] = str(opponent_score)
                            self.round_index += 1
                        elif result == 3:
                            self.notifications.append(NotifyAction('draw-round', 0, 0))
                            self.game_state.results_player[self.round_index] = str(player_score)
                            self.game_state.results_opponent[self.round_index] = str(opponent_score)
                            self.round_index += 1
                        else:
                            if result == 4:
                                self.game_state.end_state = 'lose'
                                self.game_state.results_player[self.round_index] = str(player_score)
                                self.game_state.results_opponent[self.round_index] = str(opponent_score)
                                self.round_index += 1
                            elif result == 5:
                                self.game_state.end_state = 'win'
                                self.game_state.results_player[self.round_index] = str(player_score)
                                self.game_state.results_opponent[self.round_index] = str(opponent_score)
                                self.round_index += 1
                            else:
                                self.game_state.end_state = 'draw'
                                self.game_state.results_player[self.round_index] = str(player_score)
                                self.game_state.results_opponent[self.round_index] = str(opponent_score)
                                self.round_index += 1
                            self.game_state.set_state('end screen')

                    if result < 3 and self.game.turn == 1:
                        self.notifications.append(NotifyAction('op-turn', 0, 0))
                    elif 0 < result < 3 and self.game.turn == 0:
                        self.notifications.append(NotifyAction('me-turn', 0, 0))

            if self.game.turn == 1:
                if self.game_state.ai:
                    self.step_by_ai()
        if self.game_state.state in ['menu']:
            action = self.game_state.pause_menu_option
            self.game_state.pause_menu_option = None
            if action is not None:
                if action == 0:
                    self.game_state.set_state('normal')
                elif action == 1:
                    self.restart_game()
                elif action == 2:
                    self.game_state.set_state('main menu')
                elif action == 3:
                    self.running = False
        if self.game_state.state in ['main menu']:
            action = self.game_state.main_menu_option
            self.game_state.main_menu_option = None
            if action is not None:
                if action == 0:
                    self.game_state.set_state('start screen')
                elif action == 1:
                    pass
                elif action == 2:
                    pass
                elif action == 3:
                    self.running = False
        if self.game_state.state in ['end screen']:
            action = self.game_state.end_game_option
            self.game_state.end_game_option = None
            if action is not None:
                if action == 0:
                    self.restart_game()

                elif action == 1:
                    self.game_state.set_state('main menu')

    def step_by_ai(self):
        """
        Perform a game step by the AI.

        Determines a valid action for the AI and updates the game state based on the
        action chosen by the AI.
        """
        if self.index_action_ai is None:
            bool_actions, actions = self.game.valid_actions()
            index = random.randrange(len(actions))
            self.index_action_ai = index
            split = actions[index].split(',')
            if int(split[0]) > -1:
                preview_card = Card(int(split[0]), data, self.game_state)
                self.action_ai_draw = CardPreview(self.game_state, self.screen.get_rect(), preview_card)
                self.ai_preview = True
            else:
                self.ai_preview = True
                self.action_ai_draw = None

    def draw(self):
        """
        Draw the game elements on the screen based on the current game state.

        Depending on the current game state, it draws different panels and elements
        on the screen such as the game panel, menus, and notifications.
        """
        if self.game_state.state in ['normal', 'dragging', 'carousel']:
            self.panel_game.draw(self.screen)
            self.draw_ai_action()
            self.draw_notification()
        elif self.game_state.state in ['menu']:
            self.panel_game.draw(self.screen)
            self.pause_menu.draw(self.screen)
        elif self.game_state.state in ['main menu']:
            self.main_menu.draw(self.screen)
        elif self.game_state.state in ['end screen']:
            self.panel_end.draw(self.screen)
        elif self.game_state.state in ['start screen']:
            self.panel_start.draw(self.screen)
        elif self.game_state.state in ['console']:
            self.panel_console.draw(self.screen)
        pygame.display.flip()

    def draw_ai_action(self):
        """
        Draw the AI actions on the screen.

        Visualizes the actions taken by the AI on the screen, such as playing a card.
        """
        if self.ai_preview and len(self.notifications) == 0:
            if self.preview_start_time is None:
                self.preview_start_time = pygame.time.get_ticks()
            elapsed_time = pygame.time.get_ticks() - self.preview_start_time
            passed_opponent = self.game_state.game_state_matrix[0][147]
            if elapsed_time < 500 and self.game.turn == 1 and not passed_opponent and self.action_ai_draw is not None:
                self.action_ai_draw.draw(self.screen)
            else:
                self.preview_start_time = None
                self.ai_preview = False
                bool_actions, actions = self.game.valid_actions()
                player_score = int(self.game_state.game_state_matrix[0][145])
                opponent_score = int(self.game_state.game_state_matrix[0][146])
                if self.game_state.stepper_on:
                    self.game_state.stepper.step(self.game.turn,
                                                 self.game.get_index_of_action(actions[self.index_action_ai]))
                result = self.game.step(self.game.get_index_of_action(actions[self.index_action_ai]))
                self.game_state.set_state('normal')
                if actions[self.index_action_ai] == '-1':
                    self.notifications.append(NotifyAction('op-pass', 0, 0))
                if result > 0:
                    if result == 1:
                        self.notifications.append(NotifyAction('lose-round', 0, 0))
                        self.game_state.results_player[self.round_index] = str(player_score)
                        self.game_state.results_opponent[self.round_index] = str(opponent_score)
                        self.round_index += 1
                    elif result == 2:
                        self.notifications.append(NotifyAction('win-round', 0, 0))
                        self.game_state.results_player[self.round_index] = str(player_score)
                        self.game_state.results_opponent[self.round_index] = str(opponent_score)
                        self.round_index += 1
                    elif result == 3:
                        self.notifications.append(NotifyAction('draw-round', 0, 0))
                        self.game_state.results_player[self.round_index] = str(player_score)
                        self.game_state.results_opponent[self.round_index] = str(opponent_score)
                        self.round_index += 1
                    else:
                        if result == 4:
                            self.game_state.end_state = 'win'
                            self.game_state.results_player[self.round_index] = str(player_score)
                            self.game_state.results_opponent[self.round_index] = str(opponent_score)
                            self.round_index += 1
                        elif result == 5:
                            self.game_state.end_state = 'lose'
                            self.game_state.results_player[self.round_index] = str(player_score)
                            self.game_state.results_opponent[self.round_index] = str(opponent_score)
                            self.round_index += 1
                        else:
                            self.game_state.end_state = 'draw'
                            self.game_state.results_player[self.round_index] = str(player_score)
                            self.game_state.results_opponent[self.round_index] = str(opponent_score)
                            self.round_index += 1
                        self.game_state.set_state('end screen')
                if result < 3 and self.game.turn == 0:
                    self.notifications.append(NotifyAction('me-turn', 0, 0))
                elif 0 < result < 3 and self.game.turn == 1:
                    self.notifications.append(NotifyAction('op-turn', 0, 0))
                self.index_action_ai = None

    def draw_notification(self):
        """
        Draw notifications on the screen.

        Handles the visualization of notifications on the screen, managing their
        timing and removal after being displayed.
        """
        if len(self.notifications) > 0:
            first = self.notifications[0]
            if first.start_time == 0:
                first.start_time = pygame.time.get_ticks()
                first.elapsed_time = pygame.time.get_ticks() - first.start_time
                self.notification.set_notification(first.notification_name)
                self.notification.draw(self.screen)
            elif first.start_time != 0 and first.elapsed_time < 1000:
                first.elapsed_time = pygame.time.get_ticks() - first.start_time
                self.notification.draw(self.screen)
            else:
                self.notifications.remove(first)

    def print_average_times(self):
        """
        Print the average times for different functions.

        Calculates and prints the average execution times of different parts of the
        code for performance tracking.
        """
        for function, times in self.timing_data.items():
            if times:
                average_time = sum(times) / len(times)
                max_time = max(times)
                print(f"Average time for {function}: {average_time:.6f} seconds, Maximum time: {max_time:.6f} seconds")
            else:
                print(f"No timing data for {function}")

    def restart_game(self):
        """
        Restart the game.

        Resets the game to its initial state, reinitializing game components and
        clearing the game state.
        """
        self.running = True
        self.game = Game(self.cards)
        self.game_state.clear()
        self.game_state.game_state_matrix = self.game.game_state_matrix.state_matrix_0
        self.game_state.game_state_matrix_opponent = self.game.game_state_matrix.state_matrix_1
        self.preview_start_time = None
        self.action_ai_draw = None
        self.index_action_ai = None
        self.notification = Notify(self.game_state, self.screen.get_rect(), 1, 0.14, 0, 0.43)
        self.notifications = []
        self.ai_preview = False
        self.round_index = 0
        self.panel_game = PanelGame(self.game_state, self.screen.get_rect())
        self.pause_menu = PauseMenu(self.game_state, self.screen.get_rect())
        self.panel_end = PanelEnd(self.game_state, self.screen.get_rect(), 1, 1, 0, 0)
        self.game_state.set_state('normal')


if __name__ == '__main__':
    game = MyGameGui()
    game.run()
