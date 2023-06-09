# Email Analysis with HBase

This repository contains scripts and files for loading email data into HBase, querying the data, and storing the results. The goal is to analyze emails based on various attributes such as sender, date, and content.

## Files Description

- `create_table.py`: This is a Python script that is used to create an HBase table, and load it with email data. The script reads email data from a specified directory, extracts required fields (name of the employee, sender's email address, date of the email, recipients, and the email body), and inserts the data into the HBase table.

- `query.sh`: This is a Bash script containing HBase shell commands to query the data that is loaded into HBase through `create_table.py`. It performs three tasks:
    1. Returns the bodies of all emails for a user of your choice (as a single text file `result01.txt`).
    2. Returns the bodies of all emails written during a particular month of your choice (as a single text file `result02.txt`).
    3. Returns the bodies of all emails of a given user during a particular month, both of your choice (as a single text file `result03.txt`).

- `result01.txt`: This text file contains the bodies of all emails for a specific user, as extracted by the `query.sh` script.

- `result02.txt`: This text file contains the bodies of all emails sent during a specific month, as extracted by the `query.sh` script.

- `result03.txt`: This text file contains the bodies of all emails of a specific user sent during a specific month, as extracted by the `query.sh` script.

## How to Run

1. Make sure HBase is installed and running on your system.

2. Run the `create_table.py` script to create the HBase table and load it with email data. Use the command `python create_table.py`.

3. Make the `query.sh` script executable by running `chmod +x query.sh`.

4. Run the `query.sh` script to perform the queries on the data in HBase and save the results to text files. Use the command `./query.sh`.

5. The results of the queries can be found in `result01.txt`, `result02.txt`, and `result03.txt`.
