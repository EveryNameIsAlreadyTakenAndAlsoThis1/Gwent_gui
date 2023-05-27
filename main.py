import pygame
import random
import time
import os
from Game.Game import Game


def load_file(file_path):
    """
    Loads card data from a CSV file into a dictionary.

    This function reads a CSV file where each line represents a card, and converts this data into
    a dictionary where the key is the card's ID and the value is another dictionary with the card's attributes.

    Parameters:
    -----------
    file_path : str
        The path to the CSV file to be read.

    Returns:
    --------
    dict
        A dictionary where the key is the card's ID (as an integer), and the value is a dictionary with the following structure:
        {
            'Name': str,        # The name of the card.
            'Id': int,          # The ID of the card.
            'Strength': int,    # The strength value of the card.
            'Ability': str,     # The ability of the card.
            'Type': str,        # The type of the card.
            'Placement': int,   # The placement of the card.
            'Count': int,       # The count of the card.
            'Faction': str,     # The faction of the card.
            'Image': str        # The image file name of the card.
        }

    Notes:
    ------
    This function assumes that the CSV file is formatted correctly, with each line containing the card attributes
    in the order specified in the returned dictionary. The function skips empty lines and lines that contain certain keywords.
    """
    with open(file_path, 'r') as f:
        data = f.read().splitlines()

    result = {}
    current_group = None

    for line in data:
        if line == '':
            continue

        if 'Northern Realms' in line or 'Scoiatael' in line or 'Neutral' in line or 'Nilfgaard' in line or 'Monsters' in line or 'Name' in line:
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
    with open(file_path, 'r') as f:
        data = f.read().splitlines()

    result = {}
    current_group = None

    for line in data:
        if line == '':
            continue

        if 'Northern Realms' in line or 'Scoiatael' in line or 'Neutral' in line or 'Nilfgaard' in line or 'Monsters' in line:
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
    Scales a Pygame surface proportionally to fit into the target size.

    Parameters
    ----------
    surface : pygame.Surface
        The surface to be scaled.
    target_size : tuple of int
        The target size (width, height).

    Returns
    -------
    pygame.Surface
        The scaled surface.
    """
    target_width, target_height = target_size
    width, height = surface.get_size()
    scale_factor = min(target_width / width, target_height / height)
    new_size = (round(width * scale_factor), round(height * scale_factor))
    return pygame.transform.smoothscale(surface, new_size)


def fit_text_in_rect(text, font, color, rect):
    """
    Adjusts the font size to fit the text into the rectangle.

    Parameters
    ----------
    text : str
        The text to be rendered.
    font : ResizableFont
        The font used to render the text.
    color : tuple of int
        The RGB color for the text.
    rect : pygame.Rect
        The rectangle within which the text should fit.

    Returns
    -------
    pygame.Surface
        The rendered text.
    """
    size = 1  # Start with a small font size
    font.resize(size)  # Use the same font but with a new size
    new_text = font.font.render(text, True, color)

    # Increase the size until the text no longer fits within the rectangle
    while new_text.get_width() <= rect.width and new_text.get_height() <= rect.height:
        size += 1
        font.resize(size)
        new_text = font.font.render(text, True, color)

    # If size was incremented past the point where text fits, reduce size by 1
    if new_text.get_width() > rect.width or new_text.get_height() > rect.height:
        size -= 1
        font.resize(size)
        new_text = font.font.render(text, True, color)

    return new_text


def draw_centered_text(screen, text, rect):
    """
    Draws the given text centered in the given rectangle.

    Parameters
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


def card_strength_text(screen, card, card_x, start_y, image):
    """
    Draws the strength text of a card if it exists.

    Parameters
    ----------
    screen : pygame.Surface
        The screen onto which the strength text should be drawn.
    card : Card
        The card whose strength text should be drawn.
    card_x : int
        The x-coordinate where the card is drawn.
    start_y : int
        The y-coordinate where the card is drawn.
    image : pygame.Surface
        The surface of the card image.
    """
    if card.strength_text is None:
        return

    font_small = ResizableFont('Arial Narrow.ttf', 20)
    text_color = (0, 0, 0)
    if card.type == 'Hero':
        text_color = (255, 255, 255)
    elif card.type == 'Unit' and card.strength == card.strength_text:
        text_color = (0, 0, 0)
    elif card.type == 'Unit' and card.strength < card.strength_text:
        text_color = (0, 100, 0)
    elif card.type == 'Unit' and card.strength > card.strength_text:
        text_color = (106, 28, 15)
    text_rect = pygame.Rect(card_x, start_y, image.get_width() / 2.7,
                            image.get_height() / 4)
    text = font_small.font.render(str(card.strength_text), True, text_color)
    draw_centered_text(screen, text, text_rect)


def check_valid_action(card_board, card_dragged, game_state):
    if card_board is None or card_dragged is None:
        pass
    else:
        game_state.parameter_actions.append(
            str(card_dragged._id) + ',' + str(card_board.parent_container.row_id) + ',' + str(card_board._id))


data = load_file('Gwent.csv')


class Observer:
    """
    The Observer class represents an observer in the observer design pattern.
    This is an abstract base class that should be subclassed to implement the update method.
    """

    def update(self, subject):
        """
        Update the observer based on changes in the subject.

        Parameters
        ----------
        subject : Subject
            The subject that has changed, causing the observer to need to update.
        """
        raise NotImplementedError


class Subject:
    """
    The Subject class represents a subject in the observer design pattern.
    This class maintains a list of observers and notifies them of changes.
    """

    def __init__(self):
        """
        Initialize a new Subject.

        A Subject is an object that can have observers. When the subject changes, it can notify its observers to update.
        """
        self._observers = []

    def register(self, observer):
        """
        Register a new observer to be notified of changes in the subject.

        Parameters
        ----------
        observer : Observer
            The observer to register.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer):
        """
        Unregister an observer so it will no longer be notified of changes in the subject.

        Parameters
        ----------
        observer : Observer
            The observer to unregister.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self):
        """
        Notify all registered observers that the subject has changed.
        """
        for observer in self._observers:
            observer.update(self)


class GameState(Subject):
    """
    The GameState class represents the state of a game and notifies observers of changes.
    It is a subclass of the Subject class and overrides the set_state method.
    """

    def __init__(self):
        """
        Initialize a new GameState.

        A GameState is a specific type of subject that represents the state of a game.
        """
        super().__init__()
        self.state = 'normal'
        self.parameter = None
        self.parameter_actions = []
        self.game_state_matrix = None
        self.game_state_matrix_opponent = None
        self.passed = False

    def set_state(self, new_state):
        """
        Set the state of the game and notify all observers of the change.

        Parameters
        ----------
        new_state : str
            The new state to set.
        """
        self.state = new_state
        self.notify()


class Card:
    """
    A class representing a Card in the game, complete with all relevant attributes and methods to manage the card's
    state and visual representation.

    Attributes:
    ----------
    _id : int
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
        Initializes the Card object with the given ID, data dictionary and game state.
    render(self, screen):
        Draws a rectangular border around the card.
    draw(self, screen):
        Draws the card on the screen.
    handle_event(self, event):
        Handles mouse events related to the card.
    """

    def __init__(self, _id, data, game_state):
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
        self._id = _id
        self.data = data[_id]
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
                                             self.small_image.get_height() - placement_icon.get_height()))  # bottom right corner

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
        Handles mouse events related to the card, including starting and stopping dragging,
        and updating the card's position while dragging.

        Parameters:
        ----------
        event : pygame.Event
            The event to handle.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(
                event.pos) and self.game_state.state == 'normal' and (
                self.parent_container is not None and self.parent_container.row_id == -1):
            self.game_state.parameter = self
            self.game_state.set_state('dragging')
            # If the mouse was clicked within the component, start dragging and remember the mouse offset
            self.is_dragging = True
            self.mouse_offset = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)

        elif event.type == pygame.MOUSEBUTTONUP and self.game_state.state == 'normal':
            if self.rect.collidepoint(event.pos) and self.game_state.parameter != self:
                check_valid_action(self, self.game_state.parameter, self.game_state)
        elif event.type == pygame.MOUSEBUTTONUP and self.game_state.state == 'dragging':
            self.game_state.set_state('normal')
            # If the mouse button was released, stop dragging
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            # If the mouse was moved and the component is being dragged, update the position of the component
            if self.is_dragging:
                self.rect.x = event.pos[0] - self.mouse_offset[0]
                self.rect.y = event.pos[1] - self.mouse_offset[1]


class Component(Observer):
    """
    A class that represents a Component in Pygame.

    This class serves as a base for all components that are to be rendered on the Pygame screen.
    It calculates the dimensions and position of the component based on ratios provided during instantiation.

    Attributes:
    -----------
    width : int
        The width of the component.
    height : int
        The height of the component.
    x : int
        The x-coordinate of the top left corner of the component.
    y : int
        The y-coordinate of the top left corner of the component.
    rect : pygame.Rect
        The Rect object representing the component.

    Methods:
    --------
    update(subject)
        Responds to changes in the GameState object.
    handle_event(event)
        Responds to a Pygame event.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio=0, y_ratio=0):
        """
        Initializes the Component.

        Parameters:
        -----------
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The ratio of the component's width to its parent's width.
        height_ratio : float
            The ratio of the component's height to its parent's height.
        x_ratio : float, optional
            The ratio of the component's x-coordinate to its parent's width (default is 0).
        y_ratio : float, optional
            The ratio of the component's y-coordinate to its parent's height (default is 0).
        """
        self.width = int(parent_rect.width * width_ratio)
        self.height = int(parent_rect.height * height_ratio)
        self.x = parent_rect.x + int(parent_rect.width * x_ratio)
        self.y = parent_rect.y + int(parent_rect.height * y_ratio)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.game_state = game_state
        self.game_state.register(self)

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
        Responds to changes in the GameState object. By default, this method does nothing.
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
    setup_leader_stats(y_ratio_lb, y_ratio_stats, is_opponent)
        Sets up the leader stats components.
    draw(screen)
        Draws the stats and weather components on the screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the PanelLeft.

        Parameters:
        -----------
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The ratio of the panel's width to its parent's width.
        height_ratio : float
            The ratio of the panel's height to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)

        self.weather = Weather(game_state, self, 0.549, 0.1275, 0.279, 0.416)
        self.setup_leader_stats(game_state, 0.0755, 0.2425, True)
        self.setup_leader_stats(game_state, 0.7755, 0.6175, False)

    def setup_leader_stats(self, game_state, y_ratio_lb, y_ratio_stats, is_opponent):
        """
        Sets up the leader stats components.

        Parameters:
        -----------
        y_ratio_lb : float
            The ratio of the leader box's y-coordinate to the parent's height.
        y_ratio_stats : float
            The ratio of the stats's y-coordinate to the parent's height.
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
        Draws the stats and weather components on the screen.

        Parameters:
        -----------
        screen : pygame.Surface
            The surface on which the components are to be drawn.
        """
        self.stats_op.draw(screen)
        self.weather.draw(screen)
        self.stats_me.draw(screen)


class RowScore(Component):
    """
    A class that represents a Score for a particular Row in a Pygame display.

    This class is a subclass of the Component class. It handles the displaying of
    scores in a specific area of the game interface, represented by a Pygame Rect.

    Attributes:
    ----------
    font_small : ResizableFont
        The ResizableFont used for rendering the score.
    text_color : tuple
        A tuple representing the color of the score text in RGB format.
    text_rect : pygame.Rect
        The Rect where the score will be rendered.
    text : str
        The text to be displayed, representing the score.

    Methods:
    --------
    __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the RowScore object with the given ratios relative to the parent Rect.
    set_score(self, score)
        Sets the score to be displayed.
    draw(self, screen)
        Draws the score text onto the provided screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the RowScore object with the given ratios relative to the parent Rect.

        The position and dimensions of the RowScore are determined by the ratios and the parent Rect.
        The score text is initialized as None.

        Parameters:
        -----------
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The ratio of the RowScore's width to its parent's width.
        height_ratio : float
            The ratio of the RowScore's height to its parent's height.
        x_ratio : float
            The ratio of the RowScore's x-coordinate to its parent's width.
        y_ratio : float
            The ratio of the RowScore's y-coordinate to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.font_small = ResizableFont('Arial Narrow.ttf', 24)
        self.text_color = (0, 0, 0)
        self.text_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.text = None

    def set_score(self, score):
        """
        Sets the score to be displayed.

        The score is converted to a string and fitted into the text Rect.
        The font and color used are determined by the ResizableFont and text_color attributes.

        Parameters:
        -----------
        score : int
            The score to be displayed.
        """
        self.text = fit_text_in_rect(str(score), self.font_small, self.text_color, self.text_rect)

    def draw(self, screen):
        """
        Draws the score text onto the provided screen.

        If the score text has been set, it is drawn centered in its text Rect.

        Parameters:
        -----------
        screen : pygame.Surface
            The Surface onto which the score text will be drawn.
        """
        if self.text:
            draw_centered_text(screen, self.text, self.text_rect)


class FieldRow(Component):
    """
    A class that represents a Field Row in a Pygame display.

    This class is a subclass of the Component class. It handles the rendering of a
    field row in the game interface, including the score for the row, any special
    conditions applying to the row, and the cards placed in the row.

    Attributes:
    ----------
    row_score : RowScore
        The RowScore object for this field row, representing the total score of cards in the row.
    row_special : RowSpecial
        The RowSpecial object for this field row, representing any special conditions that apply.
    row_cards : RowCards
        The RowCards object for this field row, representing the cards placed in the row.

    Methods:
    --------
    __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the FieldRow object with the given ratios relative to the parent Rect.
    draw(self, screen)
        Draws the row's score, special condition, and cards onto the provided screen.
    """

    def __init__(self, game_state, row_id, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes the FieldRow object with the given ratios relative to the parent Rect.

        Also creates a RowScore, a RowSpecial, and a RowCards for this field row.

        Parameters:
        -----------
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The ratio of the FieldRow's width to its parent's width.
        height_ratio : float
            The ratio of the FieldRow's height to its parent's height.
        x_ratio : float
            The ratio of the FieldRow's x-coordinate to its parent's width.
        y_ratio : float
            The ratio of the FieldRow's y-coordinate to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.row_id = row_id
        self.row_score = RowScore(game_state, self, 0.051, 0.4, 0.002, 0.31)
        self.row_special = RowSpecial(game_state, self, 0.1425, 1, 0.055, 0)
        self.row_cards = RowCards(self.row_id, game_state, self, 0.797, 1, 0.2, 0, is_opponent)
        self.is_opponent = is_opponent

    def draw(self, screen):
        """
        Draws the row's score, special condition, and cards onto the provided screen.

        This is accomplished by calling the draw methods of the RowScore, RowSpecial,
        and RowCards objects associated with this FieldRow.

        Parameters:
        -----------
        screen : pygame.Surface
            The Surface onto which the components will be drawn.
        """
        self.row_score.draw(screen)
        # self.row_score.render(screen)
        self.row_special.draw(screen)
        self.row_cards.draw(screen)
        # self.row_special.render(screen)
        # self.row_cards.render(screen)

    def handle_event(self, event):
        self.row_cards.handle_event(event)

    def update(self, subject):
        if subject is self.game_state and self.game_state.state == 'normal':
            if self.is_opponent:
                self.row_score.set_score(int(self.game_state.game_state_matrix[0][142 + self.row_id]))
                if self.game_state.game_state_matrix[0][136 + self.row_id] > 1:
                    self.row_special.active = True
                else:
                    self.row_special.active = False
            else:
                self.row_score.set_score(int(self.game_state.game_state_matrix[0][139 + self.row_id]))
                if self.game_state.game_state_matrix[0][133 + self.row_id] > 1:
                    self.row_special.active = True
                else:
                    self.row_special.active = False


class RowSpecial(Component):
    """
    A class that represents a special row in a Pygame display.

    This class is a subclass of the Component class. It handles the rendering of a
    special row in the game interface, including the display of a special card and
    its effects.

    Attributes:
    ----------
    card : Card
        The special Card object for this row.
    special_img : pygame.Surface
        The image of the special card, scaled to the appropriate size.
    active : bool
        A flag indicating whether the special row is active.

    Methods:
    --------
    __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the RowSpecial object with the given ratios relative to the parent Rect.
    draw(self, screen)
        Draws the special card onto the provided screen if the row is active.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the RowSpecial object with the given ratios relative to the parent Rect.

        Also creates a Card and its image for this special row.

        Parameters:
        -----------
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The ratio of the RowSpecial's width to its parent's width.
        height_ratio : float
            The ratio of the RowSpecial's height to its parent's height.
        x_ratio : float
            The ratio of the RowSpecial's x-coordinate to its parent's width.
        y_ratio : float
            The ratio of the RowSpecial's y-coordinate to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.card = Card(58, data, game_state)
        self.special_img = scale_surface(self.card.image, (self.width, self.height * 0.9))
        self.active = True
        self.allow_hovering = True

    def draw(self, screen):
        """
        Draws the special card onto the provided screen if the row is active.

        If the card is hovering, it also draws a preview of the card and its description.

        Parameters:
        -----------
        screen : pygame.Surface
            The Surface onto which the components will be drawn.
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
            hovering_image = scale_surface(hovering_image, (self.width * 1.2, self.height * 1.2))
            screen.blit(hovering_image, (img_x, img_y))
            card_preview = CardPreview(self.game_state, screen.get_rect(), self.card)
            card_preview.draw(screen)
            if self.card.ability != '0':
                card_description = CardDescription(self.game_state, screen.get_rect(), self.card)
                card_description.draw(screen)

    def update(self, subject):
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
    A class that represents a row of cards in a Pygame display.

    This class is a subclass of the Component class. It manages and renders
    a container of Card objects on the game interface.

    Attributes:
    ----------
    card_container : CardContainer
        The CardContainer object for this row.

    Methods:
    --------
    __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the RowCards object with the given ratios relative to the parent Rect.
    draw(self, screen)
        Draws the card container onto the provided screen.
    """

    def __init__(self, row_id, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes the RowCards object with the given ratios relative to the parent Rect.

        Also creates a CardContainer for this row.

        Parameters:
        ----------
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The ratio of the RowCards's width to its parent's width.
        height_ratio : float
            The ratio of the RowCards's height to its parent's height.
        x_ratio : float
            The ratio of the RowCards's x-coordinate to its parent's width.
        y_ratio : float
            The ratio of the RowCards's y-coordinate to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.row_id = row_id
        self.card_container = CardContainer(row_id, game_state, self, 1, 1, 0, 0, is_opponent)

    def draw(self, screen):
        """
        Draws the card container onto the provided screen.

        Parameters:
        ----------
        screen : pygame.Surface
            The Surface onto which the components will be drawn.
        """
        self.card_container.draw(screen)

    def handle_event(self, event):
        self.card_container.handle_event(event)


class CardPreview(Component):
    """
    A class to create a preview of a Card object in a Pygame display.

    This class is a subclass of the Component class. It manages and renders
    a preview of a specific Card object on the game interface.

    Attributes:
    ----------
    card : Card
        The Card object to be previewed.

    Methods:
    --------
    __init__(self, parent_rect, card)
        Initializes the CardPreview object with the given card and parent Rect.
    draw(self, screen)
        Draws the preview of the card onto the provided screen.
    """

    def __init__(self, game_state, parent_rect, card):
        """
        Initializes the CardPreview.

        Parameters:
        -----------
        parent_rect : pygame.Rect
            The Rect of the parent component.
        card : Card
            The Card object to be previewed.
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
    A class to create a description of a Card object in a Pygame display.

    This class is a subclass of the Component class. It manages and renders
    a description of a specific Card object on the game interface.

    Attributes:
    ----------
    card : Card
        The Card object to be described.
    image_text : str
        The string representation of the ability type of the Card object.
    ability_icon : pygame.Surface
        The icon representing the ability of the Card object.
    name_font : pygame.font.Font
        The Font object to be used to render the name of the ability.
    desc_font : pygame.font.Font
        The Font object to be used to render the description of the ability.

    Methods:
    --------
    __init__(self, parent_rect, card)
        Initializes the CardDescription object with the given card and parent Rect.
    draw(self, screen)
        Draws the description of the card onto the provided screen.
    """

    def __init__(self, game_state, parent_rect, card):
        """
        Initializes the CardDescription.

        Parameters:
        -----------
        parent_rect : pygame.Rect
            The Rect of the parent component.
        card : Card
            The Card object to be described.
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
        self.name_font = pygame.font.Font('Arial Narrow.ttf', 48)  # adjust size as necessary
        self.desc_font = pygame.font.Font('Arial Narrow.ttf', 24)  # adjust size as necessary

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
    test_card : Card
        A Card object for testing purposes.
    cards : list
        The list of Card objects to be displayed in the container.

    Methods:
    --------
    __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the CardContainer object with a specified parent Rect and ratios.
    draw(self, screen)
        Draws the Card objects in the container onto the provided screen.
    """

    def __init__(self, row_id, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes the CardContainer.

        Parameters:
        -----------
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
                    screen.blit(hovering_image, (card_x, start_y))
                    card_preview = CardPreview(self.game_state, screen.get_rect(), card)
                    card_preview.draw(screen)
                    card_strength_text(screen, card, card_x, start_y, hovering_image)
                    if card.ability != '0':
                        card_description = CardDescription(self.game_state, screen.get_rect(), card)
                        card_description.draw(screen)

    def create_card_rect(self):
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

    def update(self, subject):
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
        if event.type == pygame.MOUSEBUTTONUP and self.game_state.state == 'dragging':
            if self.rect.collidepoint(event.pos):
                self.game_state.parameter_actions.append(
                    str(self.game_state.parameter._id) + ',' + str(self.row_id) + ',-1')
                self.game_state.parameter_actions.append(
                    str(self.game_state.parameter._id) + ',' + '4' + ',-1')
        for card in self.cards:
            card.parent_container = self
            card.handle_event(event)


class Field(Component):
    """
    A class to create a Field object, a specific type of Component on a Pygame display.

    This class is a subclass of the Component class. It manages and renders FieldRow
    objects, or a CardContainer if the field represents a hand, on the game interface.

    Attributes:
    ----------
    is_hand : bool
        A flag indicating whether this field is a hand.
    field_list : list
        The list of FieldRow objects or CardContainer object to be displayed in the field.

    Methods:
    --------
    __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent, is_hand)
        Initializes the Field object with a specified parent Rect, ratios and flags.
    draw(self, screen)
        Draws the FieldRows or CardContainer in the field onto the provided screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent, is_hand):
        """
        Initializes the Field.

        Parameters:
        -----------
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
            A flag indicating whether this field belongs to an opponent.
        is_hand : bool
            A flag indicating whether this field is a hand.
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
                self.field_row_siege = FieldRow(game_state, 2, self, 1, 0.32, 0, 0.021, is_opponent)
                self.field_row_ranged = FieldRow(game_state, 1, self, 1, 0.32, 0, 0.335, is_opponent)
                self.field_row_melee = FieldRow(game_state, 0, self, 1, 0.32, 0, 0.67, is_opponent)
                self.field_list.append(self.field_row_ranged)
                self.field_list.append(self.field_row_siege)
                self.field_list.append(self.field_row_melee)
            else:
                self.field_row_melee = FieldRow(game_state, 0, self, 1, 0.32, 0, 0.021, is_opponent)
                self.field_row_ranged = FieldRow(game_state, 1, self, 1, 0.32, 0, 0.335, is_opponent)
                self.field_row_siege = FieldRow(game_state, 2, self, 1, 0.32, 0, 0.67, is_opponent)
                self.field_list.append(self.field_row_melee)
                self.field_list.append(self.field_row_ranged)
                self.field_list.append(self.field_row_siege)

    def draw(self, screen):
        """
        Draws the FieldRows or CardContainer in the field on the screen.

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
        if self.game_state.state == 'normal':
            if self.is_hand:
                self.field_list[0].handle_event(event)
        if self.game_state.state != 'carousel':
            for fieldRow in self.field_list:
                if event.type == pygame.MOUSEBUTTONUP and fieldRow.rect.collidepoint(event.pos):
                    if self.game_state.parameter is not None and self.game_state.parameter.ability == 'Medic':
                        self.game_state.parameter_actions.append(
                            str(self.game_state.parameter._id) + ',' + str(fieldRow.row_id) + ',' + '-1')
                        self.game_state.parameter = None
                        self.game_state.set_state('carousel')
                    else:
                        fieldRow.handle_event(event)


class PanelMiddle(Component):
    """
    A class to create a PanelMiddle object, a specific type of Component on a Pygame display.

    This class is a subclass of the Component class. It manages and renders three
    different Field objects: the opponent's field, the player's field, and the hand field
    on the game interface.

    Attributes:
    ----------
    field_list : list
        The list of Field objects (field_op, field_me, field_hand) to be displayed
        in the middle panel.

    Methods:
    --------
    __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        Initializes the PanelMiddle object with a specified parent Rect and ratios.
    draw(self, screen)
        Draws the Fields in the middle panel onto the provided screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the PanelMiddle.

        Parameters:
        -----------
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
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.field_list = []
        self.field_op = Field(game_state, self, 1, 0.385, 0, 0, True, False)
        self.field_me = Field(game_state, self, 1, 0.385, 0, 0.388, False, False)
        self.field_hand = Field(game_state, self, 0.938, 0.13, 0.062, 0.775, False, True)
        self.field_list.append(self.field_op)
        self.field_list.append(self.field_me)
        self.field_list.append(self.field_hand)

    def draw(self, screen):
        """
        Draws the Fields in the middle panel on the screen.

        Parameters:
        -----------
        screen : pygame.Surface
            The surface on which the Fields are to be drawn.
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
        if self.game_state.state != 'carousel':
            for field in self.field_list:
                field.handle_event(event)


class PanelRight(Component):
    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
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
        for component in self.component_list:
            component.draw(screen)

    def handle_event(self, event):
        for component in self.component_list:
            component.handle_event(event)


class PanelGame(Component):
    """
    This class represents a game panel which contains the left, middle, and right panels.

    Attributes
    ----------
    parent_rect : pygame.Rect
        The rectangle representing the area of the parent screen.
    panel_left : PanelLeft
        The left panel of the game.
    panel_middle : PanelMiddle
        The middle panel of the game.
    panel_right : PanelRight
        The right panel of the game.
    """

    def __init__(self, game_state, parent_rect):
        """
        Initializes a new instance of PanelGame.

        Parameters
        ----------
        parent_rect : pygame.Rect
            The rectangle representing the area of the parent screen.
        """
        super().__init__(game_state, parent_rect, 1, 1, 0, 0)
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
        Draws the panels on the screen.

        Parameters
        ----------
        screen : pygame.Surface
            The surface onto which the panels should be drawn.
        """
        # Get the mouse cursor position
        mouse_pos = pygame.mouse.get_pos()
        for panel in self.panel_list:
            if not panel.rect.collidepoint(mouse_pos):
                panel.draw(screen)
        for panel in self.panel_list:
            if panel.rect.collidepoint(mouse_pos):
                panel.draw(screen)
            if self.game_state.state == 'dragging':
                self.game_state.parameter.draw(screen)
        if self.carousal_active:
            if self.game_state.parameter is None:
                self.panel_carousel.cards = self.panel_right.grave_me.cards
            else:
                self.panel_carousel.cards = self.game_state.parameter
            self.panel_carousel.draw(screen)

    def handle_event(self, event):
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
        if subject is self.game_state and self.game_state.state == 'carousel':
            # The game has entered the 'carousel' state, so disable card hovering.
            self.carousal_active = True
        elif subject is self.game_state and self.game_state.state == 'normal':
            # The game has returned to the 'normal' state, so enable card hovering.
            self.carousal_active = False


class LeaderBox(Component):
    """
    A class that represents a LeaderBox, a UI component in Pygame.

    This class is a subclass of the Component class and represents a graphical
    component that usually contains an image or text representing a "leader"
    in a game.

    Methods:
    --------
    No additional methods are implemented in this subclass.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the LeaderBox.

        Parameters:
        -----------
        parent_rect : pygame.Rect
            The rectangle object that represents the parent component's area.
        width_ratio : float
            The ratio of the LeaderBox's width to its parent's width. It determines the width of the LeaderBox.
        height_ratio : float
            The ratio of the LeaderBox's height to its parent's height. It determines the height of the LeaderBox.
        x_ratio : float
            The ratio of the LeaderBox's x-coordinate (left edge) to its parent's width. It determines the horizontal position of the LeaderBox within the parent.
        y_ratio : float
            The ratio of the LeaderBox's y-coordinate (top edge) to its parent's height. It determines the vertical position of the LeaderBox within the parent.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)


class LeaderContainer(Component):
    """
    A class that represents a LeaderContainer, a specific UI component in Pygame.

    This class is a subclass of the Component class and is used to contain a
    "leader" representation, usually an image or text. It is designed to be always
    centered within its parent component, typically a LeaderBox.

    Methods:
    --------
    No additional methods are implemented in this subclass.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio):
        """
        Initializes the LeaderContainer.

        The LeaderContainer is always centered within its parent component, which is
        typically a LeaderBox.

        After initialization, the LeaderContainer's x and y coordinates are updated to
        ensure it's centered within the parent component. Consequently, its 'rect' attribute
        is updated to reflect the new position.

        Parameters:
        -----------
        parent_rect : pygame.Rect
            The rectangle object that represents the parent component's area.
        width_ratio : float
            The ratio of the LeaderContainer's width to its parent's width. Determines the width of the LeaderContainer.
        height_ratio : float
            The ratio of the LeaderContainer's height to its parent's height. Determines the height of the LeaderContainer.
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

    Methods:
    --------
    No additional methods are implemented in this subclass.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes the LeaderActive.

        The LeaderActive is positioned within its parent component, which is typically a LeaderBox.

        Parameters:
        -----------
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The ratio of the LeaderActive's width to its parent's width.
        height_ratio : float
            The ratio of the LeaderActive's height to its parent's height.
        x_ratio : float
            The ratio of the LeaderActive's x position to its parent's width.
        y_ratio : float
            The ratio of the LeaderActive's y position to its parent's height.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)  # 24% of the leader_box width, 28% of the leader_box height, positioned within the leader_box


class Stats(Component):
    """
    A class that represents Stats, a specific UI component in Pygame.

    This class is a subclass of the Component class and is used to display various statistical information
    about the game state, such as player names, deck names, hand count, and total score.

    Methods
    --------
    create_profile_image(is_opponent: bool) -> ProfileImage:
        Creates and returns a ProfileImage instance for the current Stats instance.
    create_name(is_opponent: bool) -> PlayerName:
        Creates and returns a PlayerName instance for the current Stats instance.
    create_deck_name(deck_name: str, is_opponent: bool) -> DeckName:
        Creates and returns a DeckName instance for the current Stats instance.
    create_hand_count(is_opponent: bool) -> HandCount:
        Creates and returns a HandCount instance for the current Stats instance.
    create_gem(x_ratio: float, is_opponent: bool) -> Gem:
        Creates and returns a Gem instance for the current Stats instance.
    create_score_total(is_opponent: bool) -> ScoreTotal:
        Creates and returns a ScoreTotal instance for the current Stats instance.
    draw(screen: pygame.Surface):
        Draws the stats on the provided pygame.Surface.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes the Stats component.

        Parameters:
        -----------
        parent_rect : pygame.Rect
            The Rect of the parent component.
        width_ratio : float
            The ratio of the Stats's width to its parent's width.
        height_ratio : float
            The ratio of the Stats's height to its parent's height.
        x_ratio : float
            The ratio of the Stats's x position to its parent's width.
        y_ratio : float
            The ratio of the Stats's y position to its parent's height.
        is_opponent : bool
            A flag that represents whether the Stats are for the opponent or the player.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.font_small = ResizableFont('Arial Narrow.ttf', 24)
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
        return DeckName(self.game_state, self, 0.47, 0.125, 0.53, y_ratio, deck_name)

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
        return HandCount(self.game_state, self, 0.17, 0.295, 0.5325, y_ratio)

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
        Draws all of the elements of the stats instance onto the provided Pygame surface.

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
    This class represents a player's profile image in a game.

    Attributes
    ----------
    opponent : bool
        Flag indicating if the profile image belongs to the opponent.
    profile_img_pic : pygame.Surface
        Surface containing the player's profile image.
    background_image : pygame.Surface
        Surface containing the background image of the profile.
    faction_img_pic : pygame.Surface
        Surface containing the faction image of the player.

    Methods
    -------
    draw(screen: pygame.Surface)
        Draw the profile image, its background, and the faction image onto the given screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, faction, opponent):
        """
        Initializes a new instance of ProfileImage.

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
        faction : str
            Faction to which the player belongs.
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

        Parameters
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
    This class represents a player's name displayed on the game screen.

    Attributes
    ----------
    font_size : int
        The font size for rendering the player's name.
    font : pygame.font.Font
        The font to be used for rendering the player's name.
    text : pygame.Surface
        Surface containing the rendered player's name.

    Methods
    -------
    draw(screen: pygame.Surface)
        Draw the player's name onto the given screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes a new instance of PlayerName.

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
        is_opponent : bool
            Flag indicating whether this name is for the opponent.
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
        Draws the player's name onto the given screen.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the name should be drawn.
        """
        screen.blit(self.text, (self.x, self.y))


class DeckName(Component):
    """
    This class represents a deck's name displayed on the game screen.

    Attributes
    ----------
    font_size : int
        The font size for rendering the deck's name.
    font : pygame.font.Font
        The font to be used for rendering the deck's name.
    text : pygame.Surface
        Surface containing the rendered deck's name.

    Methods
    -------
    draw(screen: pygame.Surface)
        Draw the deck's name onto the given screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, deck_name):
        """
        Initializes a new instance of DeckName.

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
        deck_name : str
            The name of the deck.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)
        self.font_size = int(parent_rect.height * height_ratio)  # 16% of the stats_op height
        self.font = ResizableFont('Arial Narrow.ttf', self.font_size)
        self.text = self.font.font.render(deck_name, True, (210, 180, 140))  # RGB for tan color

    def draw(self, screen):
        """
        Draws the deck's name onto the given screen.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the name should be drawn.
        """
        screen.blit(self.text, (self.x, self.y))


class Gem(Component):
    """
    This class represents a Gem component which is a part of the game screen.

    Attributes
    ----------
    gem_on_image : pygame.Surface
        Surface containing the image of the gem in its "on" state.
    gem_on_image_off : pygame.Surface
        Surface containing the image of the gem in its "off" state.
    gem_on_image_on : pygame.Surface
        Surface containing the image of the gem in its "on" state.

    Methods
    -------
    draw(screen: pygame.Surface)
        Draw the gem onto the given screen.
    change_gem(on: bool)
        Change the state of the gem.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes a new instance of Gem.

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
        self.gem_on_image = pygame.image.load('img/icons/icon_gem_on.png')
        self.gem_on_image = pygame.transform.scale(self.gem_on_image, (self.width, self.height))
        self.gem_on_image_off = pygame.image.load('img/icons/icon_gem_off.png')
        self.gem_on_image_off = pygame.transform.scale(self.gem_on_image_off, (self.width, self.height))
        self.gem_on_image_on = pygame.image.load('img/icons/icon_gem_on.png')
        self.gem_on_image_on = pygame.transform.scale(self.gem_on_image, (self.width, self.height))
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
    This class represents a HandCount component, which displays the number of cards in a player's hand.

    Attributes
    ----------
    font_small : ResizableFont
        The font to use for the hand count text.
    hand_count_image : pygame.Surface
        Surface containing the image of the hand count icon.
    hand_count_op_text_rect : pygame.Rect
        Rectangle specifying the area in which the hand count text should be displayed.
    hand_count_op_text : pygame.Surface
        Surface containing the hand count text.

    Methods
    -------
    draw(screen: pygame.Surface)
        Draw the hand count icon and text onto the given screen.
    change_count(count: int)
        Change the hand count displayed.
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
        self.font_small = ResizableFont('Arial Narrow.ttf', 24)
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
    This class represents a ScoreTotal component, which displays the total score of a player.

    Attributes
    ----------
    is_opponent : bool
        Indicates whether this score total is for the opponent.
    image : pygame.Surface
        Surface containing the image of the score total icon.
    font_small : ResizableFont
        The font to use for the score total text.
    text_color : tuple
        RGB tuple representing the color of the score total text.
    text_rect : pygame.Rect
        Rectangle specifying the area in which the score total text should be displayed.
    text : pygame.Surface
        Surface containing the score total text.
    high_score_image : pygame.Surface
        Surface containing the image of the high score icon.
    high_score_rect : pygame.Rect
        Rectangle specifying the area in which the high score icon should be displayed.
    high : bool
        Indicates whether this score total is the high score.

    Methods
    -------
    set_score(score: int, high: bool)
        Set the score displayed and whether it is the high score.
    draw(screen: pygame.Surface)
        Draw the score total icon and text, and the high score icon if this score is the high score, onto the given screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes a new instance of ScoreTotal.

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

        self.font_small = ResizableFont('Arial Narrow.ttf', 24)
        self.text_color = (0, 0, 0)
        self.text_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.text = None
        self.high_score_image = pygame.image.load('img/icons/icon_high_score.png')
        self.high_score_image = pygame.transform.scale(self.high_score_image,
                                                       (int(self.width * 1.95), int(self.height * 1.7)))
        self.high_score_rect = self.high_score_image.get_rect(
            topleft=(self.x + int(self.width * -0.46), self.y + int(self.height * -0.32)))
        self.high = False

    def set_score(self, score, high):
        """
        Sets the score displayed and whether it is the high score.

        Parameters
        ----------
        score : int
            The score to be displayed.
        high : bool
            Indicates whether this score is the high score.
        """
        self.text = fit_text_in_rect(str(score), self.font_small, self.text_color, self.text_rect)
        self.high = high

    def draw(self, screen):
        """
        Draws the score total icon and text, and the high score icon if this score is the high score, onto the given screen.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the score total and high score should be drawn.
        """
        screen.blit(self.image, (self.x, self.y))
        if self.high:
            screen.blit(self.high_score_image, self.high_score_rect)
        if self.text:
            draw_centered_text(screen, self.text, self.text_rect)


class Passed(Component):
    """
    This class represents a Passed component, which displays the text 'Passed' on the screen.

    Attributes
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
                         y_ratio)  # 0% height, 0% width, positioned at 90% of the parent width, 87% of the parent height
        self.font_size = int(parent_rect.height * height_ratio)  # 16% of the stats_op height
        self.font = ResizableFont('Arial Narrow.ttf', self.font_size)
        self.passed_bool = False
        self.text = self.font.font.render('Passed', True, (210, 180, 140))  # RGB white color

    def draw(self, screen):
        """
        Draws the 'Passed' text onto the given screen.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the 'Passed' text should be drawn.
        """
        if self.passed_bool:
            screen.blit(self.text, (self.x, self.y))


class Weather(Component):
    """
    This class represents a Weather component, which displays images of various weather conditions on the screen.

    Attributes
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
        The list of cards to be displayed, representing current weather conditions.

    Methods
    -------
    add_weather(weather_type: str)
        Adds a new weather type to be displayed.
    draw(screen: pygame.Surface)
        Draws the weather images onto the given screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        """
        Initializes a new instance of Weather.

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
                         y_ratio)  # 54.9% of the parent width, 12.75% of the parent height, positioned at 27.9% of the parent width, 41.25% of the parent height
        self.cards = []
        self.frost = Card(60, data, game_state)
        self.fog = Card(61, data, game_state)
        self.rain = Card(62, data, game_state)
        self.clear = Card(63, data, game_state)
        self.allow_hovering = True

    def draw(self, screen):
        """
        Draws the weather images onto the given screen.

        If there are no images to display, the method does nothing.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the weather images should be drawn.
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
                    screen.blit(hovering_image, (card_x, start_y))
                    card_preview = CardPreview(self.game_state, screen.get_rect(), card)
                    card_preview.draw(screen)
                    if card.ability != '0':
                        card_description = CardDescription(self.game_state, screen.get_rect(), card)
                        card_description.draw(screen)

    def update(self, subject):
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


class Grave(Component):
    """
    This class represents a Grave component, which stores discarded or destroyed game cards.

    Attributes
    ----------
    cards : list
        The list of discarded or destroyed game cards.

    Methods
    -------
    add_card(card: Card)
        Adds a card to the Grave.
    draw(screen: pygame.Surface)
        Draws the Grave onto the given screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        """
        Initializes a new instance of Grave.

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
        self.cards = []
        self.is_opponent = is_opponent

    def draw(self, screen):
        """
        Draws the Grave onto the given screen.

        Each card after the first one will be placed one pixel to the left and to the top from the previous card to create an effect that they are on top of each other. The first card will be centered in the middle with both width and height.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the Grave should be drawn.
        """
        if len(self.cards) > 0:
            for i, card in enumerate(self.cards):
                card_image = scale_surface(card.image, (self.width * 0.9, self.height * 0.9))
                x_position = self.x - i + (self.width - card_image.get_width()) // 2
                y_position = self.y - i + (self.height - card_image.get_height()) // 2

                # Ensuring the card does not go beyond the container's dimensions
                x_position = max(x_position, 0)
                y_position = max(y_position, 0)

                screen.blit(card_image, (x_position, y_position))
                if i == len(self.cards) - 1:
                    card_strength_text(screen, card, x_position, y_position, card_image)

    def handle_event(self, event):
        # Get the mouse cursor position
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
            self.game_state.set_state('carousel')
            self.game_state.parameter = self.cards

    def update(self, subject):
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
    This class represents a Deck component, which displays the deck of cards.

    Attributes
    ----------
    deck_back_image : pygame.Surface
        The back image of the deck of cards to be displayed.

    Methods
    -------
    draw(screen: pygame.Surface)
        Draws the deck of cards onto the given screen.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, deck, is_opponent):
        """
        Initializes a new instance of Deck.

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
        deck : str
            The deck type, used to determine the back image of the deck.
        """
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.cards = []
        self.is_opponent = is_opponent
        self.deck_back_image = pygame.image.load(f'img/icons/deck_back_{deck}.jpg')
        self.deck_back_image = scale_surface(self.deck_back_image, (self.width, self.height))

    def draw(self, screen):
        """
        Draws the deck of cards onto the given screen.

        If there are no cards to display, the method does nothing.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the deck of cards should be drawn.
        """
        if not self.cards:
            return

        card = self.cards[-1]
        card_image_scaled = self.deck_back_image
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2

        if len(self.cards) > 0:
            for i, card in enumerate(self.cards):
                card_image = scale_surface(card.image, (self.width * 0.9, self.height * 0.9))
                x_position = self.x - i + (self.width - card_image.get_width()) // 2
                y_position = self.y - i + (self.height - card_image.get_height()) // 2
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
        font = ResizableFont('Arial Narrow.ttf', 20)
        text_color = (255, 255, 255)
        text = font.font.render(str(len(self.cards)), True, text_color)
        draw_centered_text(screen, text, card_count_rect)

    def handle_event(self, event):
        # Get the mouse cursor position
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos) and not self.is_opponent:
            self.game_state.set_state('carousel')
            self.game_state.parameter = self.cards

    def update(self, subject):
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
    A carousel of card images.

    Attributes
    ----------
    cards: list of Card
        The list of cards to be displayed.

    Methods
    -------
    draw(screen)
        Draws the carousel on the screen.
    next_card()
        Moves to the next card in the carousel.
    previous_card()
        Moves to the previous card in the carousel.
    """

    def __init__(self, game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        super().__init__(game_state, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio)
        self.cards = []
        self.current_index = 0

    def draw(self, screen):
        """
        Draws the carousel on the screen, with the current card at the center and the other cards off to the sides.

        Parameters
        ----------
        screen : pygame.Surface
            The screen onto which the carousel should be drawn.
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
        Moves to the next card in the carousel.
        """
        if self.current_index < len(self.cards) - 1:
            self.current_index += 1

    def previous_card(self):
        """
        Moves to the previous card in the carousel.
        """
        if self.current_index > 0:
            self.current_index -= 1

    def handle_event(self, event):
        """
        Handles the given event.

        Parameters
        ----------
        event : pygame.event.Event
            The event to handle.
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
                new_action += ',' + str(self.cards[self.current_index]._id)
                self.game_state.parameter_actions.append(new_action)
                self.game_state.set_state('normal')


class ResizableFont:
    """
    This class represents a resizable font for pygame rendering.

    Attributes
    ----------
    path : str
        The file path to the font file.
    size : int
        The size of the font.
    font : pygame.font.Font
        The Pygame font object.

    Methods
    -------
    resize(new_size: int)
        Resizes the font to the new specified size.
    """

    def __init__(self, path, size):
        """
        Initializes a new instance of ResizableFont.

        Parameters
        ----------
        path : str
            The file path to the font file.
        size : int
            The size of the font.
        """
        self.path = path
        self.size = size
        self.font = pygame.font.Font(self.path, self.size)

    def resize(self, new_size):
        """
        Resizes the font to the new specified size.

        Parameters
        ----------
        new_size : int
            The new size for the font.
        """
        self.size = new_size
        self.font = pygame.font.Font(self.path, self.size)


class GameGui:
    def __init__(self, fps=60):
        pygame.init()
        infoObject = pygame.display.Info()
        self.width = infoObject.current_w
        self.height = infoObject.current_h
        self.fps = fps
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True
        cards = load_file_game('Gwent.csv')
        self.game = Game(cards)
        self.game_state = GameState()
        self.game_state.game_state_matrix = self.game.game_state()
        self.game_state.game_state_matrix = self.game.game_state_matrix.state_matrix_0
        self.game_state.game_state_matrix_opponent = self.game.game_state_matrix.state_matrix_1
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


class MyGameGui(GameGui):
    def __init__(self):
        super().__init__()
        self.font_small = ResizableFont('Arial Narrow.ttf', 24)
        # Load the background image
        self.background_image = pygame.image.load('img/board.jpg')  # Replace with your image path
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.width, self.height))  # Scale the image to fit the screen
        self.panel_game = PanelGame(self.game_state, self.screen.get_rect())
        self.game_state.set_state('normal')

    def run(self):
        while self.running:
            self.clock.tick(self.fps)
            start_time = time.time()
            self.handle_events()
            end_time = time.time()
            self.timing_data["handle_events"].append(end_time - start_time)

            start_time = time.time()
            self.update()
            end_time = time.time()
            self.timing_data["update"].append(end_time - start_time)

            start_time = time.time()
            self.draw()
            end_time = time.time()
            self.timing_data["draw"].append(end_time - start_time)
        self.print_average_times()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.game_state.state == 'normal':
                    self.running = False
                elif event.key == pygame.K_SPACE and self.game_state.state == 'normal':
                    self.game_state.parameter_actions.append('-1')
                    self.game_state.passed = True

            self.panel_game.handle_event(event)

    def update(self):
        need_to_refresh = False
        if len(self.game_state.parameter_actions) > 0 and self.game_state.state == 'normal':
            start_time = time.time()
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
                print('Player action: ' + action_a)
                start_time_step = time.time()
                result = self.game.step(action)
                end_time_step = time.time()
                self.timing_data["step call"].append(end_time_step - start_time_step)

                need_to_refresh = True

                if result > 3:
                    self.running = False

            end_time = time.time()
            self.timing_data["update action"].append(end_time - start_time)

        if self.game.turn == 1:
            start_time = time.time()

            start_time_step = time.time()
            self.step_by_ai()
            need_to_refresh = True
            end_time_step = time.time()
            self.timing_data["step call"].append(end_time_step - start_time_step)

            end_time = time.time()
            self.timing_data["update action"].append(end_time - start_time)

        if need_to_refresh:
            start_time_set_state = time.time()
            self.game_state.set_state('normal')
            end_time_set_state = time.time()
            self.timing_data["set_state call"].append(end_time_set_state - start_time_set_state)

    def step_by_ai(self):
        bool_actions, actions = self.game.valid_actions()
        index = random.randrange(len(actions))
        print('AI action:' + str(actions[index]))
        result = self.game.step(self.game.get_index_of_action(actions[index]))
        if result > 3:
            self.running = False

    def draw(self):
        start_time = time.time()
        self.screen.blit(self.background_image, (0, 0))
        end_time = time.time()
        self.timing_data["screen_blit"].append(end_time - start_time)

        start_time = time.time()
        self.panel_game.draw(self.screen)
        end_time = time.time()
        self.timing_data["panel_game_draw"].append(end_time - start_time)

        start_time = time.time()
        pygame.display.flip()
        end_time = time.time()
        self.timing_data["pygame_display_flip"].append(end_time - start_time)

    def print_average_times(self):
        for function, times in self.timing_data.items():
            if times:
                average_time = sum(times) / len(times)
                max_time = max(times)
                print(f"Average time for {function}: {average_time:.6f} seconds, Maximum time: {max_time:.6f} seconds")
            else:
                print(f"No timing data for {function}")


if __name__ == '__main__':
    game = MyGameGui()
    game.run()
