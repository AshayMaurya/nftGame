from settings import *
import random
# 2 classes used, Block and Tetromino
class Block(pg.sprite.Sprite):
    def __init__(self, tetromino, pos):
        # Initialize a block within a tetromino
        self.tetromino = tetromino
        self.pos = vec(pos) + INIT_POS_OFFSET
        self.next_pos = vec(pos) + NEXT_POS_OFFSET
        self.alive = True

        super().__init__(tetromino.tetris.sprite_group)
        self.image = tetromino.image
        self.rect = self.image.get_rect()

        # Set up special effects for the block
        self.sfx_image = self.image.copy()
        self.sfx_image.set_alpha(110)
        self.sfx_speed = random.uniform(0.2, 0.6)
        self.sfx_cycles = random.randrange(6, 8)
        self.cycle_counter = 0

    def sfx_end_time(self):
        # Check if the special effects duration has ended
        if self.tetromino.tetris.app.anim_trigger:
            self.cycle_counter += 1
            if self.cycle_counter > self.sfx_cycles:
                self.cycle_counter = 0
                return True

    def sfx_run(self):
        # Run special effects on the block (e.g., rotation and alpha changes)
        self.image = self.sfx_image
        self.pos.y -= self.sfx_speed
        self.image = pg.transform.rotate(self.image, pg.time.get_ticks() * self.sfx_speed)

    def is_alive(self):
        # Check if the block is still alive and manage special effects
        if not self.alive:
            if not self.sfx_end_time():
                self.sfx_run()
            else:
                self.kill()

    def rotate(self, pivot_pos):
        # Rotate the block around a given pivot position
        translated = self.pos - pivot_pos
        rotated = translated.rotate(90)
        return rotated + pivot_pos

    def set_rect_pos(self):
        # Set the rectangle position based on the block's current or next position
        pos = [self.next_pos, self.pos][self.tetromino.current]
        self.rect.topleft = pos * TILE_SIZE

    def update(self):
        # Update the block's status, apply special effects, and set its rectangle position
        self.is_alive()
        self.set_rect_pos()

    def is_collide(self, pos):
        # Check if the block collides with the game field or other blocks
        x, y = int(pos.x), int(pos.y)
        if 0 <= x < FIELD_W and y < FIELD_H and (
                y < 0 or not self.tetromino.tetris.field_array[y][x]):
            return False
        return True


class Tetromino:
    def __init__(self, tetris, current=True):
        # Initialize a tetromino with a random shape and image
        self.tetris = tetris
        self.shape = random.choice(list(TETROMINOES.keys()))
        self.image = random.choice(tetris.app.images)
        self.blocks = [Block(self, pos) for pos in TETROMINOES[self.shape]]
        self.landing = False
        self.current = current

    def rotate(self):
        # Rotate the tetromino if there's no collision after rotation
        pivot_pos = self.blocks[0].pos
        new_block_positions = [block.rotate(pivot_pos) for block in self.blocks]

        if not self.is_collide(new_block_positions):
            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]

    def is_collide(self, block_positions):
        # Check if the tetromino collides with the game field or other blocks
        return any(map(Block.is_collide, self.blocks, block_positions))

    def move(self, direction):
        # Move the tetromino in the specified direction if there's no collision
        move_direction = MOVE_DIRECTIONS[direction]
        new_block_positions = [block.pos + move_direction for block in self.blocks]
        is_collide = self.is_collide(new_block_positions)

        if not is_collide:
            for block in self.blocks:
                block.pos += move_direction
        elif direction == 'down':
            self.landing = True

    def update(self):
        # Update the tetromino's position, triggering its downward movement
        self.move(direction='down')
