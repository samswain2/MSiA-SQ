#!/usr/bin/env python3

import sys
import multiprocessing
from mapper_music import mapper_music
from shuffler_music import shuffler_music
from reducer_music import reducer_music
from tqdm import tqdm

def read_in_chunks(file, chunk_size):
    lines = []
    for line in file:
        lines.append(line)
        if len(lines) >= chunk_size:
            yield lines
            lines = []
    if lines:  # Yield any remaining lines
        yield lines

if __name__ == '__main__':
    # Define the number of map processes and reduce processes
    num_mappers = 1
    num_reducers = 1
    chunk_size = 2500000  # Modify this value based on your system's memory capacity

    # Read input data from a file
    
    # Full music file
    # input = r"D:\Big Data\MSiA 431\02_hw\dataMusic10000.csv" # Runs in about 17 minutes

    # Sample music file
    # input = r"C:\Users\nuke2\Desktop\NW Work\Spring Work\MSiA-SQ\Data\MSiA 431\02_hw\music_sample.csv" # Runs instantly

    # Laptop
    input = r"C:\Users\Sam\Desktop\NW Work\Spring Work\MSiA-SQ\Data\MSiA 431\02_hw\dataMusic10000.csv"

    with open(input, 'r', encoding='utf-8') as input_file:
        # Create a pool of processes for the mappers
        with multiprocessing.Pool(num_mappers) as pool:
            all_lines = []
            for lines in tqdm(read_in_chunks(input_file, chunk_size)):
                # Apply the mapper function to each chunk
                map_results = pool.map(mapper_music, [lines])
                all_lines.extend([line for chunk in map_results for line in chunk])

    # Apply shuffler_music to the mapper output
    sorted_lines = shuffler_music(all_lines)

    # Split the sorted lines into 5 equal-sized chunks for reducers
    def create_reducer_chunks(sorted_lines, num_reducers):
        reducer_chunks = []
        chunk = []
        current_artist = None

        for artist, duration in sorted_lines:
            if current_artist is None:
                current_artist = artist

            if artist != current_artist and len(reducer_chunks) < num_reducers - 1:
                reducer_chunks.append(chunk)
                chunk = []
                current_artist = artist

            chunk.append((artist, duration))

        if chunk:
            reducer_chunks.append(chunk)

        return reducer_chunks

    reducer_chunks = create_reducer_chunks(sorted_lines, num_reducers)

    # Create a pool of processes for the reducers
    with multiprocessing.Pool(num_reducers) as pool:
        # Apply the reducer function to each chunk
        reduce_results = list(tqdm(pool.imap(reducer_music, reducer_chunks), total=num_reducers))

    # Concatenate the reducer results
    final_results = [result for chunk in reduce_results for result in chunk]

    # Sort the final results based on the artist name (key)
    final_results.sort(key=lambda x: x[0])

    # Apply reducer_music to the sorted final results to remove duplicates and keep the max duration
    final_results = reducer_music(final_results)

    # Print the final results
    for artist, max_duration in final_results:
        print(f"{artist},{max_duration}")
