import email
import starbase
import os

if __name__ == "__main__":
    # set up connection
    c = starbase.Connection(port=20550)

    t = c.table('tlewis') #YOUR TABLE MUST BE NAMED SOMETHING UNIQUE, TABLES ARE SHARED

    #example fields
    t.create('to', 'body')

    mypath = '/home/public/enron/'
    for folder in os.listdir(mypath):
        for file in os.listdir(mypath + folder):
            key = folder + "/" + file
            # read in email
            with open(mypath + key, 'r') as f:
                read_data = f.read()
            
            try:
                b = email.message_from_string(read_data)
                to_field = b['to'].replace('\n', '').replace('\t', '')
                #get fields necessary for homework
                body_field = b.get_payload()

                t.insert(key,
                        {
                        'to': {'to': to_field},
                        'body':{'body': body_field}
                        }
                    )
            except:
                pass