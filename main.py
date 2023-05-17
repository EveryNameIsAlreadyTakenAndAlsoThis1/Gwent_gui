import pygame

class DraggableImage:
    def __init__(self, x, y, image_path, image_size=(50, 50)):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, image_size)  # Resize the image
        self.hover_image = pygame.transform.scale(self.image, (75, 75))  # An enlarged version of the image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dragging = False
        self.hovering = False
        self.selected = False  # new attribute

    def draw(self, screen):
        if self.hovering and not self.dragging:  # Draw the enlarged image if the mouse is hovering over the image and the image is not being dragged
            screen.blit(self.hover_image, self.rect)
        else:
            screen.blit(self.image, self.rect)

    def handle_event(self, event, green_rect, red_rect):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                mouse_x, mouse_y = event.pos
                self.offset_x = self.rect.x - mouse_x
                self.offset_y = self.rect.y - mouse_y
                return self  # Return the image itself when it starts being dragged
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            if not (green_rect.colliderect(self.rect) or red_rect.colliderect(self.rect)):
                self.rect.topleft = green_rect.topleft  # Snap back to green rectangle if outside both rectangles
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, mouse_y = event.pos
                self.rect.x = mouse_x + self.offset_x
                self.rect.y = mouse_y + self.offset_y
                return self  # Also return the image itself when it's being dragged
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # 3 is for right button
            if self.rect.collidepoint(event.pos):
                self.selected = not self.selected
                return self

    def update(self, mouse_pos):
        if not self.dragging:  # Only check for hover when the image is not being dragged
            if self.rect.collidepoint(mouse_pos):
                self.hovering = True
            else:
                self.hovering = False


class GameObject:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.green_rect = pygame.Rect(100, 100, 200, 200)  # Define the green rectangle
        self.red_rect = pygame.Rect(500, 100, 200, 200)  # Define the red rectangle
        self.images = [
            DraggableImage(self.green_rect.x + 50 * (i % 4), self.green_rect.y + 50 * (i // 4), f'decoy.png')
            for i in range(8)  # Change the range to the number of images you have
        ]
        self.dragged_image = None

    def draw(self, screen):
        hover_image = None  # Keep track of the image being hovered over
        for image in self.images:
            if image.hovering and not image.dragging:
                hover_image = image
            elif image != self.dragged_image:
                image.draw(screen)
        if self.dragged_image:
            self.dragged_image.draw(screen)  # Draw the image being dragged last
        if hover_image:
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

        for i, img in enumerate(green_images):
            img.rect.topleft = (self.green_rect.x + 50 * (i % 4), self.green_rect.y + 50 * (i // 4))
        for i, img in enumerate(red_images):
            img.rect.topleft = (self.red_rect.x + 50 * (i % 4), self.red_rect.y + 50 * (i // 4))

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for image in self.images:
            image.update(mouse_pos)


class Game:
    def __init__(self, width=800, height=600, fps=60):
        pygame.init()
        self.width = width
        self.height = height
        self.fps = fps
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True

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
            self.game_object.handle_event(event)

    def update(self):
        self.game_object.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (0, 255, 0), self.game_object.green_rect)  # Draw the green rectangle
        pygame.draw.rect(self.screen, (255, 0, 0), self.game_object.red_rect)  # Draw the red rectangle
        self.game_object.draw(self.screen)
        pygame.display.flip()

class MyGame(Game):
    def __init__(self):
        super().__init__()
        self.game_object = GameObject(self.width, self.height)  # pass the width and height

if __name__ == '__main__':
    game = MyGame()
    game.run()

