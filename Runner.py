#!/usr/bin/env python3

GRID_H = 4
GRID_W = 4
GRID_A = 16

# A simple object that only stores the content of the grid
class Grid(object):

    # Keep a 16-tuple of the grid's contents
    contents = None

    # Make sure there's the correct size of data
    def __init__(self, contents):
        global GRID_A
        assert(len(contents) == GRID_A)
        self.contents = tuple(contents)

    # 'Equal" is the same grid contents
    def __eq__(self, other):
        return isinstance(other, Grid) and (self.contents == other.contents)

    # Print the grid contents row by row
    def __str__(self):
        global GRID_A, GRID_W
        return "\n".join("".join("{0: <3}".format(c) for c in self.contents[i:i+GRID_W]).strip() for i in range(0, GRID_A, GRID_W))

if __name__ == "__main__":
    pass
