import json
import os

def JsonConfiguration(file_path):
    if(os.path.exists(file_path) and os.path.isfile(file_path)):
        with open(file_path, "r") as f:
            params = json.loads(f.read())
            return params
    else:
        print("Error: Invalid Configuration Path.")
        return None