#!/bin/bash

spark-submit --master yarn --deploy-mode client swain_02_p1_script.py
spark-submit --master yarn --deploy-mode client swain_02_p2_script.py
spark-submit --master yarn --deploy-mode client swain_02_p3_script.py
