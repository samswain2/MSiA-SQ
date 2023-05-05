#!/usr/bin/env python3

import sys

# Define the substrings to search for
substrings = ['nu', 'chi', 'haw']

# Function to check if year is valid
def is_valid_year(year):
    return year.isdigit()

# Read lines from STDIN
for line in sys.stdin:
    # Remove leading and trailing whitespace and convert to lowercase
    line = line.strip().lower()

    # Split the line into fields
    fields = line.split()

    # Check if there are at least four fields
    if len(fields) < 4:
        continue

    # Assign the last three items in fields to year, occurrences, and volumes
    year, occurrences, volumes = fields[-3:]

    # Check if year is valid
    if not is_valid_year(year):
        continue

    # Clean up volumes data points
    volumes = volumes.replace('"', '')

    word_list = fields[:-3]

    # Iterate through the list of words and check for each word if it contains a substring
    for word in word_list:
        # Create a dictionary for substring presence in the current word
        substring_presence = {substring: 1 if substring in word else 0 for substring in substrings}

        # Print results for substrings found in the current word
        for substring, present in substring_presence.items():
            if present:
                print(f"{year},{substring},{present * int(volumes)}")
