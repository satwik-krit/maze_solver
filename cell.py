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
