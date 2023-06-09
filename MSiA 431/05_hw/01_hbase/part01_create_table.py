import email
import starbase
import os

if __name__ == "__main__":
    # Set up the connection
    c = starbase.Connection(port=20550)

    # Create a table
    table_name = 'emails'
    t = c.table(table_name)

    # Create column families
    if not t.exists():
        t.create('info', 'content')

    # Path to data directory
    mypath = '/home/public/enron/'

    # Iterate through the folders in the directory
    for folder in os.listdir(mypath):
        # Name of individual (employee name)
        name = folder

        # Iterate through the files in the folder
        for file in os.listdir(os.path.join(mypath, folder)):
            key = folder + "/" + file

            # Read in email
            with open(os.path.join(mypath, folder, file), 'r') as f:
                read_data = f.read()

            try:
                # Parse email
                msg = email.message_from_string(read_data)

                # Extract fields
                sender_email = msg.get('From')
                date = msg.get('Date')
                to_field = msg.get('To')
                body_field = msg.get_payload()

                # Insert data into HBase
                t.insert(key, {
                    'info': {
                        'name': name,
                        'sender_email': sender_email if sender_email else '',
                        'date': date if date else '',
                        'to': to_field.replace('\n', '').replace('\t', '') if to_field else ''
                    },
                    'content': {
                        'body': body_field if body_field else ''
                    }
                })
            except Exception as e:
                print(f'Error processing file {key}: {e}')
                pass
