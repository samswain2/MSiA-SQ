#!/usr/bin/env python3

import sys
import multiprocessing
from mapper_music import mapper_music
from shuffler_music import shuffler_music
from reducer_music import reducer_music

if __name__ == '__main__':
    # Define the number of map processes and reduce processes
    num_mappers = 20
    num_reducers = 5

    # Read input data from a file
    input = "C:/Users/nuke2/Desktop/NW Work/Spring Work/MSiA-SQ/Data/MSiA 431/02_hw/music_sample.csv"
    with open(input, 'r', encoding='utf-8') as input_file:
        lines = input_file.readlines()

    # Split the input file into 20 smaller chunks
    chunks = [lines[i::num_mappers] for i in range(num_mappers)]

    # Create a pool of processes for the mappers
    with multiprocessing.Pool(num_mappers) as pool:
        # Apply the mapper function to each chunk
        map_results = pool.map(mapper_music, chunks)

    # Concatenate the mapper results
    all_lines = [line for chunk in map_results for line in chunk]

    # Apply shuffle_and_sort to the mapper output
    sorted_lines = shuffler_music(all_lines)

    # Split the sorted lines into 5 equal-sized chunks for reducers
    chunk_size = len(sorted_lines) // num_reducers
    reducer_chunks = [sorted_lines[i:i + chunk_size] for i in range(0, len(sorted_lines), chunk_size)]

    # Create a pool of processes for the reducers
    with multiprocessing.Pool(num_reducers) as pool:
        # Apply the reducer function to each chunk
        reduce_results = pool.map(reducer_music, reducer_chunks)

    # Concatenate the reducer results and print them
    final_results = [result for chunk in reduce_results for result in chunk]
    for artist, max_duration in final_results:
        print(f"{artist},{max_duration}")
