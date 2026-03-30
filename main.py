from solver import solver
from cell import Cell

def create_test_grid():
    # Create 5x5 grid with all walls intact first
    grid = [[Cell(r, c) for c in range(5)] for r in range(5)]

    # Helper to remove wall between two cells
    def open_wall(r1, c1, r2, c2):
        if r2 == r1 - 1:  # neighbor is above
            grid[r1][c1].walls['top'] = False
            grid[r2][c2].walls['bottom'] = False
        elif r2 == r1 + 1:  # neighbor is below
            grid[r1][c1].walls['bottom'] = False
            grid[r2][c2].walls['top'] = False
        elif c2 == c1 + 1:  # neighbor is right
            grid[r1][c1].walls['right'] = False
            grid[r2][c2].walls['left'] = False
        elif c2 == c1 - 1:  # neighbor is left
            grid[r1][c1].walls['left'] = False
            grid[r2][c2].walls['right'] = False

    # Row 0 connections
    open_wall(0, 0, 0, 1)
    open_wall(0, 1, 0, 2)
    open_wall(0, 3, 0, 4)

    # Row 0 to Row 1
    open_wall(0, 0, 1, 0)
    open_wall(0, 2, 1, 2)
    open_wall(0, 4, 1, 4)

    # Row 1 connections
    open_wall(1, 0, 1, 1)
    open_wall(1, 2, 1, 3)
    open_wall(1, 3, 1, 4)

    # Row 1 to Row 2
    open_wall(1, 1, 2, 1)
    open_wall(1, 2, 2, 2)
    open_wall(1, 4, 2, 4)

    # Row 2 connections
    open_wall(2, 0, 2, 1)
    open_wall(2, 2, 2, 3)

    # Row 2 to Row 3
    open_wall(2, 0, 3, 0)
    open_wall(2, 3, 3, 3)
    open_wall(2, 4, 3, 4)

    # Row 3 connections
    open_wall(3, 1, 3, 2)
    open_wall(3, 3, 3, 4)

    # Row 3 to Row 4
    open_wall(3, 0, 4, 0)
    open_wall(3, 1, 4, 1)
    open_wall(3, 3, 4, 3)

    # Row 4 connections
    open_wall(4, 0, 4, 1)
    open_wall(4, 1, 4, 2)
    open_wall(4, 2, 4, 3)
    open_wall(4, 3, 4, 4)

    # Entry and exit
    grid[0][0].walls['top'] = False       # Entry at top-left
    grid[4][4].walls['bottom'] = False    # Exit at bottom-right

    return grid

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

grid = create_test_grid()

start = grid[0][0]
end   = grid[4][4]
# Check walls of start cell
print("Start cell walls:", grid[0][0].walls)

# Check neighbours of start cell
neighbours = solver.get_accessible_neighbours(grid[0][0], grid)
print("Neighbours:", [(n.row, n.col) for n in neighbours])
# Plug in whichever solver you've written
path = solver.solve_dfs(grid, start, end)
if path:
    print("Path found!")
    for cell in path:
        print(f"  → ({cell.row}, {cell.col})")
else:
    print("No solution found.")
