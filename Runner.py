#!/usr/bin/env python3

from collections import deque
from random import shuffle, choice

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

# Create a copy of the grid that represents the objective state for the puzzle
GRID_OBJ = Grid([i for i in range(1, GRID_A)] + [0])

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

    # Determine if the grid of a given GridNode is one that already exists in the tree
    def has_visited(self, other):
        if self == other:
            return True
        elif self.parent:
            return self.parent.has_visited(other)
        else:
            return False

    # Determine if a given object is a valid child, meaning it is a GridNode and it also
    # has not been visited before
    def valid_child(self, other):
        return not self.has_visited(other) if isinstance(other, GridNode) else False

    # After a move is known to be possible, create the resultant node; The z-index is
    # translated according to where the empty tile would end up on the 1-D container
    def action_move(self, dz):
        new_zindex = self.zindex + dz
        new_contents = list(self.grid.contents)
        new_contents[self.zindex], new_contents[new_zindex] = new_contents[new_zindex], new_contents[self.zindex]
        return GridNode(self, new_contents, new_zindex)

    # Return the GridNode that would be generated as a result of moving the empty tile
    # up, None if the empty tile is already in the top row and can't be moved up
    def move_up(self):
        global GRID_W
        return None if self.zindex < GRID_W else self.action_move(-GRID_W)

    # Return the GridNode that would be generated as a result of moving the empty tile
    # down, None if the empty tile is already in the bottom row and can't be moved down
    def move_down(self):
        global GRID_A, GRID_W
        return None if self.zindex >= GRID_A - GRID_W else self.action_move(GRID_W)

    # Return the GridNode that would be generated as a result of moving the empty tile
    # left, None if the empty tile is already in the left column and can't be moved left
    def move_left(self):
        global GRID_W
        return None if self.zindex % GRID_W == 0 else self.action_move(-1)

    # Return the GridNode that would be generated as a result of moving the empty tile
    # right, None if the empty tile is already in the left column and can't be moved right
    def move_right(self):
        global GRID_W
        return None if self.zindex % GRID_W == (GRID_W - 1) else self.action_move(1)

    # Return a 4-tuple of the moves attempted in each direction
    def all_moves(self):
        return self.move_up(), self.move_down(), self.move_left(), self.move_right()

    # Perform breadth first search on a root node
    def bfs(self):
        global GRID_OBJ

        # Create the queue of child nodes to visit
        nodes = deque()
        nodes_visited = 0

        # Start at the root node, search until the objective grid has not been found
        curr_node = self
        final_node = None
        while curr_node and not final_node:
            nodes_visited = nodes_visited + 1
            if curr_node.grid == GRID_OBJ:
                # This node has the objective state, exit the loop
                final_node = curr_node
            else:
                # Get the results of the four types of moves
                for potential_child in curr_node.all_moves():
                    # Determine if each move was valid
                    if curr_node.valid_child(potential_child):
                        # Move was valid, add it to the queue of nodes to visit (push it right)
                        nodes.append(potential_child)

            # We're done with this node, get the next in the queue (pop it left)
            curr_node = nodes.popleft()

        # Eventually, the objective grid is found
        return final_node, nodes_visited

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

    # Get a randomly shuffled initial grid
    @staticmethod
    def get_rand_root_inst():
        global GRID_A
        grid_contents = list(range(GRID_A))
        shuffle(grid_contents)
        return GridNode.get_root_inst_with(grid_contents)

    # Get a pseudo-random grid, in the sense that a grid's contents are given, and the a
    # specified number of moves are given to move away from that randomly. The idea is that
    # an 'up' move is the inverse of a 'down' move and vice versa, and the same thing for a
    # 'left' and 'right' move. This is a random set of moves, so while the solution is
    # guaranteed to not take more than the specified number of moves, it's possible that a
    # solution that takes less moves exists.
    @staticmethod
    def get_pseudo_rand_root_inst(grid_contents, num_rand_moves):
        # Get the initial node and start to loop N times
        node = GridNode.get_root_inst_with(grid_contents)
        for i in range(num_rand_moves):
            # Get all of the possible moves (speed it up by Pythonicly rejecting None values)
            possible_moves = list(n for n in node.all_moves() if n)
            # Find a random parent (this is an 'inverse', so the potential moves are nodes
            # that actually describe the parent to this current node)
            parent_node = None
            while not parent_node:
                if len(possible_moves) == 0:
                    # This should never happen
                    return None
                # Select a random element from the list
                potential_parent = choice(possible_moves)
                if node.valid_child(potential_parent):
                    # Got a valid parent, continue the loop
                    parent_node = potential_parent
                else:
                    # Not a valid move, don't try to visit this node again
                    possible_moves.remove(potential_parent)
            node = parent_node

        # Make this a 'root' node by setting this node to not have a parent
        node.parent = None
        return node

if __name__ == "__main__":
    test_nodes = [
        GridNode.get_root_inst_with([1,2,3,4,5,6,0,8,9,10,7,12,13,14,11,15]),
        GridNode.get_root_inst_with([1,0,3,4,5,2,7,8,9,6,10,11,13,14,15,12]),
        GridNode.get_root_inst_with([0,2,3,4,1,5,7,8,9,6,11,12,13,10,14,15]),
        GridNode.get_root_inst_with([5,1,2,3,0,6,7,4,9,10,11,8,13,14,15,12]),
        GridNode.get_root_inst_with([1,6,2,3,9,5,7,4,0,10,11,8,13,14,15,12])
    ]
    tree, states_visited = GridNode.get_pseudo_rand_root_inst(GRID_OBJ.contents, 10).bfs()
    tree_str, tree_depth = tree.pprint()
    print("Visited {0} states. Replaying {1} move(s) from start to finish:\n\n{2}\n".format(states_visited, tree_depth - 1, tree_str))
