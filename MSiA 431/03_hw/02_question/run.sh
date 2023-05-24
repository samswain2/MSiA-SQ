#!/bin/bash

spark-submit --master yarn --deploy-mode client swain_part1_02_question.py
spark-submit --master yarn --deploy-mode client swain_part2_02_question.py
spark-submit --master yarn --deploy-mode client swain_part3_02_question.py
