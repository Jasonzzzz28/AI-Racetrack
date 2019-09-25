#!/bin/bash

###############################################################################
#
# File: run_tests.bash
# Author: Dana Nau <nau@cs.umd.edu>
# Last updated: Sept 5, 2019
#
# This bash script uses three lists -- racetrack problems, heuristic functions,
# and search strategies -- and iterates over every possible combination of
# problem, heuristic function, and search strategy. For each combination, it
# does (1) a graphic demo of the search and (2) a time test.
#
# IMPORTANT: If you try to run this file without modifying it, it won't work.
# You need to modify it to specify the python pathname, sample problems,
# heuristics, and search strategies that you want to use.
#
###############################################################################


set -f    # disable globbing, because we don't want the name a* to be expanded

###############################################################################
#
# START OF CUSTOMIZATION OPTIONS
# Below are the things you need to modify
#
###############################################################################



### IMPORTANT!!! Change this to use the pathname of YOUR python program
#
python=/Users/Nau/anaconda3/bin/python


# This line gives the rootname of the file that contains the test problems:
# Modify it if you want to use a different file.
#
prob_file=sample_probs


# Below, the first line is a list of all the problems in sample_probs.py, in roughly
# increasing order of difficulty.  Modify the second line to include just the ones
# that you want to use.
#
problems=(rect20 rect20a rect20b rect20c rect20d rect50 wall8a wall8b lhook16 rhook16a rhook16b spiral16 spiral24 pdes30 pdes30b rectwall8 rectwall16 rectwall32 rectwall32a walls32)
problems=(rect20e lhook16)


# Here's the rootname of the file that contains the heuristic functions.
# Replace it with the rootname of your heuristic function file.
#
heur_file=sample_heuristics

# The first line is a list of all the heuristic functions in sample_heuristics.py.
# Modify the second line to specify the heuristic function(s) you want to use.
#
heuristics=(h_edist h_esdist h_walldist)
heuristics=(h_walldist)


# The first line is a list of all the available search strategies.
# Modify the second line to give a list of the ones you want to use.
#
strategies=(bf df uc gbf a*)
strategies=(gbf)

# Modify the following line to specify how verbose you want fsearch.main to be.
# The options are 0, 1, 2, 3, 4.
#
verb=2

# Use draw=1 to draw the search tree, or draw=0 to draw nothing
#
draw=1

# Specify time_tests=1 to run the timing tests, or time_tests=0 to skip them
#
time_tests=0

###############################################################################
#
# END OF CUSTOMIZATION OPTIONS
#
###############################################################################


# The following code will iterate over every combination of sample problem, 
# heuristic function, and search strategy in your above lists. For each combination,
# it will first display the results graphically, and then do a time test.

# exit the loop when the user presses ^C, rather than going to the next iteration
trap "echo Exited!; exit;" SIGINT SIGTERM   

for prob in ${problems[*]}
do
  for heur in ${heuristics[*]}
  do
    for strat in ${strategies[*]}
    do
        echo ''
        echo "Running '$strat, $heur, $prob with verbose=$verb and draw=$draw"

        # strings for preliminary setup, running the program, and printing the result
        setup="import racetrack, $prob_file, $heur_file"
        run_prog="result=racetrack.main($prob_file.$prob, '$strat', $heur_file.$heur, verbose=$verb, draw=$draw, title='$strat, $heur, $prob')"
        
        # execute the strings in python
        $python -c "$setup; $run_prog"

        if [ "$time_tests" = 1 ]; then
            # Here's the code for doing a time test.
            echo ''
            echo "Time test of '$strat, $heur, $prob'"
        
            # string to do a time test (without printing or drawing anything)
            time_test="racetrack.main($prob_file.$prob, '$strat', $heur_file.$heur, verbose=0, draw=0)"

            # execute the time test
            $python -m timeit -s "$setup" "$time_test"

            # Comment-out the following lines if you don't want a pause here
            echo ""
            echo "*** Finished the time test. Type carriage return to continue:"
            read line
        fi
    done
  done
done
