import pandas as pd
import os
from time import strftime, localtime
import argparse
import matplotlib.pyplot as plt
import hashlib

pd.set_option('display.max_rows', None)

def parse_user_input():
    """ Read input variables and parse command-line arguments """

    parser = argparse.ArgumentParser(
        description='Take in user queries for moduleUsage logs.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('-s', '--save', action="store_true", help='Save dataframe to file')
    parser.add_argument('-ftype', '--filetype', type=str, default='csv', nargs='+', choices=['csv', 'parquet'], help='File type to save dataframe')

    parser.add_argument('-mod', '--unique_modules', action="store_true", help='Determine number of unique modules and how many times each one appears')
    parser.add_argument('-pltm', '--plot_modules', action="store_true", help='Plot bar graph of unique modules')
    parser.add_argument('-user', '--unique_users', action="store_true", help='Determine number of unique users and how many times each one appears')
    parser.add_argument('-pltu', '--plot_users', action="store_true", help='Plot bar graph of unique users')
    parser.add_argument('-t', '--top', type=int, default=5, help='Number of top modules or users to display')
    parser.add_argument('--hash', action="store_true", help='Use SHA-256 hash value to determine unique modules')

    args = parser.parse_args()
    return args

def build_dataframe():
    module = []
    version = []
    hash = []
    username = []
    path = []
    euid = []
    egid = []
    date = []
    time = []
    unix_time = []

    module_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'moduleTest'))
    for filename in os.listdir(module_directory):
        with open(os.path.join(module_directory, filename)) as infile:
            for line in infile:
                key_info = line[line.index("username"):].split(" ")

                username.append(extract(key_info[0], "username"))
                euid.append(extract(key_info[1], "euid"))
                egid.append(extract(key_info[2], "egid"))
                module.append(extract(key_info[3], "module"))
                version.append(extract(key_info[3], "version"))
                hash.append(extract(key_info[3], "hash"))
                path.append(extract(key_info[4], "path"))

                unix = extract(key_info[6], "unix").strip()
                unix_time.append(unix)
                date.append(strftime('%m-%d-%Y', localtime(float(unix))))
                time.append(strftime('%H:%M:%S', localtime(float(unix))))

    data = {
        "Module": module,
        "Version": version,
        "Hash Value": hash,
        "Path": path,
        "Username": username,
        "euid": euid,
        "egid": egid,
        "Date": date,
        "Time": time,
        "Unix Time": unix_time,
    }

    df = pd.DataFrame(data)
    return df


def extract(line, info):
    text = line.split("=")
    temp = text[1]
    name = temp.split("/")

    if (info == "username" or info == "euid" or info == "egid" or info == "unix" or info == "path"):
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


def save_dataframe(df, args):
    if ('csv' in args.filetype):
        df.to_csv('moduleUsage.csv')
    if ('parquet' in args.filetype):
        df.to_parquet('moduleUsage.parquet')


def plot_data(args, data_type, series):
    plt.bar(range(args.top), series[:args.top], align='center', alpha=0.8)
    plt.xlabel(data_type)
    plt.ylabel('Frequency')
    plt.title('Top ' + str(args.top) + ' ' + data_type)
    plt.xticks(range(args.top), series.index[:args.top])
    plt.show()


def print_data(data_type, series):
    print(series)
    print("\nThere are " + str(len(series)) + " unique " + data_type + "s. The complete list is shown above, ranked by how many times each " + data_type + " appears.\n")
    print("The most frequent " + data_type + " is " + series.idxmax() + " with " + str(series.max()) + " occurrences.\n")


def generate_hash(path):
    hash_object = hashlib.sha256()
    hash_object.update(path.encode())
    file_hash = hash_object.hexdigest()
        
    return file_hash


def main():
    args = parse_user_input()
    df = build_dataframe()

    if args.save:
        save_dataframe(df, args)
    elif args.unique_modules:
        df['Complete Modules'] = df['Module'] + '/' + df['Version']
        df['SHA-256'] = df['Path'].apply(generate_hash)
        df['Complete Modules'] += '  -->  ' + df['SHA-256']
        unique_modules = df['Complete Modules'].value_counts()
        
        cpu_gpu_counts = df['Path'].apply(lambda x: 'CPU' if 'cpu' in x else 'GPU' if 'gpu' in x else 'Other').value_counts()

    if args.plot_modules:
        plot_data(args, 'Modules', unique_modules)
        plot_data(args, 'CPU/GPU', cpu_gpu_counts)
    else:
            print_data('module', unique_modules)
            print_data('CPU/GPU', cpu_gpu_counts)
elif args.unique_users:
    unique_users = df['Username'].value_counts()
    if args.plot_users:
            plot_data(args, 'Users', unique_users)
    else:
            print_data('user', unique_users)
    else:
        print(df)


    instance_modules = set(df['Module'].unique())
        user_modules = df.groupby('Username')['Module'].apply(set)
        users_never_use_instance = {
            user: len(instance_modules - modules) for user, modules in user_modules.items()
        }
        never_used_instances = {user: count for user, count in users_never_use_instance.items() if count > 0}
        print("Users who never use one of the Spack instance modules:" + str{len(never_used_instances)}")
        print(never_used_instances)

    else:
        print(df)

if __name__ == "__main__":
    main()