#!/usr/bin/env bash

# Task 1: Return the bodies of all emails for a user of your choice (as a single text file).
echo "scan 'emails', {COLUMNS => ['info:name', 'content:body'], FILTER => \"SingleColumnValueFilter('info', 'name', =, 'binary:allen-p')\"}" | hbase shell > result01.txt

# Task 2: Return the bodies of all emails written during a particular month (February 2002) (as a single text file).
echo "scan 'emails', {COLUMNS => ['info:date', 'content:body'], FILTER => \"SingleColumnValueFilter('info', 'date', =, 'substring:Feb 2002')\"}" | hbase shell > result02.txt

# Task 3: Return the bodies of all emails of a given user (allen-p) during a particular month (February 2002) (as a single text file).
echo "scan 'emails', {COLUMNS => ['info:name', 'info:date', 'content:body'], FILTER => \"SingleColumnValueFilter('info', 'name', =, 'binary:allen-p') AND SingleColumnValueFilter('info', 'date', =, 'substring:Feb 2002')\"}" | hbase shell > result03.txt

# Disable and drop table
echo "disable 'emails'"
echo "drop 'emails'"
exit