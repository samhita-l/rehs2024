import pandas as pd
import os
from time import strftime, localtime
import argparse
import matplotlib.pyplot as plt
import hashlib
import datetime as datetime

pd.set_option('display.max_rows', None)

def parse_user_input():
    """ Read input variables and parse command-line arguments """

    parser = argparse.ArgumentParser(
        description='Take in user queries for moduleUsage logs.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('-s', '--save', action="store_true", help='Save dataframe to file')
    parser.add_argument('-ftype', '--filetype', type=str, default='csv', nargs='+', choices=['csv', 'parquet'], help='File type to save dataframe')
    parser.add_argument('-rcsv', '--csv_path', type=str, help='Path of .csv file, read in to create a dataframe')
    parser.add_argument('-rparquet', '--parquet_path', type=str, help='Path of .parquet file, read in to create a dataframe')

    parser.add_argument('-mod', '--unique_modules', action="store_true", help='Determine number of unique modules and how many times each one appears')
    parser.add_argument('--spack', action="store_true", help='Search for Spack instance modules')
    parser.add_argument('--spack_root', type=str, help='Search for modules with specific Spack root path')
    parser.add_argument('--hash', action="store_true", help='Use MD5 hash value to determine unique modules')

    parser.add_argument('-users', '--unique_users', action="store_true", help='Determine number of unique users and how many times each one appears')
    
    parser.add_argument('-plt', '--plot', action="store_true", help='Plot bar graph of unique modules/users')
    parser.add_argument('-t', '--top', type=int, default=5, help='Number of top modules or users to display')
    parser.add_argument('-all', '--include_all', action="store_true", help='Include all values in pie chart')
    parser.add_argument('-f', '--find', type=str, help='Find specific module or user')

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
                if line.count("username") != 1 or line.count("gpu/0.17.3a") > 0 or line.count("cpu/0.17.3a") > 0:
                    continue

                key_info = line[line.index("username"):].split(" ")

                if args.spack_root and not check_spack_root(args.spack_root, key_info[4]):
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


def check_spack_root(spack_root, path):
    """Check if the path matches the specified Spack root."""
    root_paths = {
        "cpu/0.17.3b": "/cm/shared/apps/spack/0.17.3/cpu/b",
        "gpu/0.17.3b": "/cm/shared/apps/spack/0.17.3/gpu/b",
        "cpu/0.15.4": "/cm/shared/apps/spack/cpu",
        "gpu/0.15.4": "/cm/shared/apps/spack/gpu"
    }
    return root_paths.get(spack_root) in path


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


def plot_data(args, data_type, df, series):
    # Determine the title based on user input
    if args.spack:
        plot_title = 'Breakdown of Spack Instance Modules'
    elif args.find is not None:
        plot_title = f"Breakdown of {args.find} Modules in moduleUsage Logs"
    elif args.spack_root is not None:
        plot_title = f"Breakdown of Modules Associated with {args.spack_root} in moduleUsage Logs"
    else:
        plot_title = f"Breakdown of Top {args.top} {data_type} in moduleUsage Logs"

    top_modules = series.index

    df['Date'] = pd.to_datetime(df['Date'])
    filtered_df = df[df['Modules'].isin(top_modules)]
    start_date = filtered_df['Date'].min().strftime("%m-%d-%Y")
    end_date = filtered_df['Date'].max().strftime("%m-%d-%Y")

    plot_title += f"\n\nFrom {start_date} to {end_date}"    


    # Sort the filtered series by values and select the top 'args.top' items
    top_series = series.sort_values(ascending=False).head(args.top)

    if args.include_all:
        # Aggregate "Other" category for items not included in top_series
        other_series = series[~series.index.isin(top_series.index)]
        if not other_series.empty:
            other_series = pd.Series({'Other': other_series.sum()})
            # Concatenate top_series with the "Other" category
            top_series = pd.concat([top_series, other_series])

        start_date = df['Date'].min()
        end_date = df['Date'].max()
        total_occurrences = series.sum()
    else:
        total_occurrences = top_series.sum()

    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plot the pie chart
    wedges, texts, autotexts = ax.pie(
        top_series,
        labels=top_series.index,    # Use index as labels
        autopct='%1.1f%%',          # Show percentages with one decimal place
        startangle=90               # Start angle at 90 degrees (top of the pie)
    )

    # Set the plot title
    ax.set_title(plot_title)

    # Add a new axis on the left side of the pie chart for the data table
    table_ax = fig.add_axes([0.05, 0.1, 0.2, 0.8])  # Adjust the position and size as needed

    # Create the table data
    table_data = pd.DataFrame({
        data_type: top_series.index.tolist(),
        'Occurrences': top_series.values,
        'Percentage': [f'{pct:.1f}%' for pct in top_series / total_occurrences * 100]
    })
    
    # Add totals row
    total_percentage = 100.0
    table_data.loc[len(table_data)] = ['Total', total_occurrences, f'{total_percentage:.1f}%']

    # Add the table to the axis
    table = table_ax.table(
        cellText=table_data.values,
        colLabels=table_data.columns,
        cellLoc='center',
        loc='center'
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)  # Scale the table if needed

    # Hide the table axis
    table_ax.axis('off')

    # Adjust legend position to the right side
    ax.legend(loc='center left', bbox_to_anchor=(1.1, 0.8))

    # Clear default ylabel
    ax.set_ylabel('')

    # Show the plot
    plt.show(block=True)


def output_data(args, data_type, series):
    print()
    print(series)

    if (args.find is None):
        if (args.spack_root is not None):
            print("\nThere are " + str(len(series)) + " unique " + data_type + "s associated with the Spack instance " + args.spack_root + ". The complete list is shown above, ranked by how many times each " + data_type + " appears.\n")
            print("The most frequent " + data_type + " is " + series.idxmax() + " with " + str(series.max()) + " occurrences.\n")
        elif (args.spack):
            print("\nThe Spack instance modules are listed above. The most frequent one is " + series.idxmax() + ", with " + str(series.max()) + " occurrences.\n")
        else:
            print("\nThere are " + str(len(series)) + " unique " + data_type + "s. The complete list is shown above, ranked by how many times each " + data_type + " appears.\n")
            print("The most frequent " + data_type + " is " + series.idxmax() + ", with " + str(series.max()) + " occurrences.\n")
    else:
        try:
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
    if (args.csv_path is not None):
        df = pd.read_csv(args.csv_path)
    elif (args.parquet_path is not None):
        df = pd.read_parquet(args.parquet_path, engine='pyarrow')
    else:
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
            plot_data(args, 'Modules', df, unique_modules)
        else:
            output_data(args, 'module', unique_modules)

    elif (args.unique_users):
        unique_users = df['Username'].value_counts()
        if (args.plot):
            plot_data(args, 'Users', df, unique_users)
        else:
            output_data(args, 'user', unique_users)

    else:
        print(df)

    
if __name__ == "__main__":
    main()