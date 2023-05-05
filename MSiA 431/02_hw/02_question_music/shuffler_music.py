#!/usr/bin/env python3

import sys

def shuffler_music(lines):
    # Remove leading and trailing whitespaces, and split by comma
    processed_lines = [(artist.strip(), str(duration).strip()) for artist, duration in lines]

    # Sort the lines based on the artist name (key)
    processed_lines.sort(key=lambda x: x[0])

    # Return the sorted lines
    return processed_lines
