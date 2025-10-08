# Example file showing a basic pygame "game loop"
import pygame
from base import Game
from map_generator import generate_preset, save_map

if __name__ == "__main__":
    map_path = "../maps/level1.1.txt"
    lines = generate_preset(width=24, height=24, difficulty="normal", seed=49)
    save_map(lines, map_path)
    Game(map_path)




