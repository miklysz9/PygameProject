import pygame
from sprites import *
from config import *

class Camera:
    def __init__(self, width, height):

        self.camera = pygame.Rect(0, 0, width, height)

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + WIN_WIDTH // 4
        y = -target.rect.centery + WIN_HEIGHT // 2
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.camera.width - WIN_WIDTH), x)
        y = max(-(self.camera.height - WIN_HEIGHT), y)
        self.camera.topleft = (x, y)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        # self.font = pygame.font.Font(None, 36)
        self.reset_game()

        self.font = pygame.font.SysFont("arial", 28)
        self.timer_font = pygame.font.SysFont("arial", 28)

    def reset_game(self):
        self.stage = 1
        self.lives = 3
        self.intro_screen()

    def get_tilemap(self):
        if self.stage == 1:
            return tilemap1
        elif self.stage == 2:
            return tilemap2
        elif self.stage == 3:
            return tilemap3
        else:
            return tilemap1

    def create_tilemap(self):
        current_tilemap = self.get_tilemap()
        for i, row in enumerate(current_tilemap):
            for j, tile in enumerate(row):
                Ground(self, j, i)
                if tile == "b":
                    Block(self, j, i)
                elif tile == "P":
                    self.player = Player(self, j, i)
                elif tile == "E":
                    Enemy(self, j, i)
                elif tile == "D":
                    Door(self, j, i)

    def new(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.door = pygame.sprite.LayeredUpdates()
        self.create_tilemap()
        self.camera = Camera(len(self.get_tilemap()[0]) * TILESIZE,
                             len(self.get_tilemap()) * TILESIZE)
        self.level_start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.playing = True

    def run(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
            self.last_frame = self.screen.copy()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.lives -= 1
                if self.lives <= 0:
                    self.reset_game()
                else:
                    self.new()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
        self.elapsed_time = pygame.time.get_ticks() - self.level_start_time

    def draw(self):
        self.screen.fill(BLACK)
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        # UI: Timer i życie
        # 1. Tekst "Czas:"
        label_text = self.font.render("Czas:", True, BLACK)

        # 2. Tylko liczby (np. "012.34")
        seconds = self.elapsed_time / 1000
        number_text = self.timer_font.render(f"{seconds:06.2f}", True, BLACK)

        # 3. Osobno litera 's'
        unit_text = self.font.render("s", True, BLACK)

        # 4. Pozycje — wyświetlamy jeden po drugim
        self.screen.blit(label_text, (10, 10))  # "Czas:"
        self.screen.blit(number_text, (10 + label_text.get_width() + 10, 10))  # "012.34"
        self.screen.blit(unit_text, (10 + label_text.get_width() + number_text.get_width() + 15, 10))  # "s"
        lives_text = self.font.render(f"Życia: {self.lives}", True, BLACK)
        self.screen.blit(lives_text, (10, 40))

        pygame.display.update()
        self.clock.tick(FPS)

    def intro_screen(self):
        intro = True
        while intro and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    intro = False
            self.screen.fill(BLACK)
            text = self.font.render("Naciśnij SPACJĘ, aby zacząć grę", True, WHITE)
            text_rect = text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2))
            self.screen.blit(text, text_rect)
            pygame.display.update()
            self.clock.tick(FPS)

    def level_transition_screen(self):
        waiting = True
        seconds = self.elapsed_time / 1000
        text = self.font.render(f"Poziom {self.stage - 1} ukończony!", True, WHITE)
        instruction = self.font.render("Naciśnij SPACJĘ, aby kontynuować", True, WHITE)
        time_text = self.font.render(f"Czas: {seconds:6.2f}s", True, WHITE)

        text_rect = text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 40))
        time_rect = time_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2))
        instruction_rect = instruction.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 40))

        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False

            self.screen.fill(BLACK)
            self.screen.blit(text, text_rect)
            self.screen.blit(time_text, time_rect)
            self.screen.blit(instruction, instruction_rect)
            pygame.display.flip()
            self.clock.tick(FPS)

    def game_over_screen(self):

        self.lives -= 1

        if hasattr(self, "last_frame"):
            self.screen.blit(self.last_frame, (0, 0))
        else:
            self.screen.fill(BLACK)

        # Przyciemnienie tła
        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()  # <- potrzebne żeby tło było od razu widoczne

        self.clock.tick(FPS)

        if self.lives <= 0:
            # Ekran końcowy
            end_text = self.font.render("Straciłeś wszystkie życia!", True, WHITE)
            end_rect = end_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 20))

            space_text = self.font.render("Naciśnij SPACJĘ, aby wrócić do menu głównego", True, WHITE)
            space_rect = space_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + 20))

            waiting = True
            while waiting and self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        waiting = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.reset_game()
                        waiting = False

                self.screen.blit(end_text, end_rect)
                self.screen.blit(space_text, space_rect)
                pygame.display.flip()
                self.clock.tick(FPS)

        else:
            # Ekran restartu
            restart_text = self.font.render("Naciśnij R, aby spróbować ponownie", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2))

            waiting = True
            while waiting and self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        waiting = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        waiting = False

                self.screen.blit(restart_text, restart_rect)
                pygame.display.flip()
                self.clock.tick(FPS)


# start gry
g = Game()
while g.running:
    g.new()
    g.run()

pygame.quit()
