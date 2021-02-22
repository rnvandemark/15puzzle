# 15puzzle

Use the main (and only) script to solve an X-puzzle. This is referred to an
X-puzzle because while the grid has fifteen tiles by default, it can be ran to
be any puzzle with MxN-1 tiles.

The script is marked as a Python3 executable, so just navigate to the directory
where this file is and run it as such:

./Runner.py

See the help menu for the possible options by running either of these two commands:

./Runner.py -h

./Runner.py --help

By default, each generated output text file will replay the path of success from
initial state to final state with the summary message stating how many states were
visited. If the -v / --verbose option is given anytime the program is ran, each
output file will also dump ALL of the states visited to the file.

As a short summary, some common uses cases are:

1.) The default runtime configuration (running a pseudo-random 4x4 puzzle):

./Runner.py

(See the help menu as to what makes it pseudo-random.)

2.) Running the five test cases as given for the assignment:

./Runner.py -t

./Runner.py --do-tests

3.) Run a pseudo-random 4x7 puzzle initialized from 16 inverse movements:

./Runner.py -r 4x7x16

4.) Run a 3x4 puzzle with the initial grid set to be [[2,0,3,4],[1,5,7,8],[9,6,10,11]]:

./Runner.py -p 3x4x2,0,3,4,1,5,7,8,9,6,10,11

Again, the -v option can be given to any of those above examples.
