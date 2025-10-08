import random
from collections import deque

WALL = "#"
FLOOR = "."
START = "P"
GOAL = "Z"

def generate_map(width=61, height=41, seed=None,
                 corridor_bias=0.0,     # -1.0: viele Abzweige | +1.0: lange Korridore
                 loop_factor=0.05,      # 0..1 wie viele zusätzliche Schlaufen
                 deadend_trim=0,        # 0..n Sackgassen kürzen (glatter, weniger dead ends)
                 room_attempts=0,       # Anzahl einzubauender Räume
                 room_minmax=(3,7),     # Raumgrößen (odd empfohlen)
                 min_path_ratio=0.35):  # Mindestpfad (P->Z) relativ zur Karte
    """
    width/height sollten ungerade sein (klassische Maze-Zellen=2x2-1).
    """
    if seed is not None:
        random.seed(seed)

    # --- Raster initialisieren: alles Wand
    grid = [[WALL for _ in range(width)] for _ in range(height)]

    # Helper: Nachbarn in 2-Schritten (Maze-Zellen)
    def in_bounds(y, x): return 0 <= y < height and 0 <= x < width
    def neighbors2(y, x):
        for dy, dx in ((-2,0),(2,0),(0,-2),(0,2)):
            ny, nx = y+dy, x+dx
            if in_bounds(ny, nx):
                yield ny, nx, dy, dx

    # --- Startzelle auf ungeraden Koordinaten
    sy = random.randrange(1, height, 2)
    sx = random.randrange(1, width,  2)
    grid[sy][sx] = FLOOR

    # --- DFS-Backtracker mit Korridor-Bias
    stack = [(sy, sx)]
    while stack:
        y, x = stack[-1]
        nbrs = []
        for ny, nx, dy, dx in neighbors2(y, x):
            if grid[ny][nx] == WALL:
                nbrs.append((ny, nx, dy, dx))
        if not nbrs:
            stack.pop()
            continue
        # Bias: sortiere Nachbarn so, dass Vorzugsrichtung öfter genommen wird
        # (hier simpel: zufällig mischen und optional neu sortieren)
        random.shuffle(nbrs)
        if corridor_bias != 0:
            # versuche, "Richtung beibehalten" zu belohnen: letzter Schritt = stack[-2]
            if len(stack) >= 2:
                py, px = stack[-2]
                last_dir = (y-py, x-px)
                def score(n):
                    dy, dx = n[2], n[3]
                    return (dy, dx) == last_dir
                nbrs.sort(key=lambda n: score(n), reverse=corridor_bias>0)
        ny, nx, dy, dx = nbrs[0]
        # Wand zwischen Zellen öffnen
        grid[y + dy//2][x + dx//2] = FLOOR
        grid[ny][nx] = FLOOR
        stack.append((ny, nx))

    # --- Räume einstanzen
    for _ in range(room_attempts):
        rw = random.randrange(room_minmax[0]|1, room_minmax[1]|1, 2)  # odd
        rh = random.randrange(room_minmax[0]|1, room_minmax[1]|1, 2)
        ry = random.randrange(1, height - rh - 1, 2)
        rx = random.randrange(1, width  - rw - 1, 2)
        for yy in range(ry, ry+rh):
            for xx in range(rx, rx+rw):
                grid[yy][xx] = FLOOR
        # einfache Anbindung: Tür in eine Wand stanzen
        for _try in range(4):
            side = random.choice(["N","S","W","E"])
            if side == "N":
                y, x = ry-1, random.randrange(rx, rx+rw)
            elif side == "S":
                y, x = ry+rh, random.randrange(rx, rx+rw)
            elif side == "W":
                y, x = random.randrange(ry, ry+rh), rx-1
            else:
                y, x = random.randrange(ry, ry+rh), rx+rw
            if 0 < y < height-1 and 0 < x < width-1:
                grid[y][x] = FLOOR

    # --- Loops hinzufügen (einige Wände entfernen)
    wall_cells = [(y,x) for y in range(1,height-1) for x in range(1,width-1) if grid[y][x]==WALL and (y%2!=x%2)]
    random.shuffle(wall_cells)
    to_open = int(loop_factor * len(wall_cells))
    for y, x in wall_cells[:to_open]:
        grid[y][x] = FLOOR

    # --- Sackgassen kürzen
    def count_floor_neighbors(y,x):
        c=0
        for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
            if in_bounds(y+dy,x+dx) and grid[y+dy][x+dx]==FLOOR: c+=1
        return c
    for _ in range(deadend_trim):
        changed = False
        for y in range(1,height-1):
            for x in range(1,width-1):
                if grid[y][x]==FLOOR and count_floor_neighbors(y,x)<=1:
                    grid[y][x]=WALL; changed=True
        if not changed:
            break

    # --- Start & Ziel platzieren: maximaler Abstand (ungefähr)
    floors = [(y,x) for y in range(height) for x in range(width) if grid[y][x]==FLOOR]
    P = random.choice(floors)
    # BFS von P, weiteste Zelle als Z
    def bfs_far(src):
        q=deque([src]); dist={src:0}
        while q:
            cy,cx=q.popleft()
            for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
                ny,nx=cy+dy,cx+dx
                if in_bounds(ny,nx) and grid[ny][nx]==FLOOR and (ny,nx) not in dist:
                    dist[(ny,nx)]=dist[(cy,cx)]+1; q.append((ny,nx))
        far = max(dist, key=dist.get)
        return far, dist[far], dist
    Z, d, distmap = bfs_far(P)

    # Mindestpfad prüfen – ggf. erneut Loops trimmen oder Wände öffnen
    needed = int(min_path_ratio * (width*height))
    if d < needed:
        # Heuristik: entferne gezielt einige Wände entlang des Gradienten
        for _ in range(500):
            y, x = random.choice(wall_cells)
            # wenn Wand zwei Böden trennt, öffne
            nbs = [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]
            if sum(1 for ny,nx in nbs if in_bounds(ny,nx) and grid[ny][nx]==FLOOR)>=2:
                grid[y][x]=FLOOR

        # neu bewerten
        Z, d, _ = bfs_far(P)

    # Markieren
    py, px = P
    zy, zx = Z
    grid[py][px] = START
    grid[zy][zx] = GOAL
    return ["".join(row) for row in grid]

def save_map(lines, path):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line+"\n")

# Presets für Schwierigkeit
PRESETS = {
    "easy":  dict(corridor_bias= 0.7, loop_factor=0.15, deadend_trim=0, room_attempts=3, room_minmax=(5,9),  min_path_ratio=0.20),
    "normal":dict(corridor_bias= 0.3, loop_factor=0.08, deadend_trim=1, room_attempts=2, room_minmax=(3,7),  min_path_ratio=0.30),
    "hard":  dict(corridor_bias=-0.2, loop_factor=0.02, deadend_trim=3, room_attempts=1, room_minmax=(3,5),  min_path_ratio=0.40),
}

def generate_preset(width=61, height=41, difficulty="normal", seed=None):
    return generate_map(width, height, seed=seed, **PRESETS[difficulty])
