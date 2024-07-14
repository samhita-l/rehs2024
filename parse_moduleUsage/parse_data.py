import pandas as pd
import os
from time import strftime, localtime
import argparse
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', None)

def parse_user_input():
    """ Read input variables and parse command-line arguments """

    parser = argparse.ArgumentParser(
        description='Take in user queries for moduleUsage logs.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('-s', '--save', action="store_true", help='Save dataframe to file')
    parser.add_argument('-t', '--filetype', type=str, default='csv', nargs='+', choices=['csv', 'parquet'], help='File type to save dataframe')

    parser.add_argument('-m', '--unique_modules', action="store_true", help='Determine number of unique modules and how many times each one appears')
    parser.add_argument('-pltm', '--plot_modules', action="store_true", help='Plot bar graph of unique modules')
    parser.add_argument('-u', '--unique_users', action="store_true", help='Determine number of unique users and how many times each one appears')
    parser.add_argument('-pltu', '--plot_users', action="store_true", help='Plot bar graph of unique users')

    args = parser.parse_args()
    return args

def build_dataframe():
    module = []
    hash = []
    username = []
    euid = []
    egid = []
    date = []
    time = []
    unix_time = []

    module_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'moduleUsage'))
    for filename in os.listdir(module_directory):
        with open(os.path.join(module_directory, filename)) as infile:
            for line in infile:
                key_info = line[line.index("username"):].split(" ")

                username.append(extract(key_info[0], "username"))
                euid.append(extract(key_info[1], "euid"))
                egid.append(extract(key_info[2], "egid"))
                module.append(extract(key_info[3], "module"))
                hash.append(extract(key_info[3], "hash"))

                unix = extract(key_info[6], "unix").strip()
                unix_time.append(unix)
                date.append(strftime('%m-%d-%Y', localtime(float(unix))))
                time.append(strftime('%H:%M:%S', localtime(float(unix))))

    data = {
        "Module": module,
        "Hash Value": hash,
        "Username": username,
        "euid": euid,
        "egid": egid,
        "Date": date,
        "Time": time,
        "Unix Time": unix_time
    }

    df = pd.DataFrame(data)
    return df


def extract(line, info):
    text = line.split("=")
    temp = text[1]
    name = temp.split("/")

    if (info == "username" or info == "euid" or info == "egid" or info == "unix"):
        return text[1]
    
    if (info == "module"):
        if (len(name) < 2):
            return name[0]
        else:
            return name[0] + "/" + name[1]
        
    if (info == "hash"):
        if (len(name) < 3):
            return None
        else:
            if (len(name[2]) != 7):
                return None
            else: 
                return name[2]


def save_dataframe(df, args):
    if ('csv' in args.filetype):
        df.to_csv('moduleUsage.csv')
    if ('parquet' in args.filetype):
        df.to_parquet('moduleUsage.parquet')

def plot_data(data, series):
    plt.bar(range(5), series[:5], align='center', alpha=0.8)
    plt.xlabel(data)
    plt.ylabel('Frequency')
    plt.title('Top 5 ' + data)
    plt.xticks(range(5), series.index[:5])  # Set x-axis labels to match index values
    plt.show()

def print_data(data, series):
    print(series)
    print("\nThere are " + str(len(series)) + " unique " + data + "s. The complete list is shown above, ranked by how frequently each " + data + " appears.\n")
    print("The most frequent " + data + " is " + series.idxmax() + " with " + str(series.max()) + " occurrences.\n")


def main():
    args = parse_user_input()
    df = build_dataframe()

    if (args.save):
        save_dataframe(df, args)
    elif (args.unique_modules):
        unique_modules = df['Module'].value_counts()
        if (args.plot_modules):
            plot_data('Modules', unique_modules)
        else:
            print_data('module', unique_modules)
    elif (args.unique_users):
        unique_users = df['Username'].value_counts()
        if (args.plot_users):
            plot_data('Users', unique_users)
        else:
            print_data('user', unique_users)
    else:
        print(df)

    
if __name__ == "__main__":
    main()