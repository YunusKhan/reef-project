import os
from pathlib import Path
from subprocess import call

def installer():
    file_path = Path(__file__).resolve().parent.parent.joinpath('requirements.txt')
    with open(file_path) as my_file:
        package_list = " ".join([each.strip().split("==")[0] for each in my_file.readlines()])
        my_cmd = "python3.7 -m pip install " + package_list
        os.system(my_cmd)