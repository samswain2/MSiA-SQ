#!/usr/bin/env python3

def mapper_music(lines):
    result = []

    for line in lines:
        # Remove leading and trailing whitespaces
        line = line.strip()

        fields = line.split(",")

        # Assign the artist and duration fields
        artist, duration = fields[2], float(fields[3])

        # Append artist and duration in a key-value format to the result list
        result.append((artist, duration))

    return result
