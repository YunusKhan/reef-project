README.md

FOLDER structure 

│   requirements.txt
│
├───main
│       constants.py
│       installer.py
│       root.py
│
└───templates
        template.html
        tracker.html


Instructions 

1. Open Linux (ubuntu) terminal

2. To install python 3 in linux terminal. Skip to 3 if already installed.

sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.8
python ––version
sudo apt update
sudo apt install python3-pip

3. Unzip project.zip

4. Navigate to project/main

5. Run command "python3 root.py" or "python root.py". 
The output if the tracker was used on the specfic date will be a html page.
If no tracker was used, a message will appear in the command window "No activities"

6. Defaults are provided in constant.py or you can enter 
	default date is yesterday, unless provided.
	default email is in constants.py
	default password is in constants.py
	default app-token is in constants.py

7. Requirements.txt contains packages used. They will be run by installer in installer.py
