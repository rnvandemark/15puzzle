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

# An object that represents one state of a Grid that lives in a tree of states
class GridNode(object):

    # The parent to this instance in a tree
    parent = None

    # The Grid object
    grid = None

    # The index (0 to GRID_AREA-1) of the zero/empty tile in grid
    zindex = None

    # Constructor, given all members
    def __init__(self, parent, grid_contents, zindex):
        self.parent = parent
        self.grid = Grid(grid_contents)
        self.zindex = zindex

    # 'Equal' is only if the grid is equal
    def __eq__(self, other):
        return isinstance(other, GridNode) and (self.grid == other.grid)

    # Just stringify the grid
    def __str__(self):
        return str(self.grid)

    # Pretty print, including tracking depth of the tree to be parsable
    def pprint(self, depth=1):
        s = str(self)
        if self.parent:
            s = self.parent.pprint(depth=depth+1) + "\n\n" + s
        else:
            s = str(depth) + ":" + s

        if depth == 1:
            tree_depth_str, tree_str = s.split(":")
            return tree_str, int(tree_depth_str)
        else:
            return s

    # Create a root GridNode given the grid cell contents
    @staticmethod
    def get_root_inst_with(contents):
        return GridNode(None, contents, contents.index(0))

if __name__ == "__main__":
    test_nodes = [
        GridNode.get_root_inst_with([1,2,3,4,5,6,0,8,9,10,7,12,13,14,11,15]),
        GridNode.get_root_inst_with([1,0,3,4,5,2,7,8,9,6,10,11,13,14,15,12]),
        GridNode.get_root_inst_with([0,2,3,4,1,5,7,8,9,6,11,12,13,10,14,15]),
        GridNode.get_root_inst_with([5,1,2,3,0,6,7,4,9,10,11,8,13,14,15,12]),
        GridNode.get_root_inst_with([1,6,2,3,9,5,7,4,0,10,11,8,13,14,15,12])
    ]
