#!/usr/bin/env python

import sys
import re

# Define the substrings to search for
substrings = ['nu', 'chi', 'haw']

# Read the entire line from STDIN
for line in sys.stdin:
    # Remove leading and trailing whitespace
    line = line.strip().lower()
    
    # Split the line into fields
    fields = re.split(r'\s+', line)

    # Check if it's a unigram or bigram line
    if len(fields) >= 4:
        word = fields[0]
        year = fields[1]
        num_volumes = fields[3]
    elif len(fields) >= 5:
        word = ' '.join(fields[0:2])
        year = fields[2]
        num_volumes = fields[4]
    else:
        continue

    # Check if the year is a valid number
    try:
        int(year)
    except ValueError:
        continue

    # Check if each substring appears in the word, and emit the substring, year, and num_volumes
    for substring in substrings:
        count = word.count(substring)
        if count > 0:
            print(f"{year},{substring},{count * int(num_volumes)}")
