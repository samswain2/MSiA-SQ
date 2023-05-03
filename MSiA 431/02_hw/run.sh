#!/bin/bash

input_path="02_hw/01_question" # in hdfs
output_path="output" # in hdfs and must not exist
python_path=$(pwd)
hadoop_lib_path="/opt/hadoop/hadoop/share/hadoop/tools/lib"

yarn jar ${hadoop_lib_path}/hadoop-streaming-2.10.1.jar \
       -files ${python_path}/mapper_gram.py,${python_path}/reducer_gram.py \
    -input ${input_path} \
    -output ${output_path} \
    -mapper mapper_gram.py \
    -reducer reducer_gram.py
