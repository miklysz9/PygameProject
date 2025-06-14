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
        self.font_path = "./images/font.otf"
        self.font = pygame.font.Font(self.font_path, 22)
        self.timer_font = pygame.font.Font(self.font_path, 22)
        self.reset_game()



    def reset_game(self):
        self.stage = 1
        self.lives = 3
        self.score = 0
        self.collected_coins = []  # Reset zebranych monet
        self.main_menu()

    def main_menu(self):
        menu_options = ["Start", "Ustawienia", "Wyjście"]
        selected_option = 0
        menu_running = True

        while menu_running and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_SPACE:
                        if selected_option == 0:  # Start
                            menu_running = False
                        elif selected_option == 1:  # Ustawienia
                            self.settings_menu()
                        elif selected_option == 2:  # Wyjście
                            menu_running = False
                            self.running = False

            self.screen.fill(BLACK)
            for i, option in enumerate(menu_options):
                color = WHITE if i == selected_option else (100, 100, 100)
                text = self.font.render(option, True, color)
                text_rect = text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + i * 40))
                self.screen.blit(text, text_rect)

            pygame.display.update()
            self.clock.tick(FPS)

    def settings_menu(self):
        global WIN_WIDTH, WIN_HEIGHT  # Deklaracja zmiennych globalnych
        resolutions = [(640, 480), (800, 600), (1024, 768)]
        selected_resolution = 0
        settings_running = True

        while settings_running and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    settings_running = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_resolution = (selected_resolution - 1) % len(resolutions)
                    elif event.key == pygame.K_DOWN:
                        selected_resolution = (selected_resolution + 1) % len(resolutions)
                    elif event.key == pygame.K_SPACE:
                        WIN_WIDTH, WIN_HEIGHT = resolutions[selected_resolution]
                        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
                        settings_running = False

            self.screen.fill(BLACK)
            for i, res in enumerate(resolutions):
                color = WHITE if i == selected_resolution else (100, 100, 100)
                text = self.font.render(f"{res[0]}x{res[1]}", True, color)
                text_rect = text.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + i * 40))
                self.screen.blit(text, text_rect)

            pygame.display.update()
            self.clock.tick(FPS)

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
                elif tile == "C":
                    # Tworzenie monety tylko, jeśli nie została zebrana
                    if (j, i) not in self.collected_coins:
                        Coin(self, j, i)

    def new(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.door = pygame.sprite.LayeredUpdates()
        self.coins = pygame.sprite.LayeredUpdates()
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
                    self.reset_game()  # Reset wszystkiego
                else:
                    self.new()  # Zachowanie punktów i monet

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
        self.elapsed_time = pygame.time.get_ticks() - self.level_start_time

    def draw(self):
        self.screen.fill(BLACK)
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        # UI: Timer, życie i punkty
        label_text = self.font.render("Czas:", True, BLACK)
        seconds = self.elapsed_time / 1000
        number_text = self.timer_font.render(f"{seconds:06.2f}", True, BLACK)
        unit_text = self.font.render("s", True, BLACK)

        self.screen.blit(label_text, (10, 10))
        self.screen.blit(number_text, (10 + label_text.get_width() + 10, 10))
        self.screen.blit(unit_text, (10 + label_text.get_width() + number_text.get_width() + 15, 10))
        lives_text = self.font.render(f"Życia: {self.lives}", True, BLACK)
        self.screen.blit(lives_text, (10, 40))

        score_text = self.font.render(f"Punkty: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 70))

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

        overlay = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()

        self.clock.tick(FPS)

        if self.lives <= 0:
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

# Start gry
g = Game()
while g.running:
    g.new()
    g.run()

pygame.quit()