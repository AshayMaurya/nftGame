from settings import *  # Importing settings from external file
from tetris import Tetris, Text  # Importing Tetris and Text classes from external file
import sys  # Importing the sys module for system-related operations
import pathlib  # Importing the pathlib module for working with file paths

class App:
    def __init__(self):
        pg.init()  # Initialize Pygame
        pg.display.set_caption('Tetris')
        self.screen = pg.display.set_mode(WIN_RES)  # Create the game window
        self.clock = pg.time.Clock()  # Create a Pygame clock
        self.set_timer()  # Set up timer events for animation
        self.images = self.load_images()  # Load game sprite images
        self.tetris = Tetris(self)  # Initialize Tetris game instance
        self.text = Text(self)  # Initialize Text instance for displaying information

    def load_images(self):
        # Load game sprite images from the specified directory and scale them
        files = [item for item in pathlib.Path(SPRITE_DIR_PATH).rglob('*.png') if item.is_file()]
        images = [pg.image.load(file).convert_alpha() for file in files]
        images = [pg.transform.scale(image, (TILE_SIZE, TILE_SIZE)) for image in images]
        return images

    def set_timer(self):
        # Set up timer events for regular and fast animation intervals
        self.user_event = pg.USEREVENT + 0
        self.fast_user_event = pg.USEREVENT + 1
        self.anim_trigger = False
        self.fast_anim_trigger = False
        pg.time.set_timer(self.user_event, ANIM_TIME_INTERVAL)
        pg.time.set_timer(self.fast_user_event, FAST_ANIM_TIME_INTERVAL)

    def update(self):
        # Update the Tetris game state and control the frame rate
        self.tetris.update()
        self.clock.tick(FPS)

    def draw(self):
        # Draw the game window, background, Tetris field, Tetris blocks, and additional text
        self.screen.fill(color=BG_COLOR)
        self.screen.fill(color=FIELD_COLOR, rect=(0, 0, *FIELD_RES))
        self.tetris.draw()
        self.text.draw()
        pg.display.flip()

    def check_events(self):
        # Check for user events such as quitting the game, key presses, and timer triggers
        self.anim_trigger = False
        self.fast_anim_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                self.tetris.control(pressed_key=event.key)
            elif event.type == self.user_event:
                self.anim_trigger = True
            elif event.type == self.fast_user_event:
                self.fast_anim_trigger = True

    def run(self):
        # Main game loop that continuously checks events, updates the game state, and redraws the window
        while True:
            self.check_events()
            self.update()
            self.draw()

if __name__ == '__main__':
    # Create an instance of the App class and run the game
    app = App()
    app.run()
