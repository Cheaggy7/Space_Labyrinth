import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from player import Player
from tile_map import TileMap

class Window:
    def __init__(self, width=1200, height=800, colour=(30, 30, 255)):
        self.window_width = width
        self.window_height = height
        self.window_colour = colour
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Spce Labyrinth")

    def set_size(self, width, height):
        self.window_width = width
        self.window_height = height
        self.window = pygame.display.set_mode((self.window_width, self.window_height))

    def set_colour(self, colour):
        self.window_colour = colour


class Game:
    def __init__(self, path):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.game_window = Window()
        # self.bg = (10, 10, 10)

        # Map laden
        self.map = TileMap(path)

        # Player anlegen (Startpunkt aus Map, fallback wenn None)
        start = self.map.player_start or pygame.Vector2(100, 100)
        self.player = Player(x=int(start.x), y=int(start.y))

        self.run()

    def run(self):
        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    running = False

            dt = self.clock.tick(60) / 1000.0
            self.player.handle_input(dt)
            self.player.update(dt, self.map,self.game_window.window.get_rect())

            # Kamera folgt Spieler (zentriert)
            win_w, win_h = self.game_window.window.get_size()
            camera = pygame.Vector2(self.player.pos.x - win_w/2, self.player.pos.y - win_h/2)
            # Kamera an Weltgrenzen clampen (damit kein „schwarzer Rand“)
            camera.x = max(0, min(self.map.pixel_width  - win_w, camera.x))
            camera.y = max(0, min(self.map.pixel_height - win_h, camera.y))

            # Render
            self.game_window.window.fill(self.game_window.window_colour)
            self.map.draw(self.game_window.window, camera)
            # Player mit Offset zeichnen
            self.player.draw_with_camera(self.game_window.window, camera)
            pygame.display.flip()

        pygame.quit()