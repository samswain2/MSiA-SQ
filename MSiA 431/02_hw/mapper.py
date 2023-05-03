#!/usr/bin/env python3

import sys

# Define the substrings to search for
substrings = ['nu', 'chi', 'haw']

# Read the entire line from STDIN
for line in sys.stdin:

    # Remove leading and trailing whitespace and convert to lowercase
    line = line.strip().lower()

    # Split the line into fields
    fields = line.split()

    # Assign the last three items in fields to year, occurrences, and volumes
    if len(fields) >= 4:
        year, occurrences, volumes = fields[-3:]
        word_list = fields[:-3]
    else:
        continue

    # Clean up volumes data points
    volumes = volumes.replace('"', '')

    # Iterate through the list of words and check for each word if it contains a substring
    for word in word_list:
        counts = {substring: 1 if substring in word else 0 for substring in substrings}
        
        # Print mapped strings
        for substring in counts:
            print(f"{year},{substring},{counts[substring]}")


        
