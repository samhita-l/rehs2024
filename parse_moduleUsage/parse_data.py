import pandas as pd
import os
import io
from time import strftime, localtime
from IPython.display import display, HTML

pd.set_option('display.max_rows', None)

def main() :
    module_name = []
    version = []
    hash = []
    username = []
    euid = []
    egid = []
    date = []
    time = []
    unix_time = []

    module_directory = os.path.abspath("moduleUsage")
    for filename in os.listdir(module_directory):
        with open(os.path.join(module_directory, filename)) as infile:
            for line in infile:
                key_info = line[line.index("username"):].split(" ")

                username.append(extract(key_info[0], "username"))
                euid.append(extract(key_info[1], "euid"))
                egid.append(extract(key_info[2], "egid"))
                module_name.append(extract(key_info[3], "module"))
                version.append(extract(key_info[3], "version"))
                hash.append(extract(key_info[3], "hash"))

                unix = extract(key_info[6], "unix").strip()
                unix_time.append(unix)
                date.append(strftime('%m-%d-%Y', localtime(float(unix))))
                time.append(strftime('%H:%M:%S', localtime(float(unix))))

    data = {
        "Version": version,
        "Hash Value": hash,
        "Username": username,
        "euid": euid,
        "egid": egid,
        "Date": date,
        "Time": time,
        "Unix Time": unix_time
    }
    
    df = pd.DataFrame(data, index=module_name)
    print(df)

def extract(line, info):
    text = line.split("=")
    temp = text[1]
    name = temp.split("/")

    if (info == "username" or info == "euid" or info == "egid" or info == "unix"):
        return text[1]
    
    if (info == "module"):
        return name[0] 
    
    if (info == "version"):
        if (len(name) < 2):
            return None
        else:
            return name[1]
        
    if (info == "hash"):
        if (len(name) < 3):
            return None
        else:
            if (len(name[2]) != 7):
                return None
            else: 
                return name[2]
    
    
if __name__ == "__main__":
    main()