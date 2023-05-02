#!/usr/bin/env python
  
# import sys because we need to read and write data to STDIN and STDOUT
import sys
import re
import random

# reading entire line from STDIN (standard input)
for line in sys.stdin:
    line = line.strip()
    # to remove leading and trailing whitespace
    # split the line into words
      
    # we are looping over the words array and printing the word
    # with the count of 1 to the STDOUT
    if random.uniform(0,1) < .5:
        # write the results to STDOUT (standard output);
        # what we output here will be the input for the
        # Reduce step, i.e. the input for reducer.py
        print(f"{line}")
