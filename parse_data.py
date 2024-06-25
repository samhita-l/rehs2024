import pandas as pd
import os
from time import strftime, localtime

pd.set_option('display.max_rows', None)

def main() :
    module_name = []
    version = []
    username = []
    euid = []
    egid = []
    date = []
    time = []
    unix_time = []

    with open(os.path.abspath("moduleUsage.log-20240531")) as infile:
        for line in infile:
            key_info = line[line.index("username"):].split(" ")
            # print(key_info)

            username.append(extract(key_info[0]))
            euid.append(extract(key_info[1]))
            egid.append(extract(key_info[2]))
            module_name.append(extract_module(key_info[3]))
            version.append(extract_version(key_info[3]))

            unix = extract(key_info[6]).strip()
            unix_time.append(unix)
            date.append(strftime('%m-%d-%Y', localtime(float(unix))))
            time.append(strftime('%H:%M:%S', localtime(float(unix))))

    data = {
        "Version": version,
        "Username": username,
        "euid": euid,
        "egid": egid,
        "Date": date,
        "Time": time,
        "Unix time": unix_time
    }
    
    df = pd.DataFrame(data, index=module_name)
    print(df)


def extract(data):
    text = data.split("=")
    return text[1]

def extract_module(data):
    text = data.split("=")
    temp = text[1]
    name = temp.split("/")
    return name[0]

def extract_version(data):
    text = data.split("=")
    temp = text[1]
    name = temp.split("/")
    if (len(name) == 2):
        return name[1]
    else:
        return "None"

if __name__ == "__main__":
    main()