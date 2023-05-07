#!/usr/bin/env python3

import sys
import multiprocessing
from mapper_music import mapper_music
from shuffler_music import shuffler_music
from reducer_music import reducer_music
from tqdm import tqdm
import glob
import os

def count_files(files):
    return len(files)

def read_in_files(files):
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            yield f.readlines()

def read_in_chunks(files, chunk_size):
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            lines = []
            for line in f:
                lines.append(line)
                if len(lines) >= chunk_size:
                    yield lines
                    lines = []
            if lines:
                yield lines

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

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python main_music.py <number_of_mappers> <number_of_reducers>")
        sys.exit(1)

    num_mappers = int(sys.argv[1])
    num_reducers = int(sys.argv[2])
    chunk_size = 1000000

    input_files = glob.glob(r"D:\Big Data\MSiA 431\02_hw\split_music_full\*")  # Replace with the path to the folder containing the split files

    all_lines = []
    num_files = count_files(input_files)
    with multiprocessing.Pool(num_mappers) as pool:
        with tqdm(total=len(input_files), desc="Mapping files", bar_format="{l_bar}{bar:30}{r_bar}{bar:-10b}") as progress_bar:
            for lines in read_in_chunks(input_files, chunk_size):
                map_results = pool.map(mapper_music, [lines])
                all_lines.extend([line for chunk in map_results for line in chunk])
                progress_bar.update(1)

    sorted_lines = shuffler_music(all_lines)

    reducer_chunks = create_reducer_chunks(sorted_lines, num_reducers)

    with multiprocessing.Pool(num_reducers) as pool:
        reduce_results = list(tqdm(pool.imap(reducer_music, reducer_chunks),
                                   total=num_reducers,
                                   desc="Reducing data",
                                   bar_format="{l_bar}{bar:30}{r_bar}{bar:-10b}"))

    final_results = [result for chunk in reduce_results for result in chunk]
    # With this code to write the results to a text file:
    output_file = "output.txt"  # Specify the output file name
    with open(output_file, "w", encoding="utf-8") as f:
        for artist, max_duration in final_results:
            f.write(f"{artist},{max_duration}\n")
