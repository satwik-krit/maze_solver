import random

#DFS maze generator
def dfs_generator(grid):
    stack = [grid[0][0]]
    grid[0][0].visited = True
    
    while stack:
        current = stack[-1]
        neighbors = get_unvisited_neighbors(current,grid)
        if neighbors:
            next_cell = random.choice(neighbors)
            remove_walls(current, next_cell)
            next_cell.visited = True
            stack.append(next_cell)
        else:
            stack.pop()

#Binary Tree
def gen_binarytree(grid):
    for row in grid:
        for cell in grid:
            options = []
            if cell.row>0: options.append('top')
            if cell.col>0: options.append('left')

            if options:
                option = random.choice(options)
                if option == 'left':
                    remove_wall(cell, grid[cell.row][cell.col-1])
                else:
                    rmeove_wall(cell, grid[cell.row-1][cell.col])

#Wilson algorithm generator           
def gen_wilsons(grid):
    unvisited = []
    for row in grid:
        for cell in row:
            unvisited.append(cell)
    
    #starting cell

    start = random.choice(unvisited)
    start.visited = True
    unvisited.remove(start)

    while unvisited:
        path_start = random.choice(unvisited)
        current = path_start

        path = {}

        while not current.visited:  #the random walk which temporarily updates the path, path over here is dynamically shifted depending on visited or not visited
            neighbors = get_all_neighbors(current,grid)
            next_cell = random.choice(neighbors)

            path[current] = next_cell

            current = next_cell

        current = path_start

        while current in path: #the construction phase of the loop where the path is actually updated when the random walk is over with the changed coords of each cell
            next_cell = path[current]
            remove_walls(current,next_cell)
            current.visited = True

            unvisited.remove(current)
            current = next_cell

#recursive division one

import random

def divide(grid, r, c, h, w):
    #If the room is 1 cell wide or 1 cell tall, we can't divide it anymore. (exit condition)
    if w <= 1 or h <= 1:
        return

    # Determine orientation: Horizontal or Vertical?
    if w > h:
        orientation = 'vertical'
    elif h > w:
        orientation = 'horizontal'
    else:
        # If it's a perfect square, pick randomly
        orientation = random.choice(['horizontal', 'vertical'])

    if orientation == 'vertical':
        #Pick where to draw the wall (a random column index)
        # We draw the wall to the RIGHT of wall_col
        wall_col = random.randint(c, c + w - 2)
        
        #Pick where to put the door (a random row index along the new wall)
        door_row = random.randint(r, r + h - 1)
        
        #Build the wall
        for i in range(r, r + h):
            if i != door_row: # Don't build a wall where the door is
                grid[i][wall_col].walls['right'] = True
                grid[i][wall_col + 1].walls['left'] = True
                
        # Split the left room and the right room
        # Left Room
        divide(grid, r, c, h, (wall_col - c + 1))
        # Right Room
        divide(grid, r, wall_col + 1, h, w - (wall_col - c + 1))

    else: 
        #Pick where to draw the wall (a random row index)
        # We draw the wall BELOW wall_row
        wall_row = random.randint(r, r + h - 2)
        
        #Pick where to put the door (a random col index along the new wall)
        door_col = random.randint(c, c + w - 1)
        
        #Build the wall
        for j in range(c, c + w):
            if j != door_col: # Don't build a wall where the door is
                grid[wall_row][j].walls['bottom'] = True
                grid[wall_row + 1][j].walls['top'] = True
                
       #Split the top room and the bottom room
        # Top Room
        divide(grid, r, c, (wall_row - r + 1), w)
        # Bottom Room
        divide(grid, wall_row + 1, c, h - (wall_row - r + 1), w)

import random

def generate_maze_hunt_and_kill(grid):

    current_cell = random.choice(grid)
    current_cell.visited = True

    while current_cell is not None:
        
        unvisited_neighbors = get_unvisited_neighbors(current_cell, grid)
        
        if unvisited_neighbors:
            #pick a random neighbor from neighbors of current cell
            next_cell = random.choice(unvisited_neighbors)
            
            # Knock down the walls
            remove_walls(current_cell, next_cell)
            
            # Move to the next cell
            next_cell.visited = True
            current_cell = next_cell
            
        else:
            #if all niehgbors of the cell are visited then dead end occurs and the algorithm searches for another cell in the grid with non-visited neighbors
            current_cell = None # We assume the maze is done until we find evidence otherwise
            
            # Scan the grid using nested loops
            for row in grid:
                for cell in row:
                   
                    if not cell.visited:
                       #when unvisited cell found use its neighbors and do the same loop as the upper loop but only once to find a primary path to build of
                        visited_neighbors = get_visited_neighbors(cell, grid)
                        
                        if visited_neighbors:
                            #if neighbor found 
                            # Connect it to the existing maze
                            chosen_visited = random.choice(visited_neighbors)
                            remove_walls(cell, chosen_visited)
                            
                            # Mark our new cell as visited
                            cell.visited = True
                            
                            # Make it the new starting point for the Walk phase
                            current_cell = cell
                            
                            break # Break out of the inner loop (columns)
                
                if current_cell is not None:
                    break # Break out of the outer loop (rows) to resume loop 1
                    
    # The while loop naturally terminates when the Hunt phase 
    # scans the entire grid and finds zero unvisited cells