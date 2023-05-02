#!/usr/bin/env python
  
from operator import itemgetter
import sys

current_key = None
output = None

# read the entire line from STDIN
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()
    # splitting the data on the basis of tab we have provided in mapper.py
    key, value = line.split('\t', 1)
    
    #do any additional operations, if the value is comma separated, etc.
  
    # this IF-switch only works because Hadoop sorts map output
    # by key (here: word) before it is passed to the reducer
    if current_key == key:
        # do operations on the values for each key
        output = value
    else:
        #not entirely necessary, but prevents null keys from printing and causing error
        if current_key:
            # write result to STDOUT
            print(f"{current_key}, {output}")
        #This is the first operation for each key
        current_key = key
        output = value
  
# do not forget to output the last word if needed!
    if current_key == key:
        #this will print with a comma separated file and a space for readability
        #you can use any output format as long as it is human and machine-readable
        # csv, tsv, or whatever
        #unless a format for the output is exactly specific  by the problem
        print(f"{current_key}, {output}")
