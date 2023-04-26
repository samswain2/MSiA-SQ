import yaml
import json

#reading yaml configuration file
with open("../MSIA-SQ/MSiA 423/02_lectures/05_week/samples/config_sample.yaml", "r") as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    print("Read successful")
    print("All data", data)
    print("Name", data['name'])    
    print("University", data['univ'])
    print("Team members", data['teammates'])      


#writing yaml configuration file
json_string='{"course": {"name": "Cloud Engineering"}, "modules": {"Week1": "Introduction", "Week2": "Architecture"}}'
print("JSON string :", json_string)
python_dict=json.loads(json_string)

with open('config_sample2.yaml', 'w') as file:
        yaml.dump(python_dict,file)