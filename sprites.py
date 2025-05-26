
import pygame
from config import *
import random
import os

def load_images_by_prefix(folder, prefix):
    images = []
    for filename in sorted(os.listdir(folder)):
        if filename.startswith(prefix) and filename.endswith(".png"):
            path = os.path.join(folder, filename)
            image = pygame.image.load(path).convert_alpha()
            images.append(image)
    return images
#funckja daje losowy obiekt (nie enemy)
def get_cached_images(cls, attr_name, folder, prefix):
    if not hasattr(cls, attr_name):
        setattr(cls, attr_name, load_images_by_prefix(folder, prefix))
    return getattr(cls, attr_name)



class Player(pygame.sprite.Sprite):
    animations_cache = {}

    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0
        self.facing = 'down'

        if not Player.animations_cache:
            for dir in ['down', 'up', 'left', 'right']:
                Player.animations_cache[dir] = [
                    pygame.transform.scale(
                        pygame.image.load(f'./images/character{dir[0].upper()}{i}.png'), (self.width, self.height)
                    ) for i in range(1, 3)
                ]
        self.animations = Player.animations_cache

        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 100
        self.image = self.animations[self.facing][0]

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.movement()

        prev_pos = self.rect.topleft  # zapamiętaj pozycję

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        moved = self.rect.topleft != prev_pos  # sprawdź, czy faktycznie się ruszył

        self.animate(moved)
        self.collide_enemy()
        self.collide_door()

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.facing = 'left'
            self.x_change -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.facing = 'right'
            self.x_change += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.facing = 'up'
            self.y_change -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.facing = 'down'
            self.y_change += PLAYER_SPEED
        if self.x_change != 0 and self.y_change != 0:
            self.x_change *= 0.7071
            self.y_change *= 0.7071

    def collide_blocks(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if hits:
            if direction == 'x':
                if self.x_change > 0:
                    self.rect.right = hits[0].rect.left
                if self.x_change < 0:
                    self.rect.left = hits[0].rect.right
            if direction == 'y':
                if self.y_change > 0:
                    self.rect.bottom = hits[0].rect.top
                if self.y_change < 0:
                    self.rect.top = hits[0].rect.bottom

    def collide_enemy(self):
        if pygame.sprite.spritecollideany(self, self.game.enemies):
            self.game.last_frame = self.game.screen.copy()
            self.kill()
            self.game.playing = False
            self.game.game_over_screen()


    def collide_door(self):
        if pygame.sprite.spritecollideany(self, self.game.door):
            self.game.stage += 1
            self.kill()
            self.game.playing = False
            self.game.level_transition_screen()

    def animate(self, moved):
        if not moved:
            self.current_frame = 0
            self.image = self.animations[self.facing][self.current_frame]
            return

        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.facing])
            self.image = self.animations[self.facing][self.current_frame]


from enemy_animation_data import animation_durations  # <- import ręcznych czasów

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.facing = random.choice(['up', 'down'])
        self.speed = random.randint(3, 7)
        self.movement_loop = 0
        self.travel = 40
        self.x_change = 0
        self.y_change = 0

        # Losuj zestaw sprite’ów
        self.sprite_id = random.choice(list(animation_durations.keys()))
        self.animations = {}
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

        for direction in ['up', 'down', 'left', 'right']:
            prefix = f"{self.sprite_id}_{direction[0].upper()}"
            frames = get_cached_images(Enemy, f'{self.sprite_id}_{direction}', './images/enemy_sprites', prefix)
            durations = animation_durations[self.sprite_id][direction]
            self.animations[direction] = list(zip(frames, durations))

        self.image = pygame.transform.scale(
            self.animations[self.facing][0][0], (self.width, self.height)
        )
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.movement()

        prev_pos = self.rect.topleft  # zapamiętaj poprzednią pozycję

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        moved = self.rect.topleft != prev_pos  # porównujemy pozycję

        self.animate(moved)

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        if self.facing == 'up':
            self.y_change -= self.speed
            self.movement_loop -= 1
            if self.movement_loop <= -self.travel:
                self.facing = 'down'
        elif self.facing == 'down':
            self.y_change += self.speed
            self.movement_loop += 1
            if self.movement_loop >= self.travel:
                self.facing = 'up'
        elif self.facing == 'left':
            self.x_change -= self.speed
            self.movement_loop -= 1
            if self.movement_loop <= -self.travel:
                self.facing = 'right'
        elif self.facing == 'right':
            self.x_change += self.speed
            self.movement_loop += 1
            if self.movement_loop >= self.travel:
                self.facing = 'left'

    def animate(self, moved):
        if not moved:
            self.current_frame = 0
            frame, _ = self.animations[self.facing][self.current_frame]
            self.image = pygame.transform.scale(frame, (self.width, self.height))
            return

        now = pygame.time.get_ticks()
        frame, duration = self.animations[self.facing][self.current_frame]

        if now - self.last_update > duration:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.facing])
            frame, _ = self.animations[self.facing][self.current_frame]

        self.image = pygame.transform.scale(frame, (self.width, self.height))

    def collide_blocks(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if hits:
            if direction == 'x':
                if self.x_change > 0:
                    self.rect.right = hits[0].rect.left
                elif self.x_change < 0:
                    self.rect.left = hits[0].rect.right
            elif direction == 'y':
                if self.y_change > 0:
                    self.rect.bottom = hits[0].rect.top
                elif self.y_change < 0:
                    self.rect.top = hits[0].rect.bottom

class Block(pygame.sprite.Sprite):

    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        if self.game.stage == 1:
            image = random.choice(get_cached_images(Block, 'tree_images', './images', 'tree'))


        elif self.game.stage == 2:
            image = random.choice(get_cached_images(Block, 'ice_peak1', './images', 'ice_peak'))
        elif self.game.stage == 3:
            image = random.choice(get_cached_images(Block, 'sand_peak1', './images', 'sand_peak'))

        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        if self.game.stage == 1:
            image = random.choice(get_cached_images(Ground, 'dirt_images', './images', 'dirt'))
        elif self.game.stage == 2:
            image = random.choice(get_cached_images(Ground, 'snow_images', './images', 'snow'))
        elif self.game.stage == 3:
            image = random.choice(get_cached_images(Ground, 'sand_images', './images', 'sand1'))

        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Door(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.door
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        image = random.choice(get_cached_images(Door, 'door', './images', 'door'))
        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
