import pandas as pd
import os
from time import strftime, localtime

pd.set_option('display.max_rows', None)

def main():
    data = {
        "Module Name": [],
        "Version": [],
        "Hash Value": [],
        "Username": [],
        "euid": [],
        "egid": [],
        "Date": [],
        "Time": [],
        "Unix Time": []
    }
    
    module_directory = os.path.abspath("parse_moduleUsage/moduleUsage")
    
    for filename in os.listdir(module_directory):
        filepath = os.path.join(module_directory, filename)
        if os.path.isfile(filepath):
            process_file(filepath, data)

    df = pd.DataFrame(data)
    print(df)

def process_file(filepath, data):
    with open(filepath) as infile:
        for line in infile:
            key_info = extract_info(line)
            if key_info:
                data["Username"].append(key_info['username'])
                data["euid"].append(key_info['euid'])
                data["egid"].append(key_info['egid'])
                data["Module Name"].append(key_info['module_name'])
                data["Version"].append(key_info['version'])
                data["Hash Value"].append(key_info['hash'])
                unix_time = key_info['unix_time']
                data["Unix Time"].append(unix_time)
                data["Date"].append(strftime('%m-%d-%Y', localtime(float(unix_time))))
                data["Time"].append(strftime('%H:%M:%S', localtime(float(unix_time))))

def extract_info(line):
    try:
        key_info = line[line.index("username"):].split()
        return {
            "username": get_value(key_info[0]),
            "euid": get_value(key_info[1]),
            "egid": get_value(key_info[2]),
            "module_name": get_module_name(key_info[3]),
            "version": get_version(key_info[3]),
            "hash": get_hash(key_info[3]),
            "unix_time": get_value(key_info[6]).strip()
        }
    except (IndexError, ValueError) as e:
        print(f"Error processing line: {line}. Error: {e}")
        return None

def get_value(field):
    return field.split("=")[1]

def get_module_name(module_field):
    return module_field.split("=")[1].split("/")[0]

def get_version(module_field):
    parts = module_field.split("=")[1].split("/")
    return parts[1] if len(parts) > 1 else None

def get_hash(module_field):
    parts = module_field.split("=")[1].split("/")
    return parts[2] if len(parts) > 2 and len(parts[2]) == 7 else None


