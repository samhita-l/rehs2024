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
    parser.add_argument('--spack', action="store_true", help='Search for Spack instance modules')
    parser.add_argument('--spack_root', action="store_true", help='Search for software modules on different Spack instances')
    parser.add_argument('--hash', action="store_true", help='Use MD5 hash value to determine unique modules')

    parser.add_argument('-users', '--unique_users', action="store_true", help='Determine number of unique users and how many times each one appears')
    
    parser.add_argument('-plt', '--plot', action="store_true", help='Plot bar graph of unique modules/users')
    parser.add_argument('-f', '--find', type=str, help='Find specific module or user')
    parser.add_argument('-t', '--top', type=int, default=5, help='Number of top modules or users to display')
    


    args = parser.parse_args()
    return args

def build_dataframe(args):
    module = []
    version = []
    hash_list = []
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
                if line.count("username") != 1 or line.count("gpu/0.17.3a") > 0:
                    continue

                key_info = line[line.index("username"):].split(" ")

                if (args.spack_root):
                    roots = ['cm/shared/apps/spack/0.17.3/cpu/b', '/cm/shared/apps/spack/0.17.3/gpu/b', 'cm/shared/apps/spack/cpu', '/cm/shared/apps/spack/gpu']
                    if (not any(root in key_info[4] for root in roots)):
                        continue

                username.append(extract(key_info[0], "username"))
                euid.append(extract(key_info[1], "euid"))
                egid.append(extract(key_info[2], "egid"))
                module.append(extract(key_info[3], "module"))
                version.append(extract(key_info[3], "version"))
                hash_list.append(extract(key_info[3], "hash"))
                path.append(extract(key_info[4], "path"))

                unix = extract(key_info[6], "unix").strip()
                unix_time.append(unix)
                date.append(strftime('%m-%d-%Y', localtime(float(unix))))
                time.append(strftime('%H:%M:%S', localtime(float(unix))))

    data = {
        "Name": module,
        "Version": version,
        "Hash Value": hash_list,
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
    # Determine the title based on user input
    if args.spack:
        plot_title = 'Breakdown of Spack Instance Modules'
    elif args.find is not None:
        plot_title = f"Breakdown of {args.find} Modules in moduleUsage Logs"
    else:
        plot_title = f"Breakdown of Top {args.top} {data_type} in moduleUsage Logs"

    # Sort the series by values and select the top 'args.top' items
    top_series = series.sort_values(ascending=False).head(args.top)

    # Plotting the pie chart
    pie_chart = top_series.plot.pie(
        labels=top_series.index,    # Use index as labels
        autopct='%1.1f%%',          # Show percentages with one decimal place
        startangle=90,              # Start angle at 90 degrees (top of the pie)
        title=plot_title,
        label='',                   # No need for extra labels
    )

    # Adjust legend position
    pie_chart.legend(loc='center left', bbox_to_anchor=(-0.2, 0.5))

    # Add labels and percentage to each slice
    pie_chart.set_ylabel('')        # Clear default ylabel
    plt.show(block=True)


def print_data(args, data_type, series):
    if (args.find is None):
        print(series)
        print("\nThere are " + str(len(series)) + " unique " + data_type + "s. The complete list is shown above, ranked by how many times each " + data_type + " appears.\n")
        print("The most frequent " + data_type + " is " + series.idxmax() + " with " + str(series.max()) + " occurrences.\n")
    else:
        try:
            print()
            print(series)
            print("\nThis " + data_type + " appears " + str(series[args.find]) + " times.\n")
        except KeyError:
            print("\nNo " + data_type + " exactly matches the inputted keyword.\n")


def generate_hash(path):
    hash_object = hashlib.md5()
    hash_object.update(path.encode())
    file_hash = hash_object.hexdigest()
        
    return file_hash


def main():
    args = parse_user_input()
    df = build_dataframe(args)

    if (args.save):
        save_dataframe(df, args)

    elif (args.unique_modules):
        df['Modules'] = df['Name'] + '/' + df['Version']
        
        if (args.hash):
            df['MD5'] = df['Path'].apply(generate_hash)
            df['Modules'] += '  -->  ' + df['MD5']
        else:
            df.loc[df['Hash Value'].notnull(), 'Modules'] += '/' + df['Hash Value']

        unique_modules = df['Modules'].value_counts() 
        if (args.spack):
            unique_modules = unique_modules[unique_modules.index.str.contains('cpu|gpu')]
        if (args.find is not None):
            unique_modules = unique_modules[unique_modules.index.str.contains(args.find)]

        if (args.plot):
            plot_data(args, 'Modules', unique_modules)
        else:
            print_data(args, 'module', unique_modules)

    elif (args.unique_users):
        unique_users = df['Username'].value_counts()
        if (args.plot):
            plot_data(args, 'Users', unique_users)
        else:
            print_data(args, 'user', unique_users)

    else:
        print(df)

    
if __name__ == "__main__":
    main()