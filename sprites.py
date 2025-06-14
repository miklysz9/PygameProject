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

def get_cached_images(cls, attr_name, folder, prefix):
    if not hasattr(cls, attr_name):
        setattr(cls, attr_name, load_images_by_prefix(folder, prefix))
    return getattr(cls, attr_name)

class Player(pygame.sprite.Sprite):
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

        # Ładujemy tylko dwie klatki animacji
        self.frames = [
            pygame.transform.scale(pygame.image.load('./images/character.png').convert_alpha(), (self.width, self.height)),
            pygame.transform.scale(pygame.image.load('./images/character1.png').convert_alpha(), (self.width, self.height))
        ]

        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 200  # czas zmiany klatki w ms

        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.movement()

        prev_pos = self.rect.topleft

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        moved = self.rect.topleft != prev_pos

        self.animate(moved)

        self.collide_enemy()
        self.collide_door()
        self.collide_coins()

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x_change -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.x_change += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.y_change -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.y_change += PLAYER_SPEED
        if self.x_change != 0 and self.y_change != 0:
            self.x_change *= 0.7071
            self.y_change *= 0.7071

    def animate(self, moved):
        if not moved:
            self.current_frame = 0
            self.image = self.frames[self.current_frame]
            return

        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]


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

    def collide_coins(self):
        hits = pygame.sprite.spritecollide(self, self.game.coins, True)
        for coin in hits:
            coin.collect()  # Zbieranie monety
            self.game.score += 25  # Dodanie punktów


from enemy_animation_data import animation_durations  # <- import ręcznych czasów

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Wybór sprite_id zależny od aktualnej mapy (stage)
        if self.game.stage == 1:
            self.sprite_id = random.choice(['car1', 'car2', 'car3'])

        elif self.game.stage == 2:
            self.sprite_id = random.choice(['iceorc', 'car4', 'car8'])

        elif self.game.stage == 3:
            self.sprite_id = random.choice(['car5', 'car6', 'car7'])
        else:
            # Na wszelki wypadek dla innych map
            self.sprite_id = random.choice(['car1', 'car2', 'car3', 'car4', 'iceorc', 'car5', 'car6', 'car7'])


        self.x_change = 0
        self.y_change = 0
        self.speed = random.randint(4, 7)
        self.facing = 'down'


        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

        if self.sprite_id == 'car1':
            self.frames = {
                'down': [pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car1dn.png').convert_alpha(), (self.width, self.height))],
                'up': [pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car1up.png').convert_alpha(), (self.width, self.height))]
            }
            self.image = self.frames['down'][0]

        elif self.sprite_id == 'car2':
            self.frames = [
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car2_D1.png').convert_alpha(), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car2_D2.png').convert_alpha(), (self.width, self.height))
            ]
            self.image = self.frames[0]

        elif self.sprite_id == 'car3':
            self.frames = [
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car3.png').convert_alpha(), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car32.png').convert_alpha(), (self.width, self.height))
            ]
            self.image = self.frames[0]

        elif self.sprite_id == 'car4':
            self.frames = [
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car4_D1.png').convert_alpha(), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car4_D2.png').convert_alpha(), (self.width, self.height))
            ]
            self.image = self.frames[0]

        elif self.sprite_id == 'iceorc':
            self.frames = [
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/iceorc.png').convert_alpha(), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/iceorc2.png').convert_alpha(), (self.width, self.height))
            ]
            self.image = self.frames[0]
        elif self.sprite_id == 'car5':
            self.frames = [
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car51.png').convert_alpha(),
                                       (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car52.png').convert_alpha(),
                                       (self.width, self.height))
            ]
            self.image = self.frames[0]

        elif self.sprite_id == 'car6':
            self.frames = [
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car61.png').convert_alpha(),
                                       (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car62.png').convert_alpha(),
                                       (self.width, self.height))
            ]
            self.image = self.frames[0]

        elif self.sprite_id == 'car7':
            self.frames = [
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car71.png').convert_alpha(),
                                       (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car72.png').convert_alpha(),
                                       (self.width, self.height))
            ]
            self.image = self.frames[0]

        elif self.sprite_id == 'car8':
            self.frames = [
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car81.png').convert_alpha(),
                                       (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('./images/enemy_sprites/car82.png').convert_alpha(),
                                       (self.width, self.height))
            ]
            self.image = self.frames[0]

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def animate(self, moved):
        now = pygame.time.get_ticks()

        if self.sprite_id == 'car1':
            if self.facing == 'down':
                self.image = self.frames['down'][0]
            elif self.facing == 'up':
                self.image = self.frames['up'][0]

        elif self.sprite_id in ['car2', 'car3', 'car4', 'iceorc']:
            if moved:
                if now - self.last_update > 150:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
            else:
                self.image = self.frames[0]



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

        elif self.facing == 'down':
            self.y_change += self.speed

        elif self.facing == 'left':
            self.x_change -= self.speed

        elif self.facing == 'right':
            self.x_change += self.speed


    def collide_blocks(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if hits:
            if direction == 'x':
                if self.x_change > 0:
                    self.rect.right = hits[0].rect.left
                    self.speed *= -1
                    self.facing = 'right'
                elif self.x_change < 0:
                    self.rect.left = hits[0].rect.right
                    self.speed *= -1
                    self.facing = 'left'
            elif direction == 'y':
                if self.y_change > 0:
                    self.rect.bottom = hits[0].rect.top
                    self.speed*=-1
                    self.facing = 'down'
                elif self.y_change < 0:
                    self.rect.top = hits[0].rect.bottom
                    self.speed *= -1
                    self.facing = 'up'

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

class Coin(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites, self.game.coins
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        image = random.choice(get_cached_images(Coin, 'coin_images', './images', 'coin'))
        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def collect(self):
        self.game.collected_coins.append((self.x // TILESIZE, self.y // TILESIZE))
        self.kill()