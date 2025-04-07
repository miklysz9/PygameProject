import pygame
import time
import random
from tkinter import messagebox, Tk

# Inicjalizacja Tkintera
root = Tk()
root.withdraw()


# Main char
class Character(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x = 30
        self.y = window_y / 2
        self.width = 60
        self.height = 60

        self.character = pygame.image.load('./images/character.png')
        self.character = pygame.transform.scale(self.character, (self.width, self.height))

        self.image = self.character
        self.rect = self.character.get_rect()
        self.mask = pygame.mask.from_surface(self.character)

    def update(self):
        self.movement()
        self.correction()
        self.check_collision()
        self.rect.center = (self.x, self.y)

    def movement(self):
        global cooldown_tracker
        cooldown_tracker += clock.get_time()
        if cooldown_tracker > 200:
            cooldown_tracker = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and cooldown_tracker == 0:
            self.x -= 60

        if keys[pygame.K_RIGHT] and cooldown_tracker == 0:
            self.x += 60

        if keys[pygame.K_UP] and cooldown_tracker == 0:
            self.y -= 60

        if keys[pygame.K_DOWN] and cooldown_tracker == 0:
            self.y += 60

    def correction(self):
        if self.x - self.width / 2 < 0:
            self.x = self.width / 2
        elif self.x + self.width / 2 > window_x:
            self.x = window_x - self.width / 2

        if self.y - self.height / 2 < 0:
            self.y = self.height / 2
        elif self.y + self.height / 2 > window_y:
            self.y = window_y - self.height / 2

    def check_collision(self):
        car_check = pygame.sprite.spritecollide(self, car_group, False, pygame.sprite.collide_mask)
        if car_check:
            explosion.explode(self.x, self.y)


# Cars
class Car(pygame.sprite.Sprite):
    def __init__(self, number):
        super().__init__()
        if number == 1:
            self.x = 240
            self.image = pygame.image.load('./images/car1.png')
            self.vel = -4
        else:
            self.x = 480
            self.image = pygame.image.load('./images/car2.png')
            self.vel = 6

        self.y = window_y / 2
        self.width = 60
        self.height = 120
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.movement()
        self.rect.center = (self.x, self.y)

    def movement(self):
        self.y += self.vel

        if self.y - self.height / 2 < 0:
            self.y = self.height / 2
            self.vel *= -1

        elif self.y + self.height / 2 > window_y:
            self.y = window_y - self.height / 2
            self.vel *= -1


class Screen(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.img1 = pygame.image.load('./images/scene.png')
        self.img2 = pygame.image.load('./images/win.png')
        self.img3 = pygame.image.load('./images/lose.png')

        self.img1 = pygame.transform.scale(self.img1, (window_x, window_y))
        self.img2 = pygame.transform.scale(self.img2, (window_x, window_y))
        self.img3 = pygame.transform.scale(self.img3, (window_x, window_y))

        self.image = self.img1
        self.x = 0
        self.y = 0

        self.rect = self.image.get_rect()

    def update(self):
        self.rect.topleft = (self.x, self.y)


class Explosion(object):
    def __init__(self):
        self.costume = 1
        self.width = 140
        self.height = 140
        self.image = pygame.image.load('./images/explosion' + str(self.costume) + '.png')
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def explode(self, x, y):
        x = x - self.width / 2
        y = y - self.height / 2
        deleteCharacter()

        while self.costume < 9:
            self.image = pygame.image.load('./images/explosion' + str(self.costume) + '.png')
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            screen.blit(self.image, (x, y))
            pygame.display.update()

            self.costume += 1
            time.sleep(0.1)
        deleteItems()
        endScreen(0)


def deleteCharacter():
    global mainchar

    mainchar.kill()
    screen_group.draw(screen)
    car_group.draw(screen)

    screen_group.update()
    car_group.update()

    pygame.display.update()


def deleteItems():
    car_group.empty()


def restart_game():
    global mainchar, car_group, screen_group, bg

    # Resetowanie ekranu gry
    bg.image = bg.img1
    mainchar = Character()
    mainchar_group.empty()
    mainchar_group.add(mainchar)

    car_group.empty()
    car_group.add(Car(1), Car(2))


def endScreen(n):
    if n == 0:
        bg.image = bg.img3
    elif n == 1:
        bg.image = bg.img2

    screen_group.draw(screen)
    pygame.display.update()
    time.sleep(1)

    root.update_idletasks()
    root.update()

    answer = messagebox.askyesno("Game Over!", "Chcesz zagrac ponownie?")

    if not answer:
        pygame.quit()
        exit()
    else:
        restart_game()


# Start Screen
def start_screen():
    screen.fill(black)
    font = pygame.font.Font(None, 36)
    text = font.render("Naciśnij spację, aby zacząć grać", True, white)
    text_rect = text.get_rect(center=(window_x // 2, window_y // 2))
    screen.blit(text, text_rect)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False


# Window size
window_x = 720
window_y = 480

# Colors
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

pygame.init()

screen = pygame.display.set_mode((window_x, window_y))
clock = pygame.time.Clock()
pygame.display.set_caption("CrossTheRoad")
cooldown_tracker = 0

# Object screen
bg = Screen()
screen_group = pygame.sprite.Group()
screen_group.add(bg)

# Object char
mainchar = Character()
mainchar_group = pygame.sprite.Group()
mainchar_group.add(mainchar)

# Object car
slow_car = Car(1)
fast_car = Car(2)
car_group = pygame.sprite.Group()
car_group.add(slow_car, fast_car)

# Object explosion
explosion = Explosion()

# Wywołanie start screen
start_screen()

# Running code
run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    screen_group.draw(screen)
    car_group.draw(screen)
    mainchar_group.draw(screen)

    car_group.update()
    mainchar_group.update()

    screen_group.update()

    pygame.display.update()

pygame.quit()