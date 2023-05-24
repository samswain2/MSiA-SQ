#!/bin/bash

spark-submit --master yarn --deploy-mode client part1.py
spark-submit --master yarn --deploy-mode client part2.py
spark-submit --master yarn --deploy-mode client part3.py
