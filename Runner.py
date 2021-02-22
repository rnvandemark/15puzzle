#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import deque
from random import shuffle, choice
from os import mkdir
from os.path import join as ojoin
from time import time, gmtime, strftime

OUTPUT_DIR = "output"
OUTPUT_PREFIX = "output"

GRID_H = None
GRID_W = None
GRID_A = None
GRID_OBJ = None

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

# Create the grid constants given the desired width and height above two
def set_grid_consts(h, w):
    global GRID_H, GRID_W, GRID_A, GRID_OBJ
    assert((h > 2) and (w > 2))
    # Accept the width and height of the puzzle, then calculate its area
    GRID_H = h
    GRID_W = w
    GRID_A = GRID_H * GRID_W
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
        return isinstance(other, GridNode) and (self.__key() == other.__key())

    def __hash__(self):
        return hash(self.grid.contents)

    # Just stringify the grid
    def __str__(self):
        return str(self.grid)

    def __key(self):
        return hash(self)

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
    def bfs(self, verbose=False):
        global GRID_OBJ

        # Create the queue of child nodes to visit
        nodes = deque()

        # Start at the root node, search until the objective grid has not been found
        curr_node = self
        all_nodes = set()
        all_nodes.add(curr_node)
        final_node = None
        while curr_node and not final_node:
            all_nodes.add(curr_node)
            if curr_node.grid == GRID_OBJ:
                # This node has the objective state, exit the loop
                final_node = curr_node
            else:
                # Get the results of the four types of moves
                for potential_child in curr_node.all_moves():
                    # Determine if each move was valid
                    if GridNode.valid_child(potential_child, all_nodes):
                        # Move was valid, add it to the queue of nodes to visit (push it right)
                        nodes.append(potential_child)

            # We're done with this node, get the next in the queue (pop it left)
            curr_node = nodes.popleft()

        # Eventually, the objective grid is found
        # If being verbose, return the set of grid states, else just return the length of the set
        return final_node, all_nodes if verbose else len(all_nodes)

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

    # Determine if a given object is a valid child, meaning it is a GridNode and it also
    # has not been visited before
    @staticmethod
    def valid_child(new_node, all_nodes):
        return new_node not in all_nodes if isinstance(new_node, GridNode) else False

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
            all_nodes = set()
            parent_node = None
            while not parent_node:
                if len(possible_moves) == 0:
                    # This should never happen
                    return None
                # Select a random element from the list
                potential_parent = choice(possible_moves)
                if GridNode.valid_child(potential_parent, all_nodes):
                    # Got a valid parent, continue the loop
                    parent_node = potential_parent
                else:
                    # Not a valid move, don't try to visit this node again
                    possible_moves.remove(potential_parent)
            node = parent_node
            all_nodes.add(node)

        # Make this a 'root' node by setting this node to not have a parent
        node.parent = None
        return node

if __name__ == "__main__":
    parser = ArgumentParser(description="""
        Run a X-Puzzle. By default, this runs a random 4x4 puzzle (see the
        -r / --random option, if no options are provided then this is the
        default). The five test cases can be ran if specified (see the -t /
        --do-tests option).
    """)
    parser.add_argument(
        "-r",
        "--random",
        metavar="MxNxD",
        type=str,
        default="4x4x15",
        help="""
            HEIGHTxWIDTHxMOVES, where HEIGHT and WIDTH are the height and width
            of the puzzle, and MOVES is the number of moves used to generate the
            pseudo-random puzzle. A pseudo-random puzzle means that the objective
            grid is copied and then MOVES number of actions are performed on the
            grid to have a "random" grid with a complexity to solve is known (at
            least, the max complexity is). The default value is '4x4x15'. The
            values for M and N must be greater than two.
        """
    )
    parser.add_argument(
        "-p",
        "--populate",
        metavar="MxNxv11,v21...vN1,v12,v22,...vNM",
        type=str,
        help="""
            HEIGHTxWIDTHxCONTENTS, where HEIGHT and WIDTH are the height and width
            of the puzzle, and CONTENTS is a comma-separated list of the grid, row
            by row. The values must be unique and, if sorted, sequential from 0 to
            one less than the grid's area.
        """
    )
    parser.add_argument(
        "-t",
        "--do-tests",
        action="store_true",
        help="Run the five 4x4 test cases."
    )
    args = parser.parse_args()

    try:
        mkdir(OUTPUT_DIR)
    except FileExistsError:
        pass

    test_nodes = None; pseudo_node_inverses = None
    if args.do_tests:
        set_grid_consts(4, 4)
        test_nodes = [
            GridNode.get_root_inst_with([1,2,3,4,5,6,0,8,9,10,7,12,13,14,11,15]),
            GridNode.get_root_inst_with([1,0,3,4,5,2,7,8,9,6,10,11,13,14,15,12]),
            GridNode.get_root_inst_with([0,2,3,4,1,5,7,8,9,6,11,12,13,10,14,15]),
            GridNode.get_root_inst_with([5,1,2,3,0,6,7,4,9,10,11,8,13,14,15,12]),
            GridNode.get_root_inst_with([1,6,2,3,9,5,7,4,0,10,11,8,13,14,15,12])
        ]
    elif args.populate:
        h_str, w_str, grid_contents_str = args.populate.split("x")
        set_grid_consts(int(h_str), int(w_str))
        grid_contents = [int(c) for c in grid_contents_str.split(",")]
        contents_set = sorted(list(set(grid_contents)))
        assert((len(contents_set) == GRID_A) and (contents_set[0] == 0) and (contents_set[-1] == (GRID_A - 1)))
        test_nodes = [GridNode.get_root_inst_with(grid_contents)]
    else:
        h, w, pseudo_node_inverses = (int(s) for s in args.random.split("x"))
        set_grid_consts(h, w)
        test_nodes = [GridNode.get_pseudo_rand_root_inst(GRID_OBJ.contents, pseudo_node_inverses)]

    for i, test_node in enumerate(test_nodes):
        output_filename = ojoin(OUTPUT_DIR, "{0}{1}.txt".format(OUTPUT_PREFIX, i))
        with open(output_filename, "w") as output_file:
            start_time = time()
            final_node, states_visited = test_node.bfs()
            finish_time = time()
            tree_str, tree_depth = final_node.pprint()
            formatted_time = strftime("%H:%M:%S", gmtime(finish_time - start_time))
            output_file.write("Visited {0} states. Replaying {1} move(s) from start to finish:\n\n{2}\n".format(
                states_visited,
                tree_depth - 1,
                tree_str
            ))
        print("Finished ({0}). See '{1}'.".format(formatted_time, output_filename))
