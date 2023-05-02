#!/usr/bin/env python
  
# import sys because we need to read and write data to STDIN and STDOUT
import sys
#other python-native imports
  
# reading entire line from STDIN (standard input)
for line in sys.stdin:
    # to remove leading and trailing whitespace
    line = line.strip()

    #Operations
    key = line
    value = 1
        
    print(f"{key}\t{value}")
