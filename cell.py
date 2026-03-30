class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.visited = False
        self.walls = {
            'top': True,
            'right': True,
            'bottom': True,
            'left': True
        }

    def __str__(self):
        return f"Row: {self.row} Col: {self.col}"
        
    def remove_walls(current, next_cell):
        dx = current.col - next_cell.col
        if dx == 1:
            current.walls['left'] = False
            next_cell.walls['right'] = False
        elif dx == -1:
            current.walls['right'] = False
            next_cell.walls['left'] = False
    
        dy = current.row - next_cell.row
        if dy == 1:
            current.walls['top'] = False
            next_cell.walls['bottom'] = False
        elif dy == -1:
            current.walls['bottom'] = False
            next_cell.walls['top'] = False

        ##as the cell class present here is a binary class, and the walls are shared by both the adjacent and so when updating the 
        ##walls to be reoved the method must calculate which direction walls are to be removed from each cell
        #dx and dy calculates that in a directional basis

    rows,cols = 10,10

    grid = [[Cell(r,c) for c in range(cols)] for r in range(rows)] #a list comprehension is used to make a 2d grid without nesting for loops and keeping it all in one line

    def get_neighbors(cell, grid):
        neighbors = []
        r,c = cell.row,cell.column
        for rc,dc in [(-1,0),(0,1),(1,0),(0,-1)]:
            nr,nc = dr+r,dr+c
            if 0<= nr < len(grid) and 0 <= nc < len(grid[0]):
                neighbors.append(grid[nr,nc])
        return neighbors

    def get_unvisited_neighbors(cell, grid):
        neighbors = []
    
        # Grid dimensions
        rows = len(grid)
        cols = len(grid[0])
    
        r, c = cell.row, cell.col

    #using the input cell we check for neighbors one coordinate space away from the original cell
        top    = grid[r - 1][c] if r > 0 else None
        right  = grid[r][c + 1] if c < cols - 1 else None
        bottom = grid[r + 1][c] if r < rows - 1 else None
        left   = grid[r][c - 1] if c > 0 else None

    #check for wether each directional cell exists and add them after doing so based on if visited or not, if visited then not added
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)

        return neighbors

    def get_visited_neighbors(cell, grid):
        neighbors = []
        r, c = cell.row, cell.col
        rows, cols = len(grid), len(grid[0])
    
    # Check Top, Bottom, Left, Right for VISITED cells
        if r > 0 and grid[r-1][c].visited: neighbors.append(grid[r-1][c])
        if r < rows - 1 and grid[r+1][c].visited: neighbors.append(grid[r+1][c])
        if c > 0 and grid[r][c-1].visited: neighbors.append(grid[r][c-1])
        if c < cols - 1 and grid[r][c+1].visited: neighbors.append(grid[r][c+1])
    
        return neighbors

    def get_all_neighbors(cell,grid):
        neighbors = []
        rows = len(grid)
        cols = len(grid[0])

        r,c = cell.row,cell.col

        if r>0 : neighbors.append(grid[r-1][c] )
        if r< rows-1 : neighbors.append(grid[r+1][c])
        if c>0 : neighbors.append(grid[r][c-1])
        if c< cols-1 : neighbors.append(grid[r][c+1])

        return neighbors

    def empty_grid(grid):
        rows = len(grid)
        cols = len(grid[0])

        for r in range(rows):
            for c in range(cols):

                #if cell to the bottom of the grid knock it down
                if r > 0:
                    grid[r][c].walls['top'] = False
                    grid[r-1][c].walls['bottom'] = False
                # If there is a cell to the left, knock down our left wall and their right wall
                if c > 0:
                    grid[r][c].walls['left'] = False
                    grid[r][c-1].walls['right'] = False
            #as the loop never goes to the external side and only knocks down left side or top side of the current cell
            #the right side and bottom side of the grid's walls still remain and aren't knocked down
