from os import walk


path = "./Data/MSiA 431/02_hw"
filenames = next(walk(path), (None, None, []))[2]  # [] if no file

print(filenames)