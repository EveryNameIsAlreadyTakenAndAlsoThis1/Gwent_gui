import pygame


class Component:
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio=0, y_ratio=0):
        self.width = int(parent_rect.width * width_ratio)
        self.height = int(parent_rect.height * height_ratio)
        self.x = parent_rect.x + int(parent_rect.width * x_ratio)
        self.y = parent_rect.y + int(parent_rect.height * y_ratio)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


class Panel(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio):
        super().__init__(parent_rect, width_ratio, height_ratio)  # 26.5% of the window width, Full height

        # Create the leader box
        self.leader_box_op = LeaderBox(self.rect, 0.314, 0.125, 0.275,
                                       0.0755)

        # Create the leader container
        self.leader_container_op = LeaderContainer(self.rect, 0.63, 1)

        # Create the leader active
        self.leader_active_op = LeaderActive(self.rect, 0.24, 0.28, 0.75,
                                             0.33)

        # Create the stats_op component
        self.stats_op = Stats(self.rect, 0.89, 0.125, 0,
                              0.2425,
                              True)  # 89% of the panel_left width, 12.5% of the panel_left height, positioned within the panel_left

        self.weather = Weather(self, 0.549, 0.1275, 0.279,
                               0.416)
        self.weather.add_weather('rain')
        # self.weather.add_weather('fog')
        self.weather.add_weather('frost')

        self.stats_me = Stats(self.rect, 0.89, 0.125, 0,
                              0.6175, False)
        # Create the leader box
        self.leader_box_me = LeaderBox(self.rect, 0.314, 0.125, 0.275,
                                       0.7755)

        # Create the leader container
        self.leader_container_me = LeaderContainer(self.rect, 0.63, 1)

        # Create the leader active
        self.leader_active_me = LeaderActive(self.rect, 0.24, 0.28, 0.75,
                                             0.33)

    def draw(self, screen):
        self.stats_op.draw(screen)
        self.weather.draw(screen)
        self.stats_me.draw(screen)


class LeaderBox(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        super().__init__(parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)  # 31.4% of the panel width, 12.5% of the panel height, 27.5% from the left edge of the panel, 7.55% from the top of the panel


class LeaderContainer(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio):
        super().__init__(parent_rect, width_ratio,
                         height_ratio)  # 63% of the leader_box width, 100% of the leader_box height
        self.x = parent_rect.x + (
                parent_rect.width - self.width) // 2  # The leader_container is centered within the leader_box
        self.y = parent_rect.y + (
                parent_rect.height - self.height) // 2  # The leader_container is centered within the leader_box
        self.rect = pygame.Rect(self.x, self.y, self.width,
                                self.height)  # Update the rect with the new x, y coordinates


class LeaderActive(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        super().__init__(parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)  # 24% of the leader_box width, 28% of the leader_box height, positioned within the leader_box


class Stats(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        super().__init__(parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)
        self.font_small = ResizableFont('Arial Narrow.ttf', 24)
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((20, 20, 20))
        self.surface.set_alpha(128)

        if is_opponent:
            self.profile_image = ProfileImage(self, 0.219, 0.8, 0.284,
                                              0.096,
                                              'monsters',
                                              True)  # 21.9% of the stats_op width, 80% of the stats_op height, positioned within the stats_op
            self.name = PlayerName(self, 0.47, 0.2, 0.53,
                                   0,
                                   True)  # 47% of the stats_op width, 20% of the stats_op height, positioned within the stats_op 53%
            self.deck_name = DeckName(self, 0.47, 0.125, 0.53,
                                      0.25,
                                      "Monsters")  # 47% of the stats_op width, 8% of the stats_op height, positioned within the stats_op
            self.hand_count = HandCount(self, 0.17, 0.295, 0.5325,
                                        0.585)  # 17% of the stats_op width, 29.5% of the stats_op height, positioned within the stats_op
            self.gem1 = Gem(self, 0.09, 0.31, 0.8,
                            0.56)  # 9% of the panel_left's width, 31% of the stats_op height, positioned within the stats_op
            self.gem2 = Gem(self, 0.09, 0.31, 0.7075,
                            0.5625)  # 9% of the panel_left's width, 31% of the stats_op height, positioned within the stats_op

            self.score_total = ScoreTotal(self, 0.12, 0.4, 0.94, 0.32, True)
            self.score_total.set_score(10, True)
            self.passed = Passed(self, 0.25, 0.25, 0.9, 0.87)
        else:
            self.profile_image = ProfileImage(self, 0.219, 0.8, 0.284,
                                              0.096,
                                              'monsters',
                                              False)  # 21.9% of the stats_op width, 80% of the stats_op height, positioned within the stats_op
            self.name = PlayerName(self, 0.47, 0.2, 0.53,
                                   0.56,
                                   False)  # 47% of the stats_op width, 20% of the stats_op height, positioned within the stats_op 53%
            self.deck_name = DeckName(self, 0.47, 0.125, 0.53,
                                      0.80,
                                      "Monsters")  # 47% of the stats_op width, 8% of the stats_op height, positioned within the stats_op
            self.hand_count = HandCount(self, 0.17, 0.295, 0.5325,
                                        0.185)  # 17% of the stats_op width, 29.5% of the stats_op height, positioned within the stats_op
            self.gem1 = Gem(self, 0.09, 0.31, 0.8,
                            0.145)  # 9% of the panel_left's width, 31% of the stats_op height, positioned within the stats_op
            self.gem2 = Gem(self, 0.09, 0.31, 0.7075,
                            0.145)  # 9% of the panel_left's width, 31% of the stats_op height, positioned within the stats_op

            self.score_total = ScoreTotal(self, 0.12, 0.4, 0.944, 0.31, False)
            self.score_total.set_score(10, True)
            self.passed = Passed(self, 0.25, 0.25, 0.9, 0.87)

    def draw(self, screen):
        screen.blit(self.surface, (self.x, self.y))
        self.profile_image.draw(screen)
        # self.profile_image.render(screen)
        self.name.draw(screen)
        # self.opponent_name.render(screen)
        self.deck_name.draw(screen)
        # self.deck_name_op.render(screen)
        self.hand_count.draw(screen)
        # self.hand_count_op.render(screen)
        self.gem1.draw(screen)
        self.gem2.draw(screen)
        self.score_total.draw(screen)
        self.passed.draw(screen)
        # self.passed_op.render(screen)


class ProfileImage(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, faction, opponent):
        super().__init__(
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
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        super().__init__(
            parent_rect, width_ratio, height_ratio, x_ratio,
            y_ratio)
        self.font_size = int(parent_rect.height * height_ratio)  # 20% of the stats_op height
        self.font = ResizableFont('Arial Narrow.ttf', self.font_size)
        if is_opponent:
            self.text = self.font.font.render('Opponent', True, (218, 165, 32))  # RGB white color
        else:
            self.text = self.font.font.render('Player', True, (218, 165, 32))  # RGB white color

    def draw(self, screen):
        screen.blit(self.text, (self.x, self.y))


class DeckName(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, deck_name):
        super().__init__(parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)
        self.font_size = int(parent_rect.height * height_ratio)  # 16% of the stats_op height
        self.font = ResizableFont('Arial Narrow.ttf', self.font_size)
        self.text = self.font.font.render(deck_name, True, (210, 180, 140))  # RGB for tan color

    def draw(self, screen):
        screen.blit(self.text, (self.x, self.y))


class Gem(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        super().__init__(parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)
        self.gem_on_image = pygame.image.load('img/icons/icon_gem_on.png')
        self.gem_on_image = pygame.transform.scale(self.gem_on_image, (self.width, self.height))

    def draw(self, screen):
        screen.blit(self.gem_on_image, (self.x, self.y))

    def change_gem(self, on):
        if on:
            self.gem_on_image = pygame.image.load('img/icons/icon_gem_on.png')
            self.gem_on_image = pygame.transform.scale(self.gem_on_image, (self.width, self.height))
        else:
            self.gem_on_image = pygame.image.load('img/icons/icon_gem_off.png')
            self.gem_on_image = pygame.transform.scale(self.gem_on_image, (self.width, self.height))


class HandCount(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        super().__init__(parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)
        self.font_small = ResizableFont('Arial Narrow.ttf', 24)
        self.hand_count_image = pygame.image.load('img/icons/icon_card_count.png')
        self.hand_count_image = scale_surface(self.hand_count_image, (self.width, self.height))
        self.hand_count_op_text_rect = pygame.Rect(self.x + self.hand_count_image.get_width(), self.y,
                                                   self.width - self.hand_count_image.get_width(), self.height)
        self.hand_count_op_text = fit_text_in_rect("10", self.font_small, (218, 165, 32),
                                                   self.hand_count_op_text_rect)

    def draw(self, screen):
        screen.blit(self.hand_count_image, (self.x, self.y))
        draw_centered_text(screen, self.hand_count_op_text, self.hand_count_op_text_rect)

    def change_count(self, count):
        self.hand_count_op_text = fit_text_in_rect(str(count), self.font_small, (218, 165, 32),
                                                   self.hand_count_op_text_rect)


class ScoreTotal(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio, is_opponent):
        super().__init__(parent_rect, width_ratio, height_ratio, x_ratio,
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
        self.text = fit_text_in_rect(str(score), self.font_small, self.text_color, self.text_rect)
        self.high = high

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        if self.high:
            screen.blit(self.high_score_image, self.high_score_rect)
        if self.text:
            draw_centered_text(screen, self.text, self.text_rect)


class Passed(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        super().__init__(parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)  # 0% height, 0% width, positioned at 90% of the parent width, 87% of the parent height
        self.font_size = int(parent_rect.height * height_ratio)  # 16% of the stats_op height
        self.font = ResizableFont('Arial Narrow.ttf', self.font_size)
        self.text = self.font.font.render('Passed', True, (210, 180, 140))  # RGB white color

    def draw(self, screen):
        screen.blit(self.text, (self.x, self.y))


class Weather(Component):
    def __init__(self, parent_rect, width_ratio, height_ratio, x_ratio, y_ratio):
        super().__init__(parent_rect, width_ratio, height_ratio, x_ratio,
                         y_ratio)  # 54.9% of the parent width, 12.75% of the parent height, positioned at 27.9% of the parent width, 41.25% of the parent height
        self.weather_images = []

    def add_weather(self, weather_type):
        weather_image = pygame.image.load(f'img/sm/weather_{weather_type}.jpg')
        scaled_image = scale_surface(weather_image, (self.width, self.height))
        self.weather_images.append(scaled_image)

    def draw(self, screen):
        total_images = len(self.weather_images)

        if total_images == 0:
            return  # nothing to draw

        total_width = sum(image.get_width() for image in self.weather_images)
        x_offset = (self.width - total_width) / 2

        current_x = self.x + x_offset

        for weather_image in self.weather_images:
            image_width, image_height = weather_image.get_size()
            image_y = self.y + (self.height - image_height) / 2
            screen.blit(weather_image, (current_x, image_y))
            current_x += image_width  # advance to the next image start position


class ResizableFont:
    def __init__(self, path, size):
        self.path = path
        self.size = size
        self.font = pygame.font.Font(self.path, self.size)

    def resize(self, new_size):
        self.size = new_size
        self.font = pygame.font.Font(self.path, self.size)


def scale_surface(surface, target_size):
    """Scales a Pygame surface proportionally to fit into the target size."""
    target_width, target_height = target_size
    width, height = surface.get_size()
    scale_factor = min(target_width / width, target_height / height)
    new_size = (round(width * scale_factor), round(height * scale_factor))
    return pygame.transform.smoothscale(surface, new_size)


def fit_text_in_rect(text, font, color, rect):
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
    # Get the width and height of the text
    text_width, text_height = text.get_size()

    # Calculate the position to center the text
    pos_x = rect.x + (rect.width - text_width) // 2
    pos_y = rect.y + (rect.height - text_height) // 2

    # Draw the text on the screen at the calculated position
    screen.blit(text, (pos_x, pos_y))


class DraggableImage:
    def __init__(self, x, y, image_path, game_width, game_height):
        original_image = pygame.image.load(image_path)
        self.image_size = (game_width // 10, game_height // 7)  # Updated dimensions
        self.hover_image_size = (game_width // 5, game_height // 3.5)  # Updated dimensions
        self.image = scale_surface(original_image, self.image_size)
        self.hover_image = scale_surface(original_image, self.hover_image_size)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dragging = False
        self.hovering = False
        self.selected = False

    def draw(self, screen):
        if self.hovering:
            # calculate the new x and y coordinates
            hover_x = self.rect.x - (self.hover_image_size[0] - self.image_size[0]) // 2
            hover_y = self.rect.y - (self.hover_image_size[1] - self.image_size[1]) // 2 - 50

            # adjust x if the hover image would go out of the screen on the left or right
            if hover_x < 0:
                hover_x = 0
            elif hover_x + self.hover_image_size[0] > screen.get_width():
                hover_x = screen.get_width() - self.hover_image_size[0]

            # adjust y if the hover image would go out of the screen on the top or bottom
            if hover_y < 0:
                hover_y = 0
            elif hover_y + self.hover_image_size[1] > screen.get_height():
                hover_y = screen.get_height() - self.hover_image_size[1]

            screen.blit(self.hover_image, (hover_x, hover_y))
        else:
            screen.blit(self.image, self.rect)

    def handle_event(self, event, green_rect, red_rect):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.hovering = False  # Update here to stop hovering effect when dragging
                mouse_x, mouse_y = event.pos
                self.offset_x = self.rect.x - mouse_x
                self.offset_y = self.rect.y - mouse_y
                return self
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            if not (green_rect.colliderect(self.rect) or red_rect.colliderect(self.rect)):
                self.rect.topleft = green_rect.topleft
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                self.rect.x = mouse_x + self.offset_x
                self.rect.y = mouse_y + self.offset_y
                return self

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # 3 is for right button
            if self.rect.collidepoint(event.pos):
                self.selected = not self.selected
                return self

    def update(self, mouse_pos, dragged_image):
        if not self.dragging and self != dragged_image:
            if self.rect.collidepoint(mouse_pos):
                self.hovering = True
            else:
                self.hovering = False


class GameObject:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image_width = 81
        self.image_height = self.screen_height // 7
        num_images = 10  # Number of images
        rect_width = self.image_width * num_images  # Width of the rectangles
        # Calculate the x-coordinate for centering the rectangles
        green_rect_x = (self.screen_width - rect_width) // 2
        red_rect_x = (self.screen_width - rect_width) // 2

        self.green_rect = pygame.Rect(green_rect_x, self.screen_height - self.image_height,
                                      rect_width, self.image_height)
        self.red_rect = pygame.Rect(red_rect_x, 0,
                                    rect_width, self.image_height)
        self.images = [
            DraggableImage(self.green_rect.x + self.image_width * (i % num_images),
                           self.green_rect.y + self.image_height * (i // num_images), 'decoy.png', self.screen_width,
                           self.screen_height)
            for i in range(15)  # Change the range to the number of images you have
        ]
        self.dragged_image = None

    def draw(self, screen):
        hover_image = None  # Keep track of the image being hovered over
        for image in self.images:
            if image.hovering and not image.dragging:
                hover_image = image
            elif image != self.dragged_image:
                image.draw(screen)

        dragged_image = None
        for image in self.images:
            if image.dragging and not image.hovering:
                dragged_image = image

        if self.dragged_image:
            self.dragged_image.draw(screen)  # Draw the image being dragged last
        if hover_image and not dragged_image:
            hover_image.draw(screen)  # Draw the image being hovered over last
        for image in self.images:
            if image.selected:
                enlarged_image = pygame.transform.scale(image.image, (self.screen_width, self.screen_height))
                screen.blit(enlarged_image, (0, 0))

    def handle_event(self, event):
        for image in self.images:
            dragged_image = image.handle_event(event, self.green_rect, self.red_rect)
            if dragged_image:
                self.dragged_image = dragged_image
        if event.type == pygame.MOUSEBUTTONUP:
            self.reposition_images()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 1 is for left button
            for image in self.images:
                if image.selected:
                    image.selected = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for image in reversed(self.images):  # reverse order to select topmost image first
                if image.rect.collidepoint(event.pos):
                    image.selected = not image.selected
                    return  # return after the first image is selected/deselected, preventing multiple selections/deselections

    def reposition_images(self):
        green_images = [img for img in self.images if self.green_rect.colliderect(img.rect)]
        red_images = [img for img in self.images if self.red_rect.colliderect(img.rect)]

        num_green_images = len(green_images)
        num_red_images = len(red_images)

        green_image_width = self.image_width * 10 / num_green_images if num_green_images > 10 else self.image_width
        red_image_width = self.image_width * 10 / num_red_images if num_red_images > 10 else self.image_width

        for i, img in enumerate(green_images):
            img.rect.topleft = (self.green_rect.x + green_image_width * i, self.green_rect.y)

        for i, img in enumerate(red_images):
            img.rect.topleft = (self.red_rect.x + red_image_width * i, self.red_rect.y)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for image in self.images:
            image.update(mouse_pos, self.dragged_image)


class Game:
    def __init__(self, fps=60):
        pygame.init()
        infoObject = pygame.display.Info()
        self.width = infoObject.current_w
        self.height = infoObject.current_h
        self.fps = fps
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_small = ResizableFont('Arial Narrow.ttf', 24)

        # Load the background image
        self.background_image = pygame.image.load('img/board.jpg')  # Replace with your image path
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.width, self.height))  # Scale the image to fit the screen

        # Create the panel
        self.panel_left = Panel(self.screen.get_rect(), 0.265, 1)

    def run(self):
        while self.running:
            self.clock.tick(self.fps)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            self.game_object.handle_event(event)

    def update(self):
        self.game_object.update()

    def draw(self):
        self.screen.blit(self.background_image, (0, 0))
        self.panel_left.draw(self.screen)

        self.game_object.draw(self.screen)
        pygame.display.flip()


class MyGame(Game):
    def __init__(self):
        super().__init__()
        self.game_object = GameObject(self.width, self.height)  # pass the width and height
        fake_event = pygame.event.Event(pygame.MOUSEBUTTONUP)  # Create a fake event
        self.game_object.handle_event(fake_event)  # Handle the fake event

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            self.game_object.handle_event(event)


if __name__ == '__main__':
    game = MyGame()
    game.run()
