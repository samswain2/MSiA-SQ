#!/usr/bin/env python3

import sys

def reducer_music(lines):
    current_artist = None
    current_max_duration = 0.0
    result = []

    for line in lines:
        # Extract artist and duration from line
        artist, duration = line

        # Convert duration to float
        duration = float(duration)

        if artist == current_artist:
            current_max_duration = max(current_max_duration, duration)
        else:
            if current_artist:
                result.append((current_artist, current_max_duration))

            current_artist = artist
            current_max_duration = duration

    if current_artist:
        result.append((current_artist, current_max_duration))

    return result
