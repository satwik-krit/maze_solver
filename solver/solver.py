from collections import deque
OPPOSITE = {
    'top': 'bottom',
    'bottom': 'top',
    'left': 'right',
    'right': 'left'
}

# Direction to (row_change, col_change)
DIRECTIONS = {
    'top':    (-1, 0),
    'bottom': (+1, 0),
    'left':   (0, -1),
    'right':  (0, +1)
}

"""
DFS
BFS
A*
Dijkstra's
"""

def get_accessible_neighbours(cell, grid):
    neighbours = list()
    rows = len(grid)
    cols = len(grid[0])

    for dir, (dy, dx) in DIRECTIONS.items():
        ny, nx = cell.row + dy, cell.col + dx

        if 0 <= ny < rows and 0 <= nx < cols:
            if not cell.walls[dir]:
                neighbours.append(grid[ny][nx])

    return neighbours

def solve_dfs(grid, start, end):
    marked = [[False] * len(grid) for _ in range(len(grid[0]))]
    
    # Store the nodes to be visited next along witht the path to be traversed.
    stack = [(start, [start])]

    while len(stack) > 0:
        v, path = stack.pop()

        if marked[v.row][v.col]:
            continue

        if v == end:
            return path

        marked[v.row][v.col] = True

        for w in get_accessible_neighbours(v, grid):
            if not marked[w.row][w.col]:
                stack.append((w, path+[w]))

    return None

def solve_bfs(grid, start, end):
    queue = deque((start, [start]))
    marked = [[False] * len(grid) for _ in range(len(grid[0]))]

    while queue:
        node, path = queue.popleft()

        if not marked[node.row][node.col]:
            # Process node
            if node == end:
                return path
            marked[node.row][node.col] = True

            for w in get_accessible_neighbours(node, grid):
                if not marked[w.row][w.col]:
                    queue.addright(w, path.append(w))

    return None


def solve_astar(grid):
    pass

# Basically the same as BFS, since we don't have any weights on our maze.
def solve_dijkstra(grid):
    pass
