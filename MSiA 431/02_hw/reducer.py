#!/usr/bin/env python3

import sys

current_year = None
current_substring = None
current_volumes = 0
current_count = 0

# Read the entire line from STDIN
for line in sys.stdin:
    # Remove leading and trailing whitespace
    line = line.strip()

    # Split the line into fields
    year, substring, volumes = line.split(',')

    # Convert volumes to int
    try:
        volumes = int(volumes)
    except ValueError:
        continue

    # If the current year and substring match, accumulate the volumes
    if current_year == year and current_substring == substring:
        current_volumes += volumes
        current_count += 1
    else:
        if current_year and current_substring:
            average_volumes = current_volumes / current_count
            print(f"{current_year},{current_substring},{average_volumes}")
        current_year = year
        current_substring = substring
        current_volumes = volumes
        current_count = 1

# Output the last year and substring if needed
if current_year and current_substring:
    average_volumes = current_volumes / current_count
    print(f"{current_year},{current_substring},{average_volumes}")
