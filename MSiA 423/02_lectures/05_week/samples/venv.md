# Virtual Environment

#create project folder
mkdir dl

#create a virtual environment inside the project folder
python -m venv dl/dl-venv

#activate the virtual enviornment
source dl/dl-venv/bin/activate

#install packages
python -m pip install <package-name>

#export all dependencies into a file 
python -m pip freeze > requirements.txt

#deactivate virtual environment
deactivate
