import pygame
import random
import math
import time
from collections import deque
import heapq
import tkinter as tk
from tkinter import ttk, messagebox


def start_simulation():
    global ROWS
    try:
        ROWS = int(rows_entry.get())
        
        if ROWS < 5 or ROWS > 100:
            raise ValueError("Keep rows between 5 and 100 for stability.")
            
        root.destroy()
        
    except ValueError as e:
        messagebox.showerror("Invalid Input", f"Please enter a valid number: {e}")

# --- UI Setup ---
root = tk.Tk()
root.title("Maze Configurator")
root.geometry("300x250")

# style = ttk.Style()
# style.configure("TLabel", font=("Arial", 10))
# style.configure("TButton", font=("Arial", 10, "bold"))

ttk.Label(root, text="Number of Rows:").pack(pady=(20, 5))
rows_entry = ttk.Entry(root)
rows_entry.insert(0, "20")  # Default value
rows_entry.pack(pady=5)

# ttk.Label(root, text="Select Generator:").pack(pady=(10, 5))
# algo_options = ["Recursive Backtracker (DFS)", "Prim's Algorithm", "A* Search", "Dijkstra"]
# algo_combo = ttk.Combobox(root, values=algo_options, state="readonly")
# algo_combo.current(0)  # Set default to first option
# algo_combo.pack(pady=5)

# ttk.Label(root, text="Select Solver:").pack(pady=(10, 5))
# algo_options = ["Recursive Backtracker (DFS)", "Prim's Algorithm", "A* Search", "Dijkstra"]
# algo_combo = ttk.Combobox(root, values=algo_options, state="readonly")
# algo_combo.current(0)  # Set default to first option
# algo_combo.pack(pady=5)

start_btn = ttk.Button(root, text="Generate Maze", command=start_simulation)
start_btn.pack(pady=30)

root.mainloop()


# ─── CONFIG ────────────────────────────────────────────────────────────────────
COLS, ROWS  = 30, 30
MARGIN      = 50
# Just use fullscreen
# WIDTH       = COLS * CELL + MARGIN * 2
# HEIGHT      = ROWS * CELL + MARGIN * 2 + 90
pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
display_info = pygame.display.Info()
WIDTH = display_info.current_w
HEIGHT = display_info.current_h - MARGIN * 2
CELL = (HEIGHT - 100) / ROWS

GEN_DELAY   = 0.008
SOLVE_DELAY = 0.012

# ─── PALETTE ───────────────────────────────────────────────────────────────────
BG        = (8,   10,  18)
WALL      = (210, 220, 255)
UNVISITED = (14,  18,  32)
START_COL = (60,  220, 130)
END_COL   = (220,  70, 100)
PATH_COL  = (255, 230,  80)
TEXT_COL  = (255, 255, 255)
ACCENT    = (255, 200,  50)
DIM       = (60,   70, 100)

GEN_WAVE_A  = (20,  40, 120)
GEN_WAVE_B  = (80, 200, 255)
SOL_WAVE_A  = (120,  20, 180)
SOL_WAVE_B  = (255, 100,  50)

# ─── WAVE COLOR ────────────────────────────────────────────────────────────────
def wave_color(step, total, ca, cb):
    """Map discovery order to a rippling gradient — the wave effect."""
    t = step / max(total, 1)
    t = (t + 0.15 * math.sin(t * math.pi * 6)) % 1.0
    t = max(0.0, min(1.0, t))
    return (
        int(ca[0] + (cb[0]-ca[0]) * t),
        int(ca[1] + (cb[1]-ca[1]) * t),
        int(ca[2] + (cb[2]-ca[2]) * t),
    )

# ─── CELL ──────────────────────────────────────────────────────────────────────
class Cell:
    def __init__(self, r, c):
        self.r, self.c = r, c
        self.walls      = [True, True, True, True]  # top right bottom left
        self.gen_step   = -1
        self.solve_step = -1

    def __lt__(self, other):
        return (self.r, self.c) < (other.r, other.c)

# ─── MAZE ──────────────────────────────────────────────────────────────────────
class Maze:
    def __init__(self):
        self.grid = [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)]

    def cell(self, r, c):
        if 0 <= r < ROWS and 0 <= c < COLS:
            return self.grid[r][c]
        return None

    def remove_wall(self, a, b):
        dr, dc = b.r - a.r, b.c - a.c
        if dr == -1: a.walls[0] = False; b.walls[2] = False
        if dc ==  1: a.walls[1] = False; b.walls[3] = False
        if dr ==  1: a.walls[2] = False; b.walls[0] = False
        if dc == -1: a.walls[3] = False; b.walls[1] = False

    def neighbors_open(self, cell):
        dirs = [(-1,0,0),(0,1,1),(1,0,2),(0,-1,3)]
        return [
            self.cell(cell.r+dr, cell.c+dc)
            for dr,dc,wi in dirs
            if not cell.walls[wi] and self.cell(cell.r+dr, cell.c+dc)
        ]

    def reset_solve(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.grid[r][c].solve_step = -1


# ══════════════════════════════════════════════════════════════════════════════
#  GENERATION ALGORITHMS
#  Protocol: generator, yields (r, c, step_count) each carved step.
#  Stamps cell.gen_step = step when a cell is first carved.
# ══════════════════════════════════════════════════════════════════════════════

def gen_recursive_backtracker(maze):
    """
    DFS backtracker. Digs deep corridors before backtracking.
    Wave look: a single snaking thread that slowly floods the grid.
    """
    step = 0
    stack = [maze.grid[0][0]]
    maze.grid[0][0].gen_step = step
    dirs = [(-1,0),(0,1),(1,0),(0,-1)]

    while stack:
        cur = stack[-1]
        nbrs = [maze.cell(cur.r+dr, cur.c+dc)
                for dr,dc in dirs
                if maze.cell(cur.r+dr, cur.c+dc)
                and maze.cell(cur.r+dr, cur.c+dc).gen_step == -1]
        if nbrs:
            nb = random.choice(nbrs)
            maze.remove_wall(cur, nb)
            step += 1
            nb.gen_step = step
            stack.append(nb)
            yield cur.r, cur.c, step
        else:
            stack.pop()
            if stack:
                yield stack[-1].r, stack[-1].c, step


def gen_prims(maze):
    """
    Randomised Prim's. Picks a random frontier edge each step.
    Wave look: blob expanding outward from origin — roughly circular wave.
    """
    step = 0
    maze.grid[0][0].gen_step = step
    frontier = []   # (parent, neighbor)
    dirs = [(-1,0),(0,1),(1,0),(0,-1)]

    def add_frontiers(cell):
        for dr,dc in dirs:
            nb = maze.cell(cell.r+dr, cell.c+dc)
            if nb and nb.gen_step == -1:
                frontier.append((cell, nb))

    add_frontiers(maze.grid[0][0])

    while frontier:
        idx = random.randrange(len(frontier))
        parent, nb = frontier[idx]
        frontier.pop(idx)
        if nb.gen_step != -1:
            continue
        maze.remove_wall(parent, nb)
        step += 1
        nb.gen_step = step
        add_frontiers(nb)
        yield nb.r, nb.c, step


def gen_kruskals(maze):
    """
    Randomised Kruskal's. Shuffles all edges, merges sets that aren't connected.
    Wave look: scattered sparks across the whole grid that gradually merge.
    """
    step = 0
    parent = {(r,c): (r,c) for r in range(ROWS) for c in range(COLS)}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb: return False
        parent[ra] = rb
        return True

    edges = []
    for r in range(ROWS):
        for c in range(COLS):
            if r+1 < ROWS: edges.append(((r,c),(r+1,c)))
            if c+1 < COLS: edges.append(((r,c),(r,c+1)))
    random.shuffle(edges)

    for (r1,c1),(r2,c2) in edges:
        if union((r1,c1),(r2,c2)):
            a = maze.grid[r1][c1]; b = maze.grid[r2][c2]
            maze.remove_wall(a, b)
            if a.gen_step == -1: a.gen_step = step
            if b.gen_step == -1: b.gen_step = step
            step += 1
            yield r1, c1, step


def gen_wilsons(maze):
    """
    Wilson's algorithm. Loop-erased random walks into the growing tree.
    Wave look: starts slow (few tree cells), then accelerates — unique growth pattern.
    """
    step = 0
    maze.grid[ROWS//2][COLS//2].gen_step = step
    unvisited = {(r,c) for r in range(ROWS) for c in range(COLS)
                 if (r,c) != (ROWS//2, COLS//2)}
    dirs = [(-1,0),(0,1),(1,0),(0,-1)]

    while unvisited:
        start = random.choice(list(unvisited))
        path, path_idx = [start], {start: 0}

        while path[-1] in unvisited and maze.grid[path[-1][0]][path[-1][1]].gen_step == -1:
            r, c = path[-1]
            dr, dc = random.choice(dirs)
            nr, nc = r+dr, c+dc
            if not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue
            pos = (nr, nc)
            if pos in path_idx:
                path = path[:path_idx[pos]+1]
                path_idx = {p: i for i,p in enumerate(path)}
            else:
                path_idx[pos] = len(path)
                path.append(pos)

        for i in range(len(path)-1):
            r1,c1 = path[i]; r2,c2 = path[i+1]
            a, b = maze.grid[r1][c1], maze.grid[r2][c2]
            maze.remove_wall(a, b)
            if a.gen_step == -1: a.gen_step = step; step += 1
            if b.gen_step == -1: b.gen_step = step; step += 1
            unvisited.discard((r1,c1)); unvisited.discard((r2,c2))
            yield r1, c1, step


# ══════════════════════════════════════════════════════════════════════════════
#  SOLVING ALGORITHMS
#  Protocol: generator, yields (frontier_set, came_from, solution_or_None, step)
#  Stamps cell.solve_step = step when first visited.
# ══════════════════════════════════════════════════════════════════════════════

def _reconstruct(came_from, end):
    path, node = [], (end.r, end.c)
    while node is not None:
        path.append(node); node = came_from.get(node)
    path.reverse()
    return set(path)


def solve_bfs(maze):
    """
    BFS. Explores every cell at distance d before distance d+1.
    Wave look: perfect concentric rings expanding from the start.
    """
    step = 0
    start = maze.grid[0][0]; end = maze.grid[ROWS-1][COLS-1]
    queue = deque([start])
    came_from = {(start.r,start.c): None}
    start.solve_step = step

    while queue:
        cur = queue.popleft()
        if cur == end: break
        for nb in maze.neighbors_open(cur):
            k = (nb.r, nb.c)
            if k not in came_from:
                step += 1; nb.solve_step = step
                came_from[k] = (cur.r, cur.c)
                queue.append(nb)
        yield {(c.r,c.c) for c in queue}, came_from, None, step

    yield set(), came_from, _reconstruct(came_from, end), step


def solve_dfs(maze):
    """
    DFS. Dives as deep as possible before backtracking.
    Wave look: snaking thread, may take a very winding route to the end.
    """
    step = 0
    start = maze.grid[0][0]; end = maze.grid[ROWS-1][COLS-1]
    stack = [start]
    came_from = {(start.r,start.c): None}
    start.solve_step = step

    while stack:
        cur = stack.pop()
        if cur == end: break
        for nb in maze.neighbors_open(cur):
            k = (nb.r, nb.c)
            if k not in came_from:
                step += 1; nb.solve_step = step
                came_from[k] = (cur.r, cur.c)
                stack.append(nb)
        yield {(c.r,c.c) for c in stack}, came_from, None, step

    yield set(), came_from, _reconstruct(came_from, end), step


def solve_astar(maze):
    """
    A* with Manhattan distance heuristic.
    Wave look: biased toward the goal — teardrop/directed wave rather than circular.
    """
    step = 0
    start = maze.grid[0][0]; end = maze.grid[ROWS-1][COLS-1]
    h = lambda cell: abs(cell.r-end.r) + abs(cell.c-end.c)
    open_set = [(h(start), 0, start)]
    came_from = {(start.r,start.c): None}
    g_score   = {(start.r,start.c): 0}
    start.solve_step = step

    while open_set:
        _, g, cur = heapq.heappop(open_set)
        if cur == end: break
        if g > g_score.get((cur.r,cur.c), float('inf')): continue
        for nb in maze.neighbors_open(cur):
            k = (nb.r, nb.c); ng = g+1
            if ng < g_score.get(k, float('inf')):
                g_score[k] = ng
                if k not in came_from:
                    step += 1; nb.solve_step = step
                came_from[k] = (cur.r,cur.c)
                heapq.heappush(open_set, (ng+h(nb), ng, nb))
        yield {(f[2].r,f[2].c) for f in open_set}, came_from, None, step

    yield set(), came_from, _reconstruct(came_from, end), step


def solve_dijkstra(maze):
    """
    Dijkstra's. Uniform-cost expansion — like BFS on unit-weight graphs.
    Wave look: diamond/circular, expands purely by true distance from start.
    """
    step = 0
    start = maze.grid[0][0]; end = maze.grid[ROWS-1][COLS-1]
    dist = {(start.r,start.c): 0}
    came_from = {(start.r,start.c): None}
    pq = [(0, start)]
    start.solve_step = step

    while pq:
        d, cur = heapq.heappop(pq)
        if cur == end: break
        if d > dist.get((cur.r,cur.c), float('inf')): continue
        for nb in maze.neighbors_open(cur):
            k = (nb.r, nb.c); nd = d+1
            if nd < dist.get(k, float('inf')):
                dist[k] = nd
                if k not in came_from:
                    step += 1; nb.solve_step = step
                came_from[k] = (cur.r,cur.c)
                heapq.heappush(pq, (nd, nb))
        yield {(f[1].r,f[1].c) for f in pq}, came_from, None, step

    yield set(), came_from, _reconstruct(came_from, end), step


GEN_ALGOS = [
    ("Recursive Backtracker", gen_recursive_backtracker),
    ("Prim's",                gen_prims),
    ("Kruskal's",             gen_kruskals),
    ("Wilson's",              gen_wilsons),
]
SOLVE_ALGOS = [
    ("BFS  (shortest)",  solve_bfs),
    ("DFS  (first)",     solve_dfs),
    ("A*   (heuristic)", solve_astar),
    ("Dijkstra",         solve_dijkstra),
]


# ─── DRAW ──────────────────────────────────────────────────────────────────────
def cell_rect(r, c):
    return pygame.Rect(MARGIN + c*CELL, MARGIN + r*CELL, CELL, CELL)

def draw_maze(surface, maze, gen_current=None, frontier=None, solution=None,
              gen_total=1, solve_total=1):
    surface.fill(BG)

    for r in range(ROWS):
        for c in range(COLS):
            cell = maze.grid[r][c]
            rect = cell_rect(r, c)

            if solution and (r,c) in solution:
                color = PATH_COL
            elif frontier and (r,c) in frontier:
                color = (180, 120, 255)
            elif cell.solve_step >= 0:
                color = wave_color(cell.solve_step, solve_total, SOL_WAVE_A, SOL_WAVE_B)
            elif cell.gen_step >= 0:
                color = wave_color(cell.gen_step, gen_total, GEN_WAVE_A, GEN_WAVE_B)
            else:
                color = UNVISITED

            pygame.draw.rect(surface, color, rect)

            if gen_current and (r,c) == gen_current:
                pygame.draw.rect(surface, ACCENT, rect)

    for r in range(ROWS):
        for c in range(COLS):
            cell = maze.grid[r][c]
            x = MARGIN + c*CELL; y = MARGIN + r*CELL; lw = 2
            if cell.walls[0]: pygame.draw.line(surface, WALL, (x,y),      (x+CELL,y),      lw)
            if cell.walls[1]: pygame.draw.line(surface, WALL, (x+CELL,y), (x+CELL,y+CELL), lw)
            if cell.walls[2]: pygame.draw.line(surface, WALL, (x,y+CELL), (x+CELL,y+CELL), lw)
            if cell.walls[3]: pygame.draw.line(surface, WALL, (x,y),      (x,y+CELL),       lw)

    pad = 7
    pygame.draw.rect(surface, START_COL, cell_rect(0,0).inflate(-pad,-pad),           border_radius=3)
    pygame.draw.rect(surface, END_COL,   cell_rect(ROWS-1,COLS-1).inflate(-pad,-pad), border_radius=3)


def draw_ui(surface, font, sfont, phase, stat, gen_name, solve_name):
    t = font.render("MAZE  SOLVER", True, ACCENT)
    surface.blit(t, (WIDTH//2 - t.get_width()//2, 12))

    bar_y = MARGIN + ROWS*CELL + 12
    surface.blit(sfont.render(phase, True, TEXT_COL), (MARGIN, bar_y))
    if stat:
        s = sfont.render(stat, True, ACCENT)
        surface.blit(s, (WIDTH - MARGIN - s.get_width(), bar_y))

    ly = bar_y + 22
    surface.blit(sfont.render(f"GEN: {gen_name}",     True, DIM), (MARGIN,    ly))
    surface.blit(sfont.render(f"SOLVE: {solve_name}", True, DIM), (WIDTH//2,  ly))
    # surface.blit(hint, (WIDTH//2 - hint.get_width()//2, ly+20))


def draw_menu(surface, font, sfont, gi, si):
    surface.fill(BG)
    title = font.render("SELECT ALGORITHMS", True, ACCENT)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 28))

    y = 76
    surface.blit(sfont.render("GENERATION  (keys 1-4)", True, TEXT_COL), (MARGIN, y)); y += 22
    for i,(name,_) in enumerate(GEN_ALGOS):
        col = ACCENT if i==gi else DIM
        surface.blit(sfont.render(f"  {'>' if i==gi else ' '} {i+1}. {name}", True, col), (MARGIN, y)); y += 19
    y += 12
    surface.blit(sfont.render("SOLVING  (keys 5-8)", True, TEXT_COL), (MARGIN, y)); y += 22
    for i,(name,_) in enumerate(SOLVE_ALGOS):
        col = ACCENT if i==si else DIM
        surface.blit(sfont.render(f"  {'>' if i==si else ' '} {i+5}. {name}", True, col), (MARGIN, y)); y += 19
    y += 18
    surface.blit(sfont.render("ENTER or SPACE to start", True, TEXT_COL), (MARGIN, y))
    y+= 25
    surface.blit(sfont.render("E to exit", True, TEXT_COL), (MARGIN, y))
    pygame.display.flip()


# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    pygame.display.set_caption("Maze Solver")
    clock = pygame.time.Clock()

    try:
        font  = pygame.font.SysFont("Arial", 27, bold=True)
        sfont = pygame.font.SysFont("Arial", 20)
    except:
        font  = pygame.font.SysFont(None, 18)
        sfont = pygame.font.SysFont(None, 13)

    gi, si = 0, 0

    # Menu
    in_menu = True
    while in_menu:
        draw_menu(screen, font, sfont, gi, si)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e: 
                    pygame.quit()
                    exit()
                if event.key in (pygame.K_RETURN, pygame.K_SPACE): in_menu = False
                elif event.key == pygame.K_1: gi = 0
                elif event.key == pygame.K_2: gi = 1
                elif event.key == pygame.K_3: gi = 2
                elif event.key == pygame.K_4: gi = 3
                elif event.key == pygame.K_5: si = 0
                elif event.key == pygame.K_6: si = 1
                elif event.key == pygame.K_7: si = 2
                elif event.key == pygame.K_8: si = 3

    def run(gi, si):
        maze = Maze()
        gname = GEN_ALGOS[gi][0]; sname = SOLVE_ALGOS[si][0]
        gen_algo = GEN_ALGOS[gi][1](maze)
        gen_cur = (0,0); gen_total = 1; last = time.time()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e: 
                        pygame.quit()
                        exit()
                    if event.key == pygame.K_r: return (gi, si)
                    if event.key == pygame.K_g: return ((gi+1)%len(GEN_ALGOS), si)
                    if event.key == pygame.K_s: return (gi, (si+1)%len(SOLVE_ALGOS))
            now = time.time()
            if now - last >= GEN_DELAY:
                try:
                    r, c, gen_total = next(gen_algo)
                    gen_cur = (r,c); last = now
                except StopIteration:
                    gen_cur = None; break
            draw_maze(screen, maze, gen_current=gen_cur, gen_total=gen_total)
            draw_ui(screen, font, sfont, f"GENERATING — {gname}", f"step {gen_total}", gname, sname)
            pygame.display.flip(); clock.tick(120)

        pygame.time.wait(400)
        maze.reset_solve()
        solve_algo = SOLVE_ALGOS[si][1](maze)
        frontier = set(); solution = None; solve_total = 1; last = time.time()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e: 
                        pygame.quit()
                        exit()
                    elif event.key == pygame.K_r: return (gi, si)
                    elif event.key == pygame.K_g: return ((gi+1)%len(GEN_ALGOS), si)
                    elif event.key == pygame.K_s: return (gi, (si+1)%len(SOLVE_ALGOS))
            now = time.time()
            if solution is None and now - last >= SOLVE_DELAY:
                try:
                    frontier, _, sol, solve_total = next(solve_algo)
                    if sol is not None: solution = sol
                    last = now
                except StopIteration:
                    pass
            draw_maze(screen, maze, frontier=frontier, solution=solution,
                      gen_total=gen_total, solve_total=solve_total)
            if solution:
                draw_ui(screen, font, sfont, f"SOLVED — path {len(solution)} cells  [R] restart",
                        None, gname, sname)
            else:
                draw_ui(screen, font, sfont, f"SOLVING — {sname}", f"step {solve_total}", gname, sname)
            pygame.display.flip(); clock.tick(120)

    result = (gi, si)
    while result: result = run(*result)
    pygame.quit()

if __name__ == "__main__":
    main()