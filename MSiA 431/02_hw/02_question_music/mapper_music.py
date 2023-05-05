#!/usr/bin/env python3

import sys
import csv

def mapper_music(lines):
    result = []
    insufficient_fields_count = 0
    error_count = 0

    for line in lines:
        # Remove leading and trailing whitespaces
        line = line.strip()

        # Use the csv.reader to handle the commas correctly
        reader = csv.reader([line])
        fields = next(reader)

        # Check if the line has the expected number of fields
        if len(fields) < 4:
            insufficient_fields_count += 1
            continue

        try:
            # Assign the artist and duration fields
            artist, duration = fields[2], float(fields[3])

            # Append artist and duration in a key-value format to the result list
            result.append((artist, duration))
        except Exception as e:
            error_count += 1

    if insufficient_fields_count > 0:
        print(f"Skipped {insufficient_fields_count} lines due to insufficient fields.", file=sys.stderr)
    
    if error_count > 0:
        print(f"Skipped {error_count} lines due to errors.", file=sys.stderr)

    return result
