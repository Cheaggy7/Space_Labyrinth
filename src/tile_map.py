import pygame
from pathlib import Path

TILE_SIZE = 500

TILES = {
    "#": {"colour": (30, 70, 255), "solid": True},   # Wand (grün, z. B. Labyrinth)
    ".": {"colour": (0, 0, 128),  "solid": False},  # Boden
    "P": {"colour": (255, 10, 128),  "solid": False},  # Boden + Spielerstart
}

class TileMap:
    def __init__(self, map_path: str):
        lines = Path(map_path).read_text(encoding="utf-8").splitlines()
        self.grid = [list(row) for row in lines]
        self.rows = len(self.grid)
        self.cols = max(len(r) for r in self.grid) if self.rows else 0

        # kürzere Zeilen rechts mit Boden auffüllen
        for r in self.grid:
            if len(r) < self.cols:
                r += list("." * (self.cols - len(r)))

        self.pixel_width  = self.cols * TILE_SIZE
        self.pixel_height = self.rows * TILE_SIZE

        # Spielerstart suchen (optional)
        self.player_start = None
        for y, row in enumerate(self.grid):
            for x, ch in enumerate(row):
                if ch == "P":
                    self.player_start = pygame.Vector2(
                        x * TILE_SIZE + TILE_SIZE // 2,
                        y * TILE_SIZE + TILE_SIZE // 2
                    )

    def is_solid_at(self, gx: int, gy: int) -> bool:
        # außerhalb der Karte: als Wand behandeln
        if gy < 0 or gy >= self.rows:
            return True
        row = self.grid[gy]
        if gx < 0 or gx >= len(row):
            return True
        ch = row[gx]
        return TILES.get(ch, {"solid": False})["solid"]

    def get_nearby_solid_rects(self, rect: pygame.Rect) -> list[pygame.Rect]:
        first_row = max(0, rect.top // TILE_SIZE - 1)
        last_row = min(self.rows - 1, (rect.bottom - 1) // TILE_SIZE + 1)

        first_col_base = rect.left // TILE_SIZE - 1
        last_col_base = (rect.right - 1) // TILE_SIZE + 1

        solids = []
        for gy in range(first_row, last_row + 1):
            row_len = len(self.grid[gy])  # pro Zeile clampen!
            first_col = max(0, first_col_base)
            last_col = min(row_len - 1, last_col_base)
            for gx in range(first_col, last_col + 1):
                if self.is_solid_at(gx, gy):
                    solids.append(pygame.Rect(gx * TILE_SIZE, gy * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return solids

    def draw(self, surface: pygame.Surface, camera_offset: pygame.Vector2):
        # Sichtbereich bestimmen (optional für Speed – hier simpel)
        w, h = surface.get_size()
        first_col = max(0, int(camera_offset.x // TILE_SIZE))
        first_row = max(0, int(camera_offset.y // TILE_SIZE))
        last_col  = min(self.cols, first_col + (w // TILE_SIZE) + 3)
        last_row  = min(self.rows, first_row + (h // TILE_SIZE) + 3)

        for gy in range(first_row, last_row):
            row = self.grid[gy]
            for gx in range(first_col, last_col):
                ch = row[gx] if gx < len(row) else "."
                data = TILES.get(ch, TILES["."])
                x = gx * TILE_SIZE - camera_offset.x
                y = gy * TILE_SIZE - camera_offset.y
                pygame.draw.rect(surface, data["colour"], (x, y, TILE_SIZE, TILE_SIZE))
