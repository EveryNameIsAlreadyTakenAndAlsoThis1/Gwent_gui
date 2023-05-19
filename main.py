import pygame


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

        # Calculate the width of panel-left
        self.panel_left_width = int(self.width * 0.265)  # 26.5% of the window width
        self.panel_left_height = self.height  # Full height
        self.panel_left = pygame.Rect(0, 0, self.panel_left_width, self.panel_left_height)

        # Load the background image
        self.background_image = pygame.image.load('img/board.jpg')  # Replace with your image path
        self.background_image = pygame.transform.scale(self.background_image,
                                                       (self.width, self.height))  # Scale the image to fit the screen

        # Leader box opponent

        # Calculate the size and position of leader-box
        self.leader_box_width = int(self.panel_left_width * 0.314)  # 31.4% of the panel width
        self.leader_box_height = int(self.panel_left_height * 0.125)  # 12.5% of the panel height
        self.leader_box_x = self.panel_left.x + self.panel_left_width * 0.275  # 27.5% from the left edge of the panel
        self.leader_box_y = self.panel_left.y + self.panel_left_height * 0.0755  # 7.55% from the top of the panel
        self.leader_box = pygame.Rect(self.leader_box_x, self.leader_box_y, self.leader_box_width,
                                      self.leader_box_height)

        self.leader_container_width = int(self.leader_box_width * 0.63)  # 63% of the leader_box width
        self.leader_container_height = self.leader_box_height  # 100% of the leader_box height

        # The leader_container is centered within the leader_box
        self.leader_container_x = self.leader_box.x + (self.leader_box_width - self.leader_container_width) // 2
        self.leader_container_y = self.leader_box.y + (self.leader_box_height - self.leader_container_height) // 2

        self.leader_container = pygame.Rect(self.leader_container_x, self.leader_container_y,
                                            self.leader_container_width, self.leader_container_height)

        self.leader_active_width = int(self.leader_box_width * 0.24)  # 24% of the leader_box width
        self.leader_active_height = int(self.leader_box_height * 0.28)  # 28% of the leader_box height

        # The leader_active is positioned within the leader_box
        self.leader_active_x = self.leader_box.x + int(self.leader_box_width * 0.75)
        self.leader_active_y = self.leader_box.y + int(self.leader_box_height * 0.33)

        self.leader_active = pygame.Rect(self.leader_active_x, self.leader_active_y, self.leader_active_width,
                                         self.leader_active_height)

        # Stats opponent

        self.stats_op_width = int(self.panel_left_width * 0.89)  # 89% of the panel_left width
        self.stats_op_height = int(self.panel_left_height * 0.125)  # 12.5% of the panel_left height

        # The stats_op is positioned within the panel_left
        self.stats_op_x = self.panel_left.x
        self.stats_op_y = self.panel_left.y + int(self.panel_left_height * 0.2425)

        self.stats_op = pygame.Rect(self.stats_op_x, self.stats_op_y, self.stats_op_width, self.stats_op_height)

        self.profile_img_width = int(self.stats_op_width * 0.219)  # 21.9% of the stats_op width
        self.profile_img_height = int(self.stats_op_height * 0.8)  # 80% of the stats_op height

        # The profile_img is positioned within the stats_op
        self.profile_img_x = self.stats_op.x + int(self.stats_op_width * 0.284)
        self.profile_img_y = self.stats_op.y + int(self.stats_op_height * 0.096)

        self.profile_img = pygame.Rect(self.profile_img_x, self.profile_img_y, self.profile_img_width,
                                       self.profile_img_height)
        self.profile_img_pic = pygame.image.load('img/icons/profile.png')
        self.profile_img_pic = pygame.transform.scale(self.profile_img_pic,
                                                      (self.profile_img_width, self.profile_img_height))

        self.name_op_font_size = int(self.stats_op_height * 0.20)  # 20% of the stats_op height (as per CSS)
        self.name_op_font = ResizableFont('Arial Narrow.ttf', self.name_op_font_size)
        self.name_op_text = self.name_op_font.font.render('Opponent', True, (255, 255, 255))  # RGB white color
        self.name_op_x = int(self.stats_op_width * 0.53)  # 53% of the stats_op width (as per CSS)
        self.name_op_y = int(self.stats_op_height * 0.06)  # 6% of the stats_op height (as per CSS)

        self.deck_name_op_text = self.font_small.font.render("Deck Name", True, (210, 180, 140))  # RGB for tan color
        self.deck_name_op_x = int(self.stats_op_width * 0.53)  # 53% of the stats_op width
        self.deck_name_op_y = int(self.stats_op_height * 0.25)  # 25% of the stats_op height

        self.hand_count_op_left = self.stats_op_width * 0.5325  # 53.25% of panel's width
        self.hand_count_op_top = self.stats_op_y + self.stats_op_height * 0.585  # 58.5% of stats's height + stats's y
        self.hand_count_op_width = self.stats_op_width * 0.17  # 17% of panel's width
        self.hand_count_op_height = self.stats_op_height * 0.295  # 29.5% of stats's height
        self.hand_count_image = pygame.image.load('img/icons/icon_card_count.png')
        self.hand_count_image = scale_surface(self.hand_count_image,
                                              (self.hand_count_op_width, self.hand_count_op_height))

        # Render the text for the hand count
        self.hand_count_op_rec = pygame.Rect(self.hand_count_op_left, self.hand_count_op_top, self.hand_count_op_width,
                                             self.hand_count_op_height)
        self.hand_count_op_image_rect = self.hand_count_image.get_rect(
            topleft=(self.hand_count_op_left, self.hand_count_op_top))

        self.hand_count_op_text_rect = pygame.Rect(self.hand_count_op_left + self.hand_count_image.get_width(),
                                                   self.hand_count_op_top,
                                                   self.hand_count_op_width - self.hand_count_image.get_width(),
                                                   self.hand_count_op_height)
        self.hand_count_op_text = fit_text_in_rect("10", self.font_small, (218, 165, 32), self.hand_count_op_text_rect)

        self.gem_on_image = pygame.image.load('img/icons/icon_gem_on.png')  # Change this path to your actual file

        self.gem1_op_left = self.stats_op_width * 0.8  # 80% of stats_op's width
        self.gem1_op_top = self.stats_op_y + self.stats_op_height * 0.56  # 56% of stats_op's height + stats_op's top
        self.gem1_op_width = self.panel_left_width * 0.09  # 9% of panel_left's width
        self.gem1_op_height = self.stats_op_height * 0.31  # 31% of stats_op's height

        # Scale the image to fit the rectangle
        self.gem_on_image = pygame.transform.scale(self.gem_on_image, (self.gem1_op_width, self.gem1_op_height))

        self.gem2_op_left = self.stats_op_width * 0.7075  # 70.75% of stats_op's width
        self.gem2_op_top = self.stats_op_y + self.stats_op_height * 0.5625  # 56.25% of stats_op's height + stats_op's top
        self.gem2_op_width = self.panel_left_width * 0.09  # 9% of panel_left's width
        self.gem2_op_height = self.stats_op_height * 0.31  # 31% of stats_op's height

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

        # pygame.draw.rect(self.screen, (255, 0, 0), self.panel_left)  # Draw the left panel
        # pygame.draw.rect(self.screen, (0, 255, 0), self.game_object.green_rect)  # Draw the green rectangle
        # pygame.draw.rect(self.screen, (255, 0, 0), self.game_object.red_rect)  # Draw the red rectangle
        # pygame.draw.rect(self.screen, (255, 255, 0), self.leader_box)  # Draw the leader box
        # pygame.draw.rect(self.screen, (0, 0, 255), self.leader_container)  # Draw the leader container
        # pygame.draw.rect(self.screen, (255, 255, 255), self.leader_active)  # Draw the leader active
        # pygame.draw.rect(self.screen, (0, 0, 255), self.stats_op)  # Draw the stats_op
        # pygame.draw.rect(self.screen, (0, 255, 255), self.profile_img)  # Draw the profile_img
        # pygame.draw.rect(self.screen, (255, 255, 255), self.hand_count_op_rec)  # Draw the hand count_op rectangle
        # pygame.draw.rect(self.screen, (0, 0, 0), self.hand_count_op_image_rect)
        # pygame.draw.rect(self.screen, (255, 0, 255), self.hand_count_op_text_rect)
        surface = pygame.Surface((self.stats_op.width, self.stats_op.height))
        surface.fill((20, 20, 20))
        surface.set_alpha(128)
        self.screen.blit(surface, (self.stats_op.left, self.stats_op.top))

        self.screen.blit(self.hand_count_image, self.hand_count_op_image_rect)

        self.screen.blit(self.profile_img_pic, (self.profile_img.x, self.profile_img.y))
        self.screen.blit(self.name_op_text, (self.stats_op.x + self.name_op_x, self.stats_op.y + self.name_op_y))
        self.screen.blit(self.deck_name_op_text,
                         (self.stats_op.x + self.deck_name_op_x,
                          self.stats_op.y + self.deck_name_op_y))  # Draw the deck name

        draw_centered_text(self.screen, self.hand_count_op_text, self.hand_count_op_text_rect)

        self.screen.blit(self.gem_on_image, (self.gem1_op_left, self.gem1_op_top))  # Draw the gem1_op
        self.screen.blit(self.gem_on_image, (self.gem2_op_left, self.gem2_op_top))  # Draw the gem2_op

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
